# weekly_trend_widget.py

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from mock_backend import load_weekly_history


class WeeklyTrendWidget(BoxLayout):
    """
    Simple weekly trend widget using data from mock_backend.load_weekly_history().

    Supports:
    - list of dicts: [{"day": "Mon", "score": 85}, ...]
    - dict: {"Mon": 85, "Tue": 90, ...}
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(4)
        self.size_hint_y = None

        header = Label(
            text="Weekly Trend",
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=dp(24),
            color=(1, 1, 1, 1)
        )
        self.add_widget(header)

        self.rows_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2)
        )
        self.rows_layout.bind(minimum_height=self.rows_layout.setter("height"))
        self.add_widget(self.rows_layout)

        self.refresh_data()

    def refresh_data(self):
        self.rows_layout.clear_widgets()

        try:
            data = load_weekly_history()
        except Exception as exc:
            self.rows_layout.add_widget(
                Label(
                    text=f"Failed to load weekly history: {exc}",
                    font_size=14,
                    color=(1, 0.5, 0.5, 1)
                )
            )
            return

        if isinstance(data, dict):
            items = sorted(data.items(), key=lambda x: x[0])
            for day, score in items:
                self._add_row(str(day), score)
        elif isinstance(data, list):
            for entry in data:
                day = entry.get("day", "?")
                score = entry.get("score", "-")
                self._add_row(str(day), score)
        else:
            self.rows_layout.add_widget(
                Label(
                    text="No weekly data available",
                    font_size=14,
                    color=(0.8, 0.8, 0.8, 1)
                )
            )

    def _add_row(self, day: str, score):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(22)
        )

        day_lbl = Label(
            text=str(day),
            halign="left",
            color=(0.9, 0.9, 0.9, 1)
        )
        day_lbl.bind(size=lambda *_: setattr(day_lbl, "text_size", day_lbl.size))

        score_lbl = Label(
            text=str(score),
            halign="right",
            color=(0.9, 0.9, 0.9, 1)
        )
        score_lbl.bind(size=lambda *_: setattr(score_lbl, "text_size", score_lbl.size))

        row.add_widget(day_lbl)
        row.add_widget(score_lbl)
        self.rows_layout.add_widget(row)
