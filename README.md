# Message Manager — Mini Project

A Flask dashboard that fetches Telegram conversations using Telethon, displays message history, sends replies, periodically refreshes the inbox, and applies transparent local keyword rules to order conversations. A separate Gemini AI demo analyzes synthetic sample messages.

## Why real Telegram messages are not sent to Gemini in this build

Telegram's published API/content-licensing terms prohibit using platform-derived data for AI/ML deployment except where an applicable exception has been granted. The AI page therefore sends only synthetic sample messages; the real inbox uses local rule-based priorities. See:
- https://core.telegram.org/api/terms
- https://telegram.org/tos/content-licensing

## Setup (Windows PowerShell)

1. Open this folder in VS Code.
2. Create/activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your own Telegram API credentials and Gemini key. Never share `.env` or session files.
5. If you already have a working `telegram_session.session`, place it in this project folder. Otherwise run `python telegram_client.py` once and complete Telegram authentication in the terminal.
6. Run:

   ```powershell
   python app.py
   ```

7. Open http://127.0.0.1:5000. Gemini sample demo: http://127.0.0.1:5000/ai-demo.

## Features

- Telegram chat list and latest messages
- Message-history view
- Send replies to the selected Telegram chat
- 15-second page refresh (paused while composing a reply)
- Local keyword priority labels/scores for live chats
- Gemini priority/score/category/reason/reply draft for built-in synthetic samples

## Notes

- The `.session` file is sensitive: it allows access to your logged-in Telegram account. Keep it private and out of Git.
- The local keyword scores are fixed rules (HIGH=90, MEDIUM=70/60, LOW=30), not AI scores.
- The Gemini demo requires a valid key and availability of the configured Gemini model in your account.
