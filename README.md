# SmashStats

A Discord bot that serves Super Smash Bros. Ultimate frame data and hitbox gifs
as slash commands: `/stats`, `/viz`, and `/help`.

This bot requires a file named `secret.py` in the root folder with the following content:
```
token = "PASTE_YOUR_BOT_TOKEN_HERE"
```

## Intents

The bot requests no intents at all (`discord.Intents.none()`), privileged or
otherwise. Slash commands arrive as self-contained interaction payloads, so the
bot never reads message content. Nothing needs to be enabled on the
**Bot > Privileged Gateway Intents** page of the Developer Portal.

The bot does need the `applications.commands` scope in its invite URL.

## Build

`docker build -t smashstats .`

## Run

`docker run --rm -d smashstats`

Commands are published with a global `tree.sync()` on startup, which Discord can
take up to an hour to roll out the first time.
