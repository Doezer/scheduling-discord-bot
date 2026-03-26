---
name: compile-translations
description: Compile all .po translation files to .mo binaries in res/
disable-model-invocation: true
---

msgfmt src/messages_en.po -o res/messages_en.mo
msgfmt src/messages_fr.po -o res/messages_fr.mo
echo "Done. Restart the bot to pick up new translations."