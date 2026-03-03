from __future__ import annotations
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer, Label, Input
from textual.reactive import reactive
from textual import events
from rich.text import Text

from app.interface.timer import StopwatchView
from app.shared.leaderboard import Leaderboard, Entry
from app.functions.question import QuestionService


SUBJECT_CONFIG = {
    "BIO": {
        "title": "BIO",
        "color": "#f07178",
        "desc": "Explore the wonders of life. Identify the species and complete the genetic sequence.",
        "id": "btn-bio"
    },
    "CHEM": {
        "title": "CHEM",
        "color": "#33d17a",
        "desc": "Analyze the reactions. Balance the equations and identify the mysterious compound.",
        "id": "btn-chem"
    },
    "MATH AND PHYSICS": {
        "title": "MATH AND PHYSICS",
        "color": "#4cc9f0",
        "desc": "Solve the fundamental laws. Calculate the forces and find the unknown variables.",
        "id": "btn-mathphysics"
    },
    "CS": {
        "title": "CS",
        "color": "#f72585",
        "desc": "Hack into the system. Decipher the code and debug the faulty algorithms.",
        "id": "btn-cs"
    }
}

class ModuleCard(Static):
    def __init__(self, idName, title, color):
        super().__init__(f"\n\n[b]{title}[/]\n\nPress or Click", id=idName, classes="module-box")
        self.subject_color = color
        self.styles.color = color
        self.titleText = title
        self.targetPage = f"input_{title.lower()}"

    def on_enter(self, event: events.Enter) -> None:
        self.styles.color = "black"

    def on_leave(self, event: events.Leave) -> None:
        self.styles.color = self.subject_color

    def on_click(self) -> None:
        self.app.switchToSubject(self.targetPage)

class QuestionSelectionView(Container):
    def compose(self) -> ComposeResult:
        with Container(classes="modules-container"):
            for key, config in SUBJECT_CONFIG.items():
                yield ModuleCard(config["id"], config["title"], config["color"])
        
        with Container(classes="mega-container"):
            yield Static("\n[#565f89]LOCKED\n\nComplete subject modules to unlock the final puzzle.[/]", id="mega-box")

class InputView(Container):
    def __init__(self, subject: str, color: str, description: str, **kwargs):
        super().__init__(**kwargs)
        self.subject = subject
        self.color = color
        self.description = description

    def compose(self) -> ComposeResult:
        with Static(classes="sidebar") as sidebar:
            sidebar.styles.border = ("round", self.color)
            yield Static(f"[{self.color} bold]{self.subject}[/]\n\n[#a9b1d6]{self.description}[/]")
        
        with Vertical(classes="main-content-area") as area:
            area.styles.border = ("round", "#333333")
            yield Static(f"[{self.color}]// AUTHORIZED ENTRY //[/]", classes="area-header")
            
            with Vertical(id="question-list"):
                yield Label(f"\nPart 1 : [_ _ _ _ _] ( )")
                yield Label(f"Part 2 : [_ _ _ _ _] ( )")
                yield Label(f"Final  : [_ _ _ _ _] ( )\n")
            
            yield Static("", classes="spacer")
            yield Static("", id="answer-feedback")
            with Vertical(id="input-field"):
                yield Input(placeholder="Enter answer...")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        answer = event.value.strip().upper()

        # Clear previous feedback
        self.query_one("#answer-feedback").update("")
        
        # Call the async send_submission method on the app
        await self.app.send_submission(self.subject, answer)
        
        event.input.value = ""

class StemApp(App):
    CSS_PATH = "question.tcss"
    BINDINGS = [
        ("q", "exitToDashboard", "Return to Dashboard"),
        ("1", "navQuestions", "Questions [1]"),
        ("2", "navTimer", "Timer [2]"),
        ("3", "navLeaderboard", "Standings [3]"),
        ("escape", "navQuestions", "Back")
    ]
    
    def __init__(self, team_id: int, team_name: str, uri: str = "wss://localhost:8080", **kwargs):
        super().__init__(**kwargs)
        self.team_id = team_id
        self.team_name = team_name
        self.question_service = QuestionService(team_id=team_id, uri=uri)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-switcher"):
            yield QuestionSelectionView(id="question-page")
        yield Footer()

    async def on_mount(self) -> None:
        self.title = f"STEM WEEK // {self.team_name.upper()}"
        
        # Register View Callbacks to Backend Service
        self.question_service.on_connected = self.on_server_connected
        self.question_service.on_disconnected = self.on_server_disconnected
        self.question_service.on_status_update = self.on_status_update
        self.question_service.on_protocol_started = self.on_protocol_started
        self.question_service.on_rotation_finished = self.on_rotation_finished
        self.question_service.on_feedback = self.on_feedback
        self.question_service.on_leaderboard_update = self.on_leaderboard_update
        
        # Start Backend Tasks
        self.run_worker(self.question_service.connect(), exclusive=False)
        self.run_worker(self.status_polling_loop(), exclusive=False)

    def on_server_connected(self):
        self.notify("Connected to Server", severity="information")

    def on_server_disconnected(self, reason: str):
         self.notify(f"Disconnected: {reason}", severity="warning")

    def on_status_update(self, data: dict):
        total_seconds = data.get("total", 0)
        in_progress = data.get("inProgress", False)
        timer_query = self.query("#page-timer")
        if timer_query:
            timer = timer_query.first()
            timer.sync_time(total_seconds, paused=not in_progress)

    def on_protocol_started(self):
        self.notify("PROTOCOL STARTED // TIMER ACTIVE", severity="information")

    def on_rotation_finished(self):
        self.notify("ROTATION COMPLETED // STOPPING TIMER", severity="success")

    def on_feedback(self, correct: bool):
        input_view = None
        for view in self.query(InputView):
            if view.display:
                input_view = view
                break
        
        if input_view:
            feedback = input_view.query_one("#answer-feedback")
            if correct:
                feedback.update(Text("CORRECT", style="#33d17a", justify="center"))
                self.notify("Correct Answer! Timer Paused.", severity="success")
                
                # Immediate UI pause feedback
                timer_query = self.query("#page-timer")
                if timer_query:
                    timer_query.first().paused = True
            else:
                feedback.update(Text("INCORRECT", style="#f72585", justify="center"))
                self.notify("Incorrect Answer!", severity="error")

    def on_leaderboard_update(self, data: list):
        # We could parse and update leaderboard page here
        # For simplicity, just log or trigger a UI refresh conceptually
        pass

    async def status_polling_loop(self):
        while True:
            await self.question_service.get_status()
            await asyncio.sleep(5)

    async def send_submission(self, subject: str, answer: str):
        await self.question_service.submit_answer(subject=subject, answer=answer)

    def action_navQuestions(self) -> None:
        self.switchToMainPage("questions")

    def action_navTimer(self) -> None:
        self.switchToMainPage("timer")

    def action_navLeaderboard(self) -> None:
        self.switchToMainPage("leaderboard")
        self.run_worker(self.question_service.get_leaderboard())

    def switchToMainPage(self, pageName: str) -> None:
        switcher = self.query_one("#main-switcher")
        
        for child in switcher.children:
            child.display = False

        target_id = f"page-{pageName}"
        existing = switcher.query(f"#{target_id}")
        
        if existing:
            existing.first().display = True
        else:
            if pageName == "questions":
                view = QuestionSelectionView(id=target_id)
                view.add_class("layout-vertical")
                switcher.mount(view)
            elif pageName == "timer":
                view = StopwatchView(id=target_id)
                view.message = "TIMER ACTIVE"
                view.styles.height = "100%"
                view.styles.width = "100%"
                switcher.mount(view)
            elif pageName == "leaderboard":
                mock_entries = [Entry("00", "Loading...", "00:00", 0, 0, 0)]
                view = Leaderboard(mock_entries, id=target_id)
                switcher.mount(view)

    def switchToSubject(self, pageName: str) -> None:
        switcher = self.query_one("#main-switcher")
        
        for child in switcher.children:
            child.display = False
            
        found_config = None
        for key, config in SUBJECT_CONFIG.items():
            if config["id"] == pageName or config["title"].lower() in pageName.lower():
                found_config = config
                break
        
        if not found_config:
            return

        subject = found_config["title"]
        target_id = f"page-input-{subject.lower().replace(' ', '')}"
        existing = switcher.query(f"#{target_id}")
        
        if existing:
            view = existing.first()
            view.display = True
            view.query_one(Input).focus()
        else:
            view = InputView(subject, found_config["color"], found_config["desc"], id=target_id)
            view.add_class("layout-horizontal")
            switcher.mount(view)
            view.query_one(Input).focus()

    async def action_exitToDashboard(self) -> None:
        self.question_service.shutdown()
        self.exit(result=100)

def run(team_id: int = 1, team_name: str = "Team 1", uri: str = "wss://localhost:8080"):
    app = StemApp(team_id=team_id, team_name=team_name, uri=uri)
    return app.run()

if __name__ == "__main__":
    run()
