#!/usr/bin/env python3
"""
STEM WEEK Admin App - Entry Point
A standalone application for managing STEM Week events.
"""
import sys
import os
from configparser import ConfigParser
from pathlib import Path

from app.interface.panel import AdminApp


def load_config(config_path: str = "config.ini") -> dict:
    """Load configuration from config.ini file."""
    config = ConfigParser()
    
    if not os.path.exists(config_path):
        # Create default config if it doesn't exist
        create_default_config(config_path)
    
    config.read(config_path)
    
    # Get values with defaults
    return {
        "server_ip": config.get("server", "ip", fallback="127.0.0.1"),
        "server_port": config.get("server", "port", fallback="8080"),
    }


def create_default_config(config_path: str = "config.ini"):
    """Create a default configuration file."""
    config = ConfigParser()
    config.add_section("server")
    config.set("server", "ip", "127.0.0.1")
    config.set("server", "port", "8080")
    config.set("server", "# ip", "Change this to your server IP on event day")
    
    with open(config_path, "w") as f:
        f.write("# STEM WEEK Admin App Configuration\n")
        f.write("# Update the IP address to match your server on event day\n\n")
        config.write(f)
    
    print(f"✓ Created default config file: {config_path}")
    print(f"  Please update the server IP before running the app.")


def main():
    """Main entry point for the Admin App."""
    print("=" * 60)
    print("STEM WEEK // ADMIN CONTROL CENTER")
    print("=" * 60)
    
    # Load configuration
    config = load_config("config.ini")
    server_ip = config["server_ip"]
    server_port = config["server_port"]
    
    uri = f"wss://{server_ip}:{server_port}"
    
    print(f"\n📡 Server Configuration:")
    print(f"   IP:   {server_ip}")
    print(f"   Port: {server_port}")
    print(f"   URI:  {uri}")
    print(f"\n📖 Keybindings:")
    print(f"   q: Quit")
    print(f"   r: Refresh Data")
    print(f"   d: Debug View")
    print(f"   l: Leaderboard View")
    print(f"\n" + "=" * 60 + "\n")
    
    try:
        app = AdminApp(uri=uri)
        app.run()
    except KeyboardInterrupt:
        print("\n\n✓ Admin app closed.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
