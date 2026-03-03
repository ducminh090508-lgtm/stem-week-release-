# STEM WEEK Admin App

A standalone terminal-based application for event administrators to control and monitor STEM Week competitions.

## Features

- **Real-time Leaderboard**: View team standings and progress
- **Team Management**: Start/pause timers for individual teams or all teams
- **Penalty System**: Apply hints, inaccuracy, and DNF penalties
- **Debug Console**: Monitor active connections and system logs
- **Live Status**: Real-time updates from the server

## Quick Start

### Windows

1. Extract the admin-app folder
2. Open Command Prompt and navigate to the admin-app folder
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Update `config.ini` with your server IP address
5. Run the app:
   ```
   python main.py
   ```
   *or double-click `run.bat`*

### macOS / Linux

1. Extract the admin-app folder
2. Open Terminal and navigate to the admin-app folder
3. Ensure the `python3-venv` package is installed (`sudo apt install python3-venv`).
4. Install dependencies:
   ```
   pip3 install -r requirements.txt
   ```
   *(the `run.sh` script will also auto-install when executed)*
5. Update `config.ini` with your server IP address
6. Make launcher executable once:
   ```sh
   chmod +x run.sh
   ```
7. Run the app:
   ```sh
   ./run.sh
   ```
   or `python3 main.py`

> The launcher will create a `.venv` directory on first run and install all dependencies inside it, avoiding system-wide package installs.

## Configuration

Edit `config.ini` to set your server connection:

```ini
[server]
ip = 192.168.1.100      # Change to your server IP
port = 8080             # Change if using a different port
```

## Keyboard Controls

- `q` - Quit the application
- `r` - Refresh data from server
- `d` - Switch to debug view
- `l` - Switch to leaderboard view

## Troubleshooting

**Can't connect to server**
- Verify the server IP in `config.ini` is correct
- Ensure the server is running and accessible on port 8080
- Check firewall settings

**AttributeError or import errors**
- Delete the `__pycache__` folder and try again
- Reinstall requirements: `pip install --upgrade -r requirements.txt`

## System Requirements

- Python 3.8+
- Windows, macOS, or Linux
- Terminal/Command Prompt with UTF-8 support
