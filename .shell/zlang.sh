#!/bin/sh

source /opt/config/mod/.shell/0.sh

if [ "$1" == 'en' ]; then ZLANG="en"
else if [ "$1" == 'de' ]; then ZLANG="de"
else if [ "$1" == 'ru' ]; then ZLANG="ru"
else if [ "$1" == 'fr' ]; then ZLANG="fr"
else if [ "$1" == 'es' ]; then ZLANG="es"
else if [ "$1" == 'it' ]; then ZLANG="it"
else if [ "$1" == 'zh' ]; then ZLANG="zh"
else if [ "$1" == 'ja' ]; then ZLANG="ja"
else if [ "$1" == 'ko' ]; then ZLANG="ko"
else if [ "$1" == 'pt' ]; then ZLANG="pt"
else if [ "$1" == 'cs' ]; then ZLANG="cs"
else ZLANG="en"
fi; fi; fi; fi; fi; fi; fi; fi; fi; fi; fi

# Path to the symlink that Klipper includes (e.g., .../config/lang/language.cfg)
SYM_LINK_PATH="${MOD_CONF}/mod/lang/language.cfg"
# Path to the target configuration file (e.g., .../config/lang/en.cfg)
TARGET_CONFIG_PATH="${MOD_CONF}/mod/lang/${ZLANG}.cfg"
# Check if the file exists. If the file does not exist, set the language back to 'en'.
if [ ! -f "$TARGET_CONFIG_PATH" ]; then
    echo "Warning: Configuration file for language ${ZLANG} not found (${TARGET_CONFIG_PATH}). Using default 'en'." >&2
    ZLANG="en"
    TARGET_CONFIG_PATH="${MOD_CONF}/lang/${ZLANG}.cfg"
fi

# 2. Removing the old symlink, if it exists
rm -f $SYM_LINK_PATH &>/dev/null

# 3. Creating a new symlink
# Correct format: ln -s [TARGET] [LINK]
# The link (SYM_LINK_PATH) will point to the TARGET (TARGET_CONFIG_PATH)
ln -s $TARGET_CONFIG_PATH $SYM_LINK_PATH &>/dev/null

echo "[zmod]
language: ${ZLANG}" >${MOD_CONF}/mod_data/lang.cfg
echo "Use lang: ${ZLANG}"
sync
sleep 5
sync
/opt/config/mod/.shell/zremote.sh reboot
