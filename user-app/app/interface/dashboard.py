from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Input, Header, Footer

from app.functions.dashboard import DashboardService
from app.interface import question

class DashboardApp(App):
    CSS_PATH = "dashboard.tcss"

    def __init__(self, server_ip: str, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_service = DashboardService(target_ip=server_ip)

    def compose(self) -> ComposeResult:
        duckAscii = """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣉⡥⠶⢶⣿⣿⣿⣿⣷⣆⠉⠛⠿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡿⢡⡞⠁⠀⠀⠤⠈⠿⠿⠿⠿⣿⠀⢻⣦⡈⠻⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡇⠘⡁⠀⢀⣀⣀⣀⣈⣁⣐⡒⠢⢤⡈⠛⢿⡄⠻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡇⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠉⠐⠄⡈⢀⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠇⢠⣿⣿⣿⣿⡿⢿⣿⣿⣿⠁⢈⣿⡄⠀⢀⣀⠸⣿⣿⣿⣿
⣿⣿⣿⣿⡿⠟⣡⣶⣶⣬⣭⣥⣴⠀⣾⣿⣿⣿⣶⣾⣿⣧⠀⣼⣿⣷⣌⡻⢿⣿
⣿⣿⠟⣋⣴⣾⣿⣿⣿⣿⣿⣿⣿⡇⢿⣿⣿⣿⣿⣿⣿⡿⢸⣿⣿⣿⣿⣷⠄⢻
⡏⠰⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢂⣭⣿⣿⣿⣿⣿⠇⠘⠛⠛⢉⣉⣠⣴⣾
⣿⣷⣦⣬⣍⣉⣉⣛⣛⣉⠉⣤⣶⣾⣿⣿⣿⣿⣿⣿⡿⢰⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡘⣿⣿⣿⣿⣿⣿⣿⣿⡇⣼⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⢸⣿⣿⣿⣿⣿⣿⣿⠁⣿⣿⣿⣿⣿⣿⣿⣿⣿
        """
        
        infoText = f"""
[bold white]USER[/] @ [bold white]STEM WEEK[/]
------------------
[#f7768e bold]OS[/]:      [#7dcfff]STEM WEEK OS[/]
[#f7768e bold]Host[/]:    [#7dcfff]{self.dashboard_service.target_ip}[/]
[#f7768e bold]Port[/]:    [#7dcfff]{self.dashboard_service.port}[/]
[#f7768e bold]Status[/]:  [#7dcfff]Connection Pending[/]
"""

        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Container(id="split-view"):
                yield Static(duckAscii, id="ascii-art")
                yield Static(infoText, id="info-panel")
            
            with Vertical(id="input-area"):
                yield Input(placeholder="ENTER TEAM ID TO ACCESS PROTOCOL...")

        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        team_id_input = event.value.strip()
        
        team_data = self.dashboard_service.verify_team(team_id_input)
        
        if team_data:
            self.exit(result={"team": team_data, "uri": self.dashboard_service.uri})
        else:
            self.notify("INVALID TEAM ID", severity="error")
            event.input.value = ""
            
    def on_mount(self) -> None:
        self.title = "STEM WEEK TERMINAL // ACCESS"

def main(server_ip: str = "127.0.0.1"):
    while True:
        app = DashboardApp(server_ip=server_ip)
        result_data = app.run()
        
        if result_data and isinstance(result_data, dict):
            team_data = result_data["team"]
            target_uri = result_data["uri"]
            print(f"\nInitializing Protocol for {team_data['name']} on {target_uri}...")
            
            # Launch Question Protocol and inject URI
            resultProto = question.run(team_data['id'], team_data['name'], uri=target_uri)
            
            if resultProto == 100:
                continue
            else:
                break
        else:
            print("\nShutting down...")
            break

if __name__ == "__main__":
    main()
