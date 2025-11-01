import os
import shutil
import re
import yaml
from pathlib import Path

def generate_msg_key(message, existing_keys):
    """Generate unique MSG_ key from English message text with max length 20."""
    # Sanitize and uppercase
    sanitized = re.sub(r'[^\w\s]', '', message)
    sanitized = re.sub(r'\s+', '_', sanitized.strip()).upper()
    if not sanitized:
        sanitized = "TEXT"
    prefix = "MSG_"
    max_total = 20

    def build_key(base, counter=None):
        if counter is None:
            max_body = max_total - len(prefix)
            body = (base[:max_body]).rstrip('_') or "TEXT"[:max_body]
            return f"{prefix}{body}"
        suffix = f"_{counter}"
        max_body = max_total - len(prefix) - len(suffix)
        max_body = max(1, max_body)
        body = (base[:max_body]).rstrip('_') or "TEXT"[:max_body]
        return f"{prefix}{body}{suffix}"

    base = sanitized
    key = build_key(base)
    if key in existing_keys:
        counter = 1
        while True:
            key = build_key(base, counter)
            if key not in existing_keys:
                break
            counter += 1
    return key

def extract_respond_messages(content):
    """Extract all RESPOND ... MSG="..." from content (any attribute order, TYPE/PREFIX with/bez uvozovek).
    Ignore lines starting with # (comments)."""
    # Najdi na jednom řádku vše od 'RESPOND' po 'MSG="..."' a vytáhni obsah MSG
    # Filtruj řádky začínající # (komentáře)
    results = []
    pattern = r'RESPOND[^\n]*?MSG="([^"]*)"'
    
    for match in re.finditer(pattern, content):
        # Zjisti, zda řádek začíná #
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_prefix = content[line_start:match.start()].strip()
        
        # Ignoruj, pokud řádek začíná #
        if line_prefix.startswith('#'):
            continue
        
        results.append((match.start(), match.end(), match.group(0), match.group(1)))
    
    return results

def _extract_placeholders(msg):
    """
    Return ordered list of simple placeholder names found in msg, e.g. {name}.
    Only identifiers ([A-Za-z_][A-Za-z0-9_]*) are returned; dotted names are ignored.
    """
    seen = set()
    names = []
    for raw in re.findall(r'\{([^{}]+)\}', msg):
        if re.match(r'^[A-Za-z_]\w*$', raw) and raw not in seen:
            seen.add(raw)
            names.append(raw)
    return names

def _build_zlocale_call(key, placeholders):
    """
    Build MSG replacement: MSG="{ zlocale('KEY', a=a, b=b) }"
    """
    if placeholders:
        args = ", " + ", ".join(f"{p}={p}" for p in placeholders)
    else:
        args = ""
    return f'MSG="{{ zlocale(\'{key}\'{args}) }}"'

def process_cfg_file(file_path, processed_dir, en_yml_path, log_dir, existing_keys):
    """Process single .cfg file"""
    filename = os.path.basename(file_path)
    print(f"Processing: {filename}")
    
    # Read original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Copy to processed directory
    processed_path = os.path.join(processed_dir, filename)
    shutil.copy2(file_path, processed_path)
    
    # Extract messages
    messages = extract_respond_messages(original_content)
    
    if not messages:
        print(f"  No localizable strings found in {filename}")
        return existing_keys
    
    # Prepare for replacement
    translations = {}
    changes_log = []
    modified_content = original_content
    offset = 0
    
    for start, end, full_match, message in messages:
        # Skip already localized or keyed messages
        if 'zlocale(' in message or re.search(r'\{MSG_[^}]+\}', message):
            continue

        # Generate unique key (based only on EN text) with 20-char limit
        msg_key = generate_msg_key(message, existing_keys)
        existing_keys.add(msg_key)
        
        # Store translation
        translations[msg_key] = message
        
        # Calculate line number
        line_num = original_content[:start].count('\n') + 1
        
        # Log change
        changes_log.append({
            'line': line_num,
            'key': msg_key,
            'original': message
        })
        
        # Replace in content with zlocale(...)
        placeholders = _extract_placeholders(message)
        replacement = _build_zlocale_call(msg_key, placeholders)
        adjusted_start = start + offset
        adjusted_end = end + offset
        # replace only the MSG="... part within the matched RESPOND"
        old = f'MSG="{message}"'
        new = replacement
        new_match = full_match.replace(old, new)
        modified_content = modified_content[:adjusted_start] + new_match + modified_content[adjusted_end:]
        offset += len(new_match) - len(full_match)
    
    # Write modified file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    # Update en.yml
    update_yml_file(en_yml_path, translations)
    
    # Write change log do changes/ složky
    changes_dir = os.path.join(log_dir, 'changes')
    os.makedirs(changes_dir, exist_ok=True)
    log_file = os.path.join(changes_dir, f"{os.path.splitext(filename)[0]}.txt")
    write_change_log(log_file, changes_log)
    
    print(f"  Extracted {len(translations)} strings from {filename}")
    
    return existing_keys

def update_yml_file(yml_path, translations):
    """Update or create en.yml file"""
    if os.path.exists(yml_path):
        with open(yml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    
    if 'messages' not in data:
        data['messages'] = {}
    
    data['messages'].update(translations)

    # Vlastní dumper: vždy uvozovky a bez zalomení řádků
    class QuotedDumper(yaml.SafeDumper):
        pass

    def str_representer(dumper, value):
        return dumper.represent_scalar('tag:yaml.org,2002:str', value, style='"')

    QuotedDumper.add_representer(str, str_representer)

    with open(yml_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            data,
            f,
            Dumper=QuotedDumper,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=4096,  # nezalamovat na více řádků
        )

def write_change_log(log_path, changes):
    """Write change log file"""
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Total changes: {len(changes)}\n")
        f.write("=" * 80 + "\n\n")
        for change in changes:
            f.write(f"Line: {change['line']}\n")
            f.write(f"Key: {change['key']}\n")
            f.write(f"Original: {change['original']}\n")
            f.write("-" * 80 + "\n")

def _parse_change_log(log_path):
    """Parse change log produced for EN into list of {line, key, original}."""
    entries = []
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            current = {}
            for line in f:
                if line.startswith("Line: "):
                    try:
                        current['line'] = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        current['line'] = None
                elif line.startswith("Key: "):
                    current['key'] = line.split(":", 1)[1].strip()
                elif line.startswith("Original: "):
                    current['original'] = line.split(":", 1)[1].strip()
                    if current.get('line') and current.get('key'):
                        entries.append(current)
                    current = {}
    except FileNotFoundError:
        pass
    return entries

def _extract_msg_from_line(line):
    """Extract MSG=\"...\" from a single line."""
    m = re.search(r'MSG="([^"]*)"', line)
    return m.group(1) if m else None

def find_matching_strings_in_other_langs(base_dir, en_translations):
    """Build {lang}.yml for each language (except en) by reading original cfgs at
    the same line numbers as in EN change logs. Do not modify non-EN cfg files.
    Ensure processed/ (backups) and changes/ directories exist for structure consistency."""
    lang_dirs = [d for d in os.listdir(base_dir) 
                 if os.path.isdir(os.path.join(base_dir, d)) and d != 'en']
    
    print(f"\nProcessing other languages: {', '.join(lang_dirs)}")

    en_dir = os.path.join(base_dir, 'en')
    en_changes_dir = os.path.join(en_dir, 'changes')
    if not os.path.isdir(en_changes_dir):
        print("  No EN change logs found, skipping other languages.")
        return

    en_change_logs = [f for f in os.listdir(en_changes_dir) if f.endswith('.txt')]

    # Vytvořit locale složku pro yml soubory
    locale_dir = os.path.join(base_dir, 'locale')
    os.makedirs(locale_dir, exist_ok=True)

    for lang in lang_dirs:
        lang_dir = os.path.join(base_dir, lang)
        lang_yml_path = os.path.join(locale_dir, f"{lang}.yml")

        # Ensure structure (no cfg changes will be written)
        changes_dir = os.path.join(lang_dir, 'changes')
        processed_dir = os.path.join(lang_dir, 'processed')
        os.makedirs(changes_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

        # Backup original cfgs from the language directory into processed/
        lang_cfg_files = [f for f in os.listdir(lang_dir) if f.endswith('.cfg')]
        for cfg_file in lang_cfg_files:
            src = os.path.join(lang_dir, cfg_file)
            dst = os.path.join(processed_dir, cfg_file)
            try:
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            except Exception:
                pass

        # Aggregate translations for this language using EN logs (keys + line numbers)
        lang_translations = {}
        for log_name in en_change_logs:
            base_name = os.path.splitext(log_name)[0]
            lang_cfg_path = os.path.join(lang_dir, f"{base_name}.cfg")
            if not os.path.exists(lang_cfg_path):
                continue

            entries = _parse_change_log(os.path.join(en_changes_dir, log_name))
            with open(lang_cfg_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()

            for entry in entries:
                ln = entry.get('line')
                key = entry.get('key')
                if not key or not isinstance(ln, int):
                    continue

                value = None
                if 1 <= ln <= len(lines):
                    value = _extract_msg_from_line(lines[ln - 1])

                # Fallback to EN value if not found
                if not value:
                    value = en_translations.get(key, "")

                lang_translations[key] = value

        # Update language yml with collected translations (no cfg replacements, no per-lang logs)
        if lang_translations:
            update_yml_file(lang_yml_path, lang_translations)
            print(f"  Created/updated {lang}.yml with {len(lang_translations)} keys")
        else:
            print(f"  No matching entries for {lang}, skipped yml update")

def write_localization_file(base_dir=None, en_dir=None, output_yml=None):
    """
    Entry point function for writing localization files.
    Steps:
      1) Process EN cfgs -> backup to processed/, replace MSG with { zlocale('KEY', ...) }, log to en/changes/, save to locale/en.yml
      2) For each other language, backup originals to processed/ and create/update locale/{lang}.yml
         by reading original cfgs at the same line numbers from EN change logs (no cfg modifications).
    """
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'orig'))
    if en_dir is None:
        en_dir = os.path.join(base_dir, 'en')
    
    # Vytvořit locale složku a nastavit cestu pro en.yml
    locale_dir = os.path.join(base_dir, 'locale')
    os.makedirs(locale_dir, exist_ok=True)
    
    if output_yml is None:
        output_yml = os.path.join(locale_dir, 'en.yml')

    processed_dir = os.path.join(en_dir, 'processed')
    log_dir = en_dir

    # Create directories including changes/
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(os.path.join(log_dir, 'changes'), exist_ok=True)

    # Track existing keys based on EN processing
    existing_keys = set()

    # Process all EN .cfg files
    cfg_files = [f for f in os.listdir(en_dir) if f.endswith('.cfg')]
    if not cfg_files:
        return None

    for cfg_file in cfg_files:
        file_path = os.path.join(en_dir, cfg_file)
        existing_keys = process_cfg_file(file_path, processed_dir, output_yml, log_dir, existing_keys)

    # Load all EN translations from en.yml
    all_translations = {}
    if os.path.exists(output_yml):
        with open(output_yml, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'messages' in data:
                all_translations = data['messages']

    # Build language yml files (no modifications to non-EN cfgs)
    find_matching_strings_in_other_langs(base_dir, all_translations)

    return output_yml

def main():
    # Configuration
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'orig'))
    en_dir = os.path.join(base_dir, 'en')
    processed_dir = os.path.join(en_dir, 'processed')
    
    # Locale složka pro yml soubory
    locale_dir = os.path.join(base_dir, 'locale')
    en_yml_path = os.path.join(locale_dir, 'en.yml')
    
    log_dir = en_dir
    
    # Create directories
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(locale_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    print(f"Working directory: {en_dir}")
    print(f"Processed directory: {processed_dir}")
    print(f"Locale directory: {locale_dir}")
    print(f"Output yml: {en_yml_path}")
    print("=" * 80)
    
    # Track existing keys to avoid duplicates
    existing_keys = set()
    
    # Process all .cfg files
    cfg_files = [f for f in os.listdir(en_dir) if f.endswith('.cfg')]
    
    if not cfg_files:
        print(f"No .cfg files found in {en_dir}")
        return
    
    all_translations = {}
    
    for cfg_file in cfg_files:
        file_path = os.path.join(en_dir, cfg_file)
        existing_keys = process_cfg_file(file_path, processed_dir, en_yml_path, log_dir, existing_keys)
    
    print("=" * 80)
    print(f"Processing complete. Total unique keys: {len(existing_keys)}")
    
    # Load all translations from en.yml
    if os.path.exists(en_yml_path):
        with open(en_yml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'messages' in data:
                all_translations = data['messages']
    
    # Find matching strings in other languages
    find_matching_strings_in_other_langs(base_dir, all_translations)
    
    print("\nDone!")

if __name__ == "__main__":
    main()