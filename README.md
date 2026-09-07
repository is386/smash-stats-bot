# SmashStats

This is a Discord bot written in Python that serves Super Smash Bros. Ultimate frame data and hitbox gifs.
The data comes from [Ultimate Frame Data](https://ultimateframedata.com/smash) and is stored in SQLite
databases. Everything is a slash command, so there is nothing to remember about prefixes. It is used by over
10,000 users across the Smashcords.

## Features

### Frame Data

`/stats <character> <move>` sends an embed with the frame data for a move: startup, total frames, landing
lag, shield lag, and whatever else that move has.

### Hitboxes

`/viz <character> <move>` sends the hitbox gif for a move. Every result has a button to flip between the
stats and the gif, so you do not have to run the other command yourself.

### Autocomplete

Both fields autocomplete. Start typing a character and pick from the list, and the move list fills in once a
character is chosen. Moves can be searched by their name (`neutral air`) or their short code (`nair1`).
Character names also go through a synonyms database, so nicknames and abbreviations work.

### Move Picker

Some moves have several versions, like multi hit moves and moves with different hitboxes. When that happens
the bot sends a dropdown to pick from instead of guessing. Only the moves that actually have the data you
asked for show up in the dropdown, so you cannot pick an option that errors out.

### Help

`/help` sends the command list and an explanation of every error message the bot can send. It is ephemeral,
so it does not clutter the channel.

Note: Only the user who ran the command can use its buttons and dropdowns. Everyone else gets a private
message telling them it is not theirs. The components also grey themselves out after they time out.

## Intents

The bot requests no intents at all (`discord.Intents.none()`), privileged or otherwise. Slash commands
arrive as self contained interaction payloads, so the bot never reads message content. Nothing needs to be
enabled on the **Bot > Privileged Gateway Intents** page of the Developer Portal.

The bot does need the `applications.commands` scope in its invite URL.

## Setup

This bot requires a file named `secret.py` in the root folder with the following content:

```
token = "PASTE_YOUR_BOT_TOKEN_HERE"
```

## Dependencies

- `python 3.11`

### Python Dependencies

- `discord.py`
- `pytest`

To use the `requirements.txt` file, just run `pip3 install -r requirements.txt`.

## Tests

From the root folder, run `python -m pytest`.

## Build

`docker build -t smashstats .`

## Run

`docker run --rm -d smashstats`

Note: Commands are published with a global `tree.sync()` on startup, which Discord can take up to an hour to
roll out the first time.
