# Relaygram

Relaygram is a Telegram relay bot that forwards messages from multiple source channels to one destination channel.

## 🧠 Purpose

This project automatically monitors Telegram channels to:
- Forward all new messages (whether they contain files or not) to another channel

It is built with Python using the Telethon library and supports Docker deployment.
For local runs, environment variables are loaded automatically from `.env`.

## 🔐 Telegram Authentication

Before using the bot, you need to generate a **persistent Telegram session**.

### Steps:
1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Create an app to get your `API_ID` and `API_HASH`
3. On the first launch, the script will guide you to generate a `StringSession`:
    - Enter your phone number
    - Enter the code you receive by SMS or Telegram
    - Copy the generated session string
    - Paste it into the `.env` file under `SESSION_STRING`

This session will be reused automatically on each launch.

## ⚙️ Execution Modes

You can choose between two modes using the `MODE` variable in `.env`:

### 🧪 Development Mode (`dev`)
- Uses the same `.env` configuration as production
- Useful for local testing

### 🚀 Production Mode (`prod`)
- Source channels are loaded from a file set in `.env`
- The destination channel is set in `.env`
- No user interaction is needed
- Ideal for automated server deployment

## 📁 Project Structure

- `generate_session.py` : generates the StringSession
- `main.py` : main bot script
- `start.py` : entrypoint that checks for session and launches the right script
- `lang.py` : contains CLI messages
- `source_channels.txt.example` : example source channels file (one channel link per line)
- `.env` : environment configuration (not versioned)
- `.env.example` : configuration template
- `Dockerfile` : defines the Docker image
- `docker-compose.yml` : simplifies containerized execution
- `README.md` : this documentation

## ⚙️ Environment Variables (.env)

Required variables:

- `API_ID` : your Telegram app ID
- `API_HASH` : your Telegram app hash
- `SESSION_STRING` : persistent session string
- `MODE` : either `dev` or `prod`
- `SOURCE_CHANNELS_FILE` : path to file with source channels (one line = one channel link)
- `TARGET_CHANNEL_ID` : destination channel numeric ID

Example `SOURCE_CHANNELS_FILE` content:

```txt
@channel_one
https://t.me/channel_two
```

## 🐳 Useful Docker Commands

### 🔧 Build the Docker image

Run this only once, or after modifying the Dockerfile:

```bash
docker compose build
```

### ▶️ Launch in development mode

Run the bot locally with `.env` configuration:

```bash
docker compose run --rm relaygram
```

Project files are mounted into the container at `/config`, so `SOURCE_CHANNELS_FILE` can point to any file from the repo (for example `source_channels.txt` or `source_channels_flow1.txt`) without extra launch variables.

### 🚀 Automatic launch (prod mode)

Run the bot in production mode using `.env` configuration, with no user interaction:

```bash
docker compose up -d
```

## 📝 Final Notes

- Authentication happens **only once**: the Telegram session is saved.
- You must be a **member of both source and destination channels**.
- Only **new messages** are forwarded – history is not retrieved.
