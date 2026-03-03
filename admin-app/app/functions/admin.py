import asyncio
import json
import ssl
from typing import Optional, Callable
import websockets

class AdminService:
    def __init__(self, uri: str = "wss://localhost:8080"):
        self.uri = uri
        self.ws = None
        self._shutdown = asyncio.Event()

        # Callbacks for UI updates
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[str], None]] = None
        self.on_admin_data: Optional[Callable[[dict], None]] = None
        self.on_log: Optional[Callable[[str], None]] = None
        self.on_debug_conns: Optional[Callable[[list], None]] = None
        self.on_debug_logs: Optional[Callable[[list], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    async def connect(self):
        """Main loop to connect and handle incoming messages as an Admin."""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        while not self._shutdown.is_set():
            try:
                async with websockets.connect(self.uri, ssl=ssl_context) as ws:
                    self.ws = ws
                    if self.on_connected:
                        self.on_connected()

                    # Authenticate as Admin
                    await self._send_command("ADMIN_LOGIN")
                    
                    # Request initial full data load
                    await self.get_admin_data()

                    async for message in ws:
                        if self._shutdown.is_set():
                            break
                        await self._handle_message(message)

            except Exception as e:
                # Discard current socket
                self.ws = None
                if self.on_disconnected:
                    self.on_disconnected(str(e))
                # Wait before reconnecting to prevent thrashing
                if not self._shutdown.is_set():
                    await asyncio.sleep(2)

    async def _handle_message(self, raw_msg: str):
        try:
            msg = json.loads(raw_msg)
            msg_type = msg.get("type", "")

            if msg_type == "LOG" and self.on_log:
                self.on_log(msg.get("msg", ""))
            elif msg_type == "ADMIN_DATA" and self.on_admin_data:
                self.on_admin_data(msg.get("data", {}))
            elif msg_type == "DEBUG_CONNS" and self.on_debug_conns:
                self.on_debug_conns(msg.get("data", []))
            elif msg_type == "DEBUG_LOGS" and self.on_debug_logs:
                self.on_debug_logs(msg.get("data", []))
            
        except json.JSONDecodeError:
            if self.on_error:
                self.on_error(f"Failed to parse server message: {raw_msg}")

    async def _send_command(self, cmd: str) -> bool:
        """Helper to safely send commands if socket is open."""
        if not self.ws:
            if self.on_error:
                self.on_error("Not connected to server.")
            return False
            
        try:
            await self.ws.send(cmd)
            return True
        except Exception as e:
            if self.on_error:
                self.on_error(f"Send failed: {e}")
            return False

    async def apply_penalty(self, team_ids: str, penalty_type: str, seconds: int):
        """Request the server to apply a penalty to multiple teams."""
        # PENALTY <tids> <typeId> <seconds>
        success = await self._send_command(f"PENALTY {team_ids} {penalty_type} {seconds}")
        if success:
            # Refresh data to reflect penalty instantly
            await self.get_admin_data()

    async def get_admin_data(self):
        """Fetch the current full state (leaderboards, teams, progress) from the server."""
        await self._send_command("GET_ADMIN_DATA")

    async def start_protocol(self, team_ids: str):
        """Send the START signal to server for multiple teams."""
        # The Server.cpp now handles "START 1,2,3"
        await self._send_command(f"START {team_ids}")

    async def pause_protocol(self, team_ids: str):
        """Send the PAUSE signal to server for multiple teams."""
        await self._send_command(f"PAUSE {team_ids}")

    async def pause_all(self):
        """Send the PAUSE_ALL signal to server to pause all active timers."""
        await self._send_command("PAUSE_ALL")

    async def fetch_debug_conns(self):
        """Request the server to send current connection metadata."""
        await self._send_command("GET_DEBUG_CONNS")

    async def fetch_debug_logs(self):
        """Request the server to send buffered log history."""
        await self._send_command("GET_DEBUG_LOGS")

    def shutdown(self):
        self._shutdown.set()
        if self.ws:
            asyncio.create_task(self.ws.close())
