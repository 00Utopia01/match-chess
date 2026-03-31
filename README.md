# ♟️ Match-Chess Telegram Bot

Match-Chess is a Telegram bot built with `python-telegram-bot` that allows users to play chess directly within the chat interface. It features a matchmaking system, direct user challenges, and persistent state management to ensure games survive bot restarts.

An istance of this bot is available as: [@mchessqd_bot](https://t.me/mchessqd_bot)

## Features

- **Matchmaking Queue:** Find opponents automatically using a global queue system.
    
- **Direct Challenges:** Challenge specific users to a match.
    
- **In-Chat Moves:** Execute chess moves using bot commands.
    
- **Persistence:** Use `PicklePersistence` to save user data and active game states.
    
- **Registration:** Integrated user sign in and terms of service acceptance.
    
---

## Installation

### 1. Clone the Repository


```
git clone https://github.com/yourusername/match-chess.git
cd match-chess
```

### 2. Prerequisites

It is recommended to use a virtual environment:


```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt requirements_dev.txt
```

### 4. Configuration

Create an environment configuration (based on your `src.env` implementation) to provide your Telegram Bot Token.

### 5. Database setup

Setup a mysql database and configure a `.env` file to contain these values (otherwise set them manually):

```
DB_USER="<user>"
DB_HOST="<hostname>"
DB_PASSWORD="<user_pw>"
DB_DATABASE="<db_name>"
```

### 6. Telegram token

Create a bot via [Telegram botfather](https://core.telegram.org/bots/tutorial).
Set the bot token as an environment variable:

```
TELEGRAM_TOKEN=<bot-token>
```

---

## Usage

To start the bot, simply run the main script:

```
python main.py
```

### Available Commands

| Command          | Description                                         |
| -------------------- | ------------------------------------------------------- |
| /start               | Initialize the bot and begin the registration process.  |
| /help                | Display the list of available commands and how to play. |
| /register            | Register your account to start playing.                 |
| /matchmaking         | Enter the global queue to find an opponent.             |
| /challenge_user      | Challenge a specific user by their ID or username.      |
| /play                | Initialize a game session.                              |
| /move <uci_notation> | Make a move in an active game (e.g., `/move e2e4`).     |
| /eula                | View the End User License Agreement.                    |
| /info                | Display user session information.                       |
| /surrender           | Abandon a match.                                        |

---
## Contributing

1. Fork the Project
2. Create your Feature Branch
3. Push to the Branch
4. Open a Pull Request
