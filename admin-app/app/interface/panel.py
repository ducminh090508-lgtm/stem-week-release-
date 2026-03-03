import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, Button, RichLog, Input, ContentSwitcher
from textual import on, work
from textual.events import Mount

from app.functions.admin import AdminService


class ControlPanel(Static):
    # ... (remains same)
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Target Team ID(s):", classes="label")
            yield Input(placeholder="e.g. 1, 2, 5-10", id="input-team-ids")
            
            with Horizontal(classes="action-row"):
                yield Button("BEGIN PROTOCOL (Start Timer)", id="btn-start", variant="success")
                yield Button("PAUSE", id="btn-pause", variant="warning")
            
            with Horizontal(classes="action-row"):
                yield Button("PAUSE ALL TEAMS", id="btn-pause-all", variant="error")
            
            yield Static("Apply Deductions:", classes="label")
            with Horizontal(classes="action-row"):
                yield Button("HINT (+5m)", id="btn-hint", variant="warning")
                yield Button("INACCURATE (+30s)", id="btn-inaccurate", variant="primary")
                yield Button("DNF (+10m)", id="btn-dnf", variant="error")

class DebugView(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(id="debug-layout"):
            with Vertical(id="debug-left-pane"):
                yield Static("Active Connections", classes="pane-title")
                yield DataTable(id="dt-connections")
                yield Static("System Metadata", classes="pane-title")
                yield Static("Loading server metadata...", id="server-metadata")
            with Vertical(id="debug-right-pane"):
                yield Static("Full Communication Log", classes="pane-title")
                yield RichLog(id="debug-logs", wrap=True, highlight=True, markup=True)

class MainDashboard(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(id="main-layout"):
            with Vertical(id="left-pane"):
                yield Static("Teams & Leaderboard", classes="pane-title")
                yield DataTable(id="dt-leaderboard")
            with Vertical(id="right-pane"):
                yield Static("Command & Control", classes="pane-title")
                yield ControlPanel(id="control-panel")
                yield Static("Server Console Logs", classes="pane-title")
                yield RichLog(id="server-logs", wrap=True, highlight=True, markup=True)

class AdminApp(App):
    CSS_PATH = "panel.tcss"
    BINDINGS = [
        ("q", "quit", "Quit Admin"),
        ("r", "refresh_data", "Refresh Data"),
        ("d", "toggle_debug", "Debug Page"),
        ("l", "toggle_main", "Leaderboard")
    ]

    def __init__(self, uri: str = "wss://localhost:8080", **kwargs):
        super().__init__(**kwargs)
        self.uri = uri
        self.admin_service = AdminService(uri=uri)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ContentSwitcher(initial="main-dashboard"):
            yield MainDashboard(id="main-dashboard")
            yield DebugView(id="debug-view")
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "STEM WEEK // COMMAND CENTER"
        
        # Callbacks
        self.admin_service.on_connected = lambda: self.log_msg("✓ Connected to server.", style="green")
        self.admin_service.on_disconnected = lambda r: self.log_msg(f"⨯ Disconnected: {r}", style="red")
        self.admin_service.on_admin_data = self.on_admin_data
        self.admin_service.on_log = self.on_server_log
        self.admin_service.on_debug_conns = self.on_debug_conns
        self.admin_service.on_debug_logs = self.on_debug_logs

        # Init DataTables
        dt = self.query_one("#dt-leaderboard", DataTable)
        dt.add_columns("ID", "Team Name", "Total Time", "Rank")

        debug_dt = self.query_one("#dt-connections", DataTable)
        debug_dt.add_columns("CID", "IP Address", "Duration", "Sent", "Recv")

        # Background tasks
        self.run_worker(self.admin_service.connect())
        self.run_worker(self.polling_loop())

    async def polling_loop(self):
        while True:
            await self.admin_service.get_admin_data()
            if self.query_one(ContentSwitcher).current == "debug-view":
                await self.admin_service.fetch_debug_conns()
            await asyncio.sleep(2)

    def on_server_log(self, msg: str):
        # Write to both dashboard log and debug log
        for log_id in ["#server-logs", "#debug-logs"]:
            try:
                log_widget = self.query_one(log_id, RichLog)
                log_widget.write(msg)
            except: pass

    def on_debug_conns(self, conns: list):
        dt = self.query_one("#dt-connections", DataTable)
        dt.clear()
        import time
        now = time.time()
        for c in conns:
            duration = int(now - c.get("time", 0))
            dt.add_row(
                str(c.get("id")),
                c.get("ip"),
                f"{duration}s",
                f"{c.get('sent',0)}B",
                f"{c.get('recv',0)}B"
            )

    def on_debug_logs(self, logs: list):
        log_widget = self.query_one("#debug-logs", RichLog)
        log_widget.clear()
        for line in logs:
            log_widget.write(line)

    def action_toggle_debug(self) -> None:
        self.query_one(ContentSwitcher).current = "debug-view"
        asyncio.create_task(self.admin_service.fetch_debug_logs())

    def action_toggle_main(self) -> None:
        self.query_one(ContentSwitcher).current = "main-dashboard"

    def log_msg(self, msg: str, style: str = ""):
        try:
            log_widget = self.query_one("#server-logs", RichLog)
            if style:
                log_widget.write(f"[{style}]{msg}[/]")
            else:
                log_widget.write(msg)
        except: pass

    def on_admin_data(self, data: dict):
        try:
            dt = self.query_one("#dt-leaderboard", DataTable)
            dt.clear()
            leaderboard = data.get("Leaderboard", [])
            for row in leaderboard:
                dt.add_row(
                    str(row.get("team_id", "?")), 
                    str(row.get("team_name", "?")), 
                    str(row.get("total_score_seconds", "?")), 
                    str(row.get("rank", "?"))
                )
        except: pass

    async def action_refresh_data(self):
        self.log_msg("Requesting manual sync...")
        asyncio.create_task(self.admin_service.get_admin_data())

    def get_target_args(self) -> str:
        tid_str = self.query_one("#input-team-ids", Input).value.strip().replace(" ", "")
        return tid_str

    @on(Button.Pressed, "#btn-start")
    async def handle_start(self, event: Button.Pressed) -> None:
        tids = self.get_target_args()
        if not tids:
            self.log_msg("⨯ Please enter Team ID(s)", style="red")
            return
        self.log_msg(f"Initiating protocol for Teams {tids}...")
        asyncio.create_task(self.admin_service.start_protocol(team_ids=tids))

    @on(Button.Pressed, "#btn-pause")
    async def handle_pause(self, event: Button.Pressed) -> None:
        tids = self.get_target_args()
        if not tids:
            self.log_msg("⨯ Please enter Team ID(s)", style="red")
            return
        self.log_msg(f"Pausing protocol for Teams {tids}...")
        asyncio.create_task(self.admin_service.pause_protocol(team_ids=tids))

    @on(Button.Pressed, "#btn-pause-all")
    async def handle_pause_all(self, event: Button.Pressed) -> None:
        self.log_msg("!!! PAUSING ALL ACTIVE TIMERS !!!", style="bold red")
        asyncio.create_task(self.admin_service.pause_all())

    @on(Button.Pressed, "#btn-hint")
    async def handle_hint(self, event: Button.Pressed) -> None:
        tids = self.get_target_args()
        if tids:
            asyncio.create_task(self.admin_service.apply_penalty(team_ids=tids, penalty_type="HINT", seconds=300))

    @on(Button.Pressed, "#btn-inaccurate")
    async def handle_inacc(self, event: Button.Pressed) -> None:
        tids = self.get_target_args()
        if tids:
            asyncio.create_task(self.admin_service.apply_penalty(team_ids=tids, penalty_type="INACCURATE", seconds=30))

    @on(Button.Pressed, "#btn-dnf")
    async def handle_dnf(self, event: Button.Pressed) -> None:
        tids = self.get_target_args()
        if tids:
            asyncio.create_task(self.admin_service.apply_penalty(team_ids=tids, penalty_type="DNF", seconds=600))

    async def on_unmount(self):
        self.admin_service.shutdown()
