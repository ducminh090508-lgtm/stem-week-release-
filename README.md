# Stem Week Release
This folder contains two standalone applications for STEM Week event day. Simply download and then configuire the server IP to start running. Server code found in different repository. 

## Download instructions
Linux/MacOS: 
```
curl -LO https://github.com/ducminh090508-lgtm/stem-week-release-
unzip production.zip
```
Windows: 
```
winget install https://github.com/ducminh090508-lgtm/stem-week-release-
unzip production.zip
```

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
1. **Extract** the `admin-app` onto a folder location on your computer
2. **Update** `config.ini` with your server IP:
```ini
[server]
ip = 192.168.1.100      #change to your server IP
port = 8080
```

3. **Run** the app:
    - **Windows**: Double-click the .exe files and run `python main.py`
    - **MacOS/Linux**: Double-click the .exe files and run `python main.py`
4. **Enter your team PIN** whenever that is given (given by event organizers)

## System Requirement 
- **Absolutely nothing**

## App features



