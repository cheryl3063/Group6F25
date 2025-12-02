# trip_summary_screen.py
import json, os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from trip_summary_utils import compute_summary
from alert_rules import AlertRules


class TripSummaryScreen(Screen):
    LOW_SCORE_THRESHOLD = 50

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = []
        self.alert_rules = AlertRules()
        self.alert_sound = SoundLoader.load("alert.mp3")

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        # Title
        self.title = Label(
            text="[b][color=F5C542]📄 Trip Summary[/color][/b]",
            font_size=26,
            markup=True,
            size_hint_y=None,
            height=dp(40),
            halign="center"
        )
        root.add_widget(self.title)

        center = AnchorLayout()
        root.add_widget(center)

        # Summary card
        card = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint=(0.75, None),
            height=dp(350),
            pos_hint={"center_x": 0.5},
        )

        from kivy.graphics import Color, RoundedRectangle
        with card.canvas.before:
            Color(0.12, 0.12, 0.12, 0.9)
            self.bg = RoundedRectangle(radius=[15])

        card.bind(pos=self._update_bg, size=self._update_bg)

        # MAIN METRICS TEXT
        self.metrics = Label(
            text="[i]No data yet.[/i]",
            font_size=18,
            markup=True,
            halign="left",
            valign="top",
            text_size=(dp(300), None),
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", (self.metrics.width, None)))
        card.add_widget(self.metrics)

        # ALERT SUMMARY SECTION (OPTION A)
        self.alert_section = Label(
            text="[b]--- Alerts for This Trip ---[/b]\n[i]No alerts yet.[/i]",
            font_size=17,
            markup=True,
            halign="left",
            valign="top",
            text_size=(dp(300), None),
        )
        self.alert_section.bind(size=lambda *_: setattr(self.alert_section, "text_size", (self.alert_section.width, None)))
        card.add_widget(self.alert_section)

        center.add_widget(card)

        # BUTTON ROW
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(50), 0])
        self.btn_back = Button(text="⬅ Back")
        self.btn_back.bind(on_press=self._go_back)

        self.btn_refresh = Button(text="↻ Recompute")
        self.btn_refresh.bind(on_press=lambda *_: self._render())

        btn_row.add_widget(self.btn_back)
        btn_row.add_widget(self.btn_refresh)

        root.add_widget(btn_row)
        self.add_widget(root)

    def _update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def _go_back(self, *_):
        self.manager.current = "dashboard"

    def set_samples(self, samples):
        self.alert_rules.reset()
        self.samples = samples or []
        self._render()

    # ----------------- SAVE FINAL SUMMARY -----------------
    def _save_final_summary(self, summary):
        FILE = "trip_summary.json"

        if os.path.exists(FILE):
            try:
                with open(FILE, "r") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except:
                data = []
        else:
            data = []

        data.append(summary)

        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)

        print("✔ Trip summary saved to trip_summary.json")

    # ----------------- RENDER FULL SUMMARY -----------------
    def _render(self):
        s = compute_summary(self.samples)

        # ---------- MAIN SUMMARY ----------
        self.metrics.text = (
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ [b]Safety Score: {s['safety_score']}[/b]"
        )

        # ---------- ALERT SUMMARY (OPTION A) ----------
        speeding = s.get("speeding_events", 0)
        brakes = s.get("brake_events", 0)
        harsh = s.get("harsh_accel", 0)

        total_alerts = speeding + brakes + harsh

        self.alert_section.text = (
            "[b]--- Alerts for This Trip ---[/b]\n"
            f"🚨 Speeding: {speeding}\n"
            f"🛑 Braking: {brakes}\n"
            f"⚡ Harsh Accel: {harsh}\n"
            f"📊 Total Alerts: {total_alerts}"
        )

        # ---------- LOW SCORE ALERT ----------
        score = int(s["safety_score"])
        if self.alert_rules.evaluate_score(score):
            if self.alert_sound:
                self.alert_sound.play()

            popup = Popup(
                title="⚠️ Low Safety Score",
                content=Label(
                    text=f"Your safety score is {score}. Drive more carefully!",
                    font_size=18
                ),
                size_hint=(0.6, 0.35)
            )
            popup.open()

            # Append warning to alert section
            self.alert_section.text += "\n\n❗ [color=FF4444][b]Low Safety Score![/b][/color]"

        # ---------- SAVE SUMMARY ----------
        self._save_final_summary(s)
