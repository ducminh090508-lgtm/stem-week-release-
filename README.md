# STEM WEEK Production Apps

This folder contains two standalone applications for the STEM Week event on event day. No setup required beyond downloading, configuring the server IP, and running!

## Getting It On Your Machine

You can simulate a "download" by copying or zipping the production directory. For macOS/Linux the sequence looks like:

```bash
# from your web server or repo clone
curl -LO https://example.com/stemweek-production.zip   # or use wget
unzip stemweek-production.zip
```

If you're simply testing locally you can also copy from the Windows drive (`/mnt/d/stemWeek/production`).

## Folder Structure

```
production/
├── admin-app/          # Admin control center
│   ├── main.py        # Entry point
│   ├── config.ini     # Server configuration
│   ├── run.bat        # Windows launcher
│   ├── requirements.txt
│   ├── README.md
│   └── app/
│       ├── interface/ # UI components
│       └── functions/ # Logic & networking
│
└── user-app/          # Team participation portal
    ├── main.py        # Entry point
    ├── config.ini     # Server configuration
    ├── run.bat        # Windows launcher
    ├── requirements.txt
    ├── README.md
    └── app/
        ├── interface/ # UI components
        ├── functions/ # Logic & networking
        └── shared/    # Shared components
```

## Quick Setup (On Event Day)

### For Admin Team

1. **Extract** the `admin-app` folder to a location on your admin computer
2. **Update** `config.ini` with your server IP:
   ```ini
   [server]
   ip = 192.168.1.100    # Change to your server IP
   port = 8080
   ```
3. **Run** the app:
   - **Windows**: Double-click `run.bat` or open Command Prompt and run `python main.py`
   - **macOS/Linux**: Open Terminal and run `python main.py`
4. **Install dependencies** if prompted (will auto-install on first run)

### For Each Team

1. **Extract** the `user-app` folder to a team computer or kiosk
2. **Update** `config.ini` with your server IP:
   ```ini
   [server]
   ip = 192.168.1.100    # Change to your server IP
   port = 8080
   ```
3. **Run** the app:
   - **Windows**: Double-click `run.bat` or open Command Prompt and run `python main.py`
   - **macOS/Linux**: Open Terminal and run `python main.py`
4. **Enter your team PIN** when prompted (provided by event organizers)

## System Requirements

- **Python 3.8+** (Install from [python.org](https://www.python.org/downloads/))
- **Internet connection** to reach the server
- **Terminal/Command Prompt** with UTF-8 support
- Compatible with Windows, macOS, and Linux

## First-Time Setup Instructions

### Windows Users

1. **Install Python 3.8+**:
   - Download from [python.org](https://www.python.org/downloads/)
   - Important: Check "Add Python to PATH" during installation
   
2. **Verify Python Installation**:
   - Open Command Prompt
   - Type: `python --version`
   - You should see Python 3.8 or higher

3. **Run the App**:
   - Navigate to the app folder
   - Double-click `run.bat`
   - Or open Command Prompt in the folder and type: `python main.py`

### macOS / Linux Users

1. **Install Python 3.8+**:
   - macOS: Use [Homebrew](https://brew.sh) or download from [python.org](https://www.python.org/downloads/)
   - Linux: Use your package manager (apt, yum, etc.)

2. **Verify Python Installation**:
   - Open Terminal
   - Type: `python3 --version`
   - You should see Python 3.8 or higher

3. **Run the App**:
   - Navigate to the app folder
   - Type: `python3 main.py`

## Troubleshooting

### "Python is not recognized"
- Python wasn't installed or not added to PATH
- Reinstall Python and check "Add Python to PATH"

### "Can't connect to server"
- Verify server IP in `config.ini` is correct
- Ensure server is running on port 8080
- Check network connectivity and firewall

### "ModuleNotFoundError" (missing packages)
- Run: `pip install -r requirements.txt` (or `pip3` on macOS/Linux)
- Windows `run.bat` will auto-install if packages are missing

### "Port already in use"
- Another application is using port 8080
- Change port in `config.ini` on both admin and user apps

### Terminal UI is broken or garbled
- Update your terminal to support UTF-8
- Try a different terminal application
- On Windows, use Windows Terminal (better than CMD) or PowerShell

## App Features

### Admin App (`admin-app`)
- Real-time leaderboard monitoring
- Start/pause timers for teams
- Apply penalties (hints, inaccuracies, DNF)
- View active connections and system logs
- Debug console for troubleshooting

**Keyboard Shortcuts:**
- `q` - Quit
- `r` - Refresh data
- `d` - Debug view
- `l` - Leaderboard view

### User App (`user-app`)
- Team PIN authentication
- Question modules (BIO, CHEM, MATH & PHYSICS, CS)
- Real-time synchronized timer
- Live leaderboard
- Answer submission with instant feedback

**Keyboard Shortcuts:**
- `1` - Questions
- `2` - Timer
- `3` - Leaderboard
- `escape` - Back
- `q` - Quit

## Network Configuration

## Containerised Deployment

If a machine doesn’t have Python installed (e.g. a kiosk), you can run either app in a Docker container. Each subfolder now contains a `Dockerfile`.

Build an image from the appropriate folder:

```sh
# admin container
cd admin-app
docker build -t stemweek-admin .

# user container
cd ../user-app
docker build -t stemweek-user .
```

Run the container, mounting a configuration file from the host:

```sh
# start admin UI
docker run --rm -it \
    -v /path/to/my-admin-config.ini:/etc/stemweek/config.ini \
    stemweek-admin

# start user UI
docker run --rm -it \
    -v /path/to/my-user-config.ini:/etc/stemweek/config.ini \
    stemweek-user
```

Config volumes allow you to change server IP without rebuilding.

## Network Configuration

By default:
- Server IP: `127.0.0.1` (localhost)
- Server Port: `8080`

On **event day**, update both `config.ini` files with the actual server IP address. The port should remain `8080` unless your server uses a different port.

### Example Server IPs

- **Same network**: `192.168.1.100` (depends on your network)
- **Remote server**: `example.com` or `203.0.113.42`
- **Cloud server**: Provided by your hosting service

## Support

If you encounter issues:

1. **Check README.md** in each app folder for app-specific help
2. **Check config.ini** to ensure server IP is correct
3. **Verify network connectivity** with `ping <server-IP>`
4. **Check server logs** from the admin app
5. **Reinstall packages**: `pip install --upgrade -r requirements.txt`

## Development Notes

The apps communicate with the server via WebSocket (secure WSS connection). All configuration is stored in `config.ini` files, making it easy to deploy to different networks.

### File Structure
- `app/interface/` - Textual UI components
- `app/functions/` - Business logic and WebSocket communication
- `app/shared/` - Shared components used by multiple views

For production deployment, users simply update the server IP in `config.ini` and run `python main.py`.
