# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the bot

```bash
# Copy and fill in credentials
cp config.json.example config.json

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

The bot token can also be provided via the `DISCORD_TOKEN` environment variable instead of `config.json`.

## Config keys (`config.json`)

| Key | Description |
|-----|-------------|
| `token` | Discord bot token |
| `botname` | Bot display name |
| `ClientID` | Discord application client ID |
| `language` | Locale code (`en` or `fr`) |
| `default_emote` | Fallback emoji name |
| `prompt` | Command prefix (default `!`) |
| `modrole_name` | Role name with mod permissions |
| `adminrole_name` | Role name with admin permissions |

## Architecture

`main.py` is the entry point. It reads config, sets the locale, registers regex-based command handlers, and starts the `DiscordBot`.

**`src/DiscordBot.py` — `DiscordBot`**: Wraps a `discord.Client` (discord.py v2+) and an `AsyncIOScheduler` (APScheduler, `Europe/Paris` timezone). Commands are registered as `(compiled_regex, coroutine)` pairs via `register_action()`. On each message, the first matching regex triggers its coroutine. The scheduler is started in `on_ready`.

**`src/cogs/core.py`**: The three command handlers:
- `bot_help_embed` — sends an embed listing available commands
- `schedule_post` — interactive wizard (mod/admin only) that collects channel ID, message content, and either a one-shot `DATE` (`YYYY.MM.DD HH:mm`) or recurring `INTERVAL` (`YYYY.MM.DD HH:mm Nx` where x is `d/h/m/s`) schedule, then adds an APScheduler job
- `language` — mod/admin only; switches bot locale at runtime

**`src/cogs/utils.py`**: Helpers for config I/O (`write_config`), locale loading (`load_language`), and custom emoji resolution/substitution (`transform_emojis_in_str`).

**`src/config_utils.py`**: Thread-safe `config.json` read/write helpers (`load_config`, `save_config`, `get_config_value`, `set_config_value`).

## Internationalisation

`.po` source files live in `src/` (`messages_en.po`, `messages_fr.po`). Compiled `.mo` files must be placed in `res/` as `messages_<locale>.mo`. Compile with:

```bash
msgfmt src/messages_en.po -o res/messages_en.mo
msgfmt src/messages_fr.po -o res/messages_fr.mo
```

The active locale is loaded at startup from `config.json` and can be changed at runtime with `<prompt>language <en|fr>` (requires mod or admin role).

## Discord permissions required

The bot needs **Read Messages**, **Send Messages**, and **Add Reactions**. **Use External Emojis** is required if the bot should resolve custom emojis from other servers it is connected to.
