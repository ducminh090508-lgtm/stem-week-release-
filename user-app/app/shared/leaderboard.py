from __future__ import annotations

from dataclasses import dataclass
from typing import List

from art import text2art  # type: ignore
from rich.align import Align
from rich.box import HORIZONTALS, ASCII
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Static, Footer, Header

@dataclass(frozen=True)
class Entry:
    rank_label: str              # e.g. "01"
    team: str                    # team name
    time_display: str            # e.g. "12:34"
    hints: int
    dnf: int
    inaccurate: int

class Leaderboard(Static):
    """Renders a themed leaderboard table for STEM Week with a merged-style header."""
    def __init__(self, entries: List[Entry], *, title: str = "RANKING // GLOBAL LEADERBOARD", **kwargs) -> None:
        super().__init__(**kwargs)
        self.entries = entries
        self.header_title = title

    def _build_table(self) -> Table:
        # Using HORIZONTALS box to remove vertical bars between columns
        table = Table(
            box=HORIZONTALS,
            show_header=False,
            show_lines=True,
            pad_edge=False,
            expand=True,
            border_style="#222222",
        )

        # Columns with ratios to maintain alignment
        table.add_column("RANK", justify="center", ratio=1)
        table.add_column("TEAM", justify="center", ratio=2)
        table.add_column("TIME", justify="center", ratio=2)
        table.add_column("HINTS", justify="center", ratio=1)
        table.add_column("DNF", justify="center", ratio=1)
        table.add_column("ACC", justify="center", ratio=1)

        # Header row 1: PENALTIES centered over the last 3 columns
        table.add_row(
            Text("RANK", style="bold #bb9af7"),
            Text("TEAM", style="bold #7dcfff"),
            Text("TIME", style="bold #7dcfff"),
            Text(""),
            Text("PENALTIES", style="bold #f7768e", justify="center"),
            Text(""),
            end_section=True
        )

        # Header row 2: Sub-headers for penalties
        table.add_row(
            Text(""),
            Text(""),
            Text(""),
            Text("HINT", style="dim #f7768e"),
            Text("DNF", style="dim #f7768e"),
            Text("ACC", style="dim #f7768e"),
            end_section=True
        )

        # Data rows
        for i, e in enumerate(self.entries):
            # Rank color styling (Gold, Silver, Bronze, Default)
            rank_style = "#e0af68" if i == 0 else "#a9b1d6" if i == 1 else "#cd7f32" if i == 2 else "#565f89"
            
            table.add_row(
                Text(e.rank_label, style=f"bold {rank_style}"),
                Text(e.team.upper(), style="white"),
                Text(e.time_display, style="#33d17a"),
                Text(str(e.hints), style="#f7768e" if e.hints > 0 else "#565f89"),
                Text(str(e.dnf), style="#f7768e" if e.dnf > 0 else "#565f89"),
                Text(str(e.inaccurate), style="#f7768e" if e.inaccurate > 0 else "#565f89"),
            )

        return table

    def render(self):
        # ASCII Logo
        logo = Text(text2art("LEADERBOARD", font="small").rstrip("\n"), style="#7dcfff")
        
        status_line = Text.assemble(
            ("[ ", "#565f89"),
            ("STATUS: ", "bold #a9b1d6"),
            ("WOOOOOOOOOOO", "#33d17a"),
            (" ]", "#565f89")
        )

        # Render table
        table = self._build_table()
        body = Group(
            Align.center(logo),
            Align.center(status_line),
            "",
            table,
        )
        panel = Panel(
            body,
            title=self.header_title,
            border_style="#7dcfff",
            expand=True
        )
        return panel
