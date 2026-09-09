# Security

- Keep `TELEGRAM_BOT_TOKEN` and `LLM_API_KEY` outside source control.
- Treat LLM output as untrusted data; validate it before rendering or storing it.
- Do not send unnecessary personal information to an LLM provider.
- Escape user-controlled text before using Telegram HTML formatting.
- Add rate limits, abuse monitoring, encrypted backups and a deletion workflow before production use.
- Rotate any credential that has ever appeared in a commit or log.

This public edition contains no original user database, messages, logs or production credentials.

