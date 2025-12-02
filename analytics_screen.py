# analytics_screen.py
import json
import io
from datetime import datetime
import matplotlib.pyplot as plt

from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from mock_backend import BACKEND_FILE

Window.clearcolor = (0, 0, 0, 1)

#-----#
self.manager.current = "history"
#---#

class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", padding=25, spacing=18)

        # -------------------------
        # TITLE
        # -------------------------
        self.title = Label(
            text="[b][color=F5C542]📈 Driving Analytics Overview[/color][/b]",
            font_size=26,
            markup=True,
            size_hint_y=None,
            height=50,
        )
        self.layout.add_widget(self.title)

        # -------------------------
        # METRICS LABELS
        # -------------------------
        self.total_alerts_label = Label(
            text="[i]Loading analytics...[/i]",
            font_size=18,
            color=(1, 1, 1, 1),
            markup=True
        )
        self.layout.add_widget(self.total_alerts_label)

        self.common_alert_label = Label(
            text="",
            font_size=18,
            color=(1, 1, 1, 1),
            markup=True
        )
        self.layout.add_widget(self.common_alert_label)

        self.last5_label = Label(
            text="",
            font_size=18,
            color=(1, 1, 1, 1),
            markup=True
        )
        self.layout.add_widget(self.last5_label)

        # -------------------------
        # BIGGER CHART AREA
        # -------------------------
        self.chart = Image(
            size_hint=(1, None),
            height=520,
            allow_stretch=True,
            keep_ratio=True
        )
        self.layout.add_widget(self.chart)

        # -------------------------
        # BACK BUTTON
        # -------------------------
        back_btn = Button(
            text="⬅ Back",
            font_size=18,
            background_color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.15),
        )
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    # -------------------------
    # LOAD TRIPS
    # -------------------------
    def load_trip_data(self):
        try:
            with open(BACKEND_FILE, "r") as f:
                db = json.load(f)
            return db.get("user123", [])
        except:
            return []

    # -------------------------
    # AGGREGATE ALERTS WEEKLY
    # -------------------------
    def safe_alerts(self, trip):
        """Returns consistent alert values even if missing."""
        alerts = trip.get("alerts") or {}

        return {
            "speeding": alerts.get("speeding", 0) or 0,
            "brakes": alerts.get("brakes", 0) or 0,
            "harsh_accel": alerts.get("harsh_accel", 0) or 0,
        }

    def aggregate_weekly_alerts(self, trips):
        weekly = {}

        for trip in trips:
            created_at = trip.get("created_at")
            if not created_at:
                continue

            try:
                date = datetime.fromisoformat(created_at)
            except:
                continue

            year, week, _ = date.isocalendar()
            key = f"{year}-W{week}"

            a = self.safe_alerts(trip)
            weekly[key] = weekly.get(key, 0) + (a["speeding"] + a["brakes"] + a["harsh_accel"])

        return weekly

    # -------------------------
    # GENERATE CHART
    # -------------------------
    def generate_weekly_chart(self, weekly_data):
        if not weekly_data:
            return None

        weeks = list(weekly_data.keys())
        counts = list(weekly_data.values())

        plt.figure(figsize=(14, 7), dpi=200)
        plt.plot(weeks, counts, marker="o", color="white", linewidth=3)
        plt.title("Weekly Alert Trend", fontsize=22, color="white")
        plt.xlabel("Week", fontsize=18, color="white")
        plt.ylabel("Total Alerts", fontsize=18, color="white")
        plt.grid(True, linestyle="--", alpha=0.4)

        # Theme
        ax = plt.gca()
        ax.set_facecolor("#222222")
        plt.gcf().patch.set_facecolor("#111111")
        ax.tick_params(axis='x', colors='white', labelsize=14)
        ax.tick_params(axis='y', colors='white', labelsize=14)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor=plt.gcf().get_facecolor())
        plt.close()
        buf.seek(0)

        try:
            core_img = CoreImage(buf, ext="png")
            return core_img.texture
        except:
            return None

    # -------------------------
    # UPDATE SCREEN
    # -------------------------
    def on_pre_enter(self):
        trips = self.load_trip_data()

        if not trips:
            self.total_alerts_label.text = "[color=FF4444]No trip data found.[/color]"
            self.common_alert_label.text = ""
            self.last5_label.text = ""
            self.chart.texture = None
            return

        # ---------- TOTAL ALERTS ----------
        total_speed = total_brake = total_harsh = 0

        for t in trips:
            a = self.safe_alerts(t)
            total_speed += a["speeding"]
            total_brake += a["brakes"]
            total_harsh += a["harsh_accel"]

        self.total_alerts_label.text = (
            f"[b][color=F5C542]Total Alerts Across All Trips[/color][/b]\n\n"
            f"🚀 Speeding: {total_speed}\n"
            f"🛑 Braking: {total_brake}\n"
            f"⚡ Harsh Accel: {total_harsh}"
        )

        # ---------- MOST COMMON ALERT ----------
        alert_totals = {
            "Speeding": total_speed,
            "Braking": total_brake,
            "Harsh Accel": total_harsh
        }

        if all(v == 0 for v in alert_totals.values()):
            self.common_alert_label.text = "\n[b]Most Common Alert:[/b] None"
        else:
            mc = max(alert_totals, key=alert_totals.get)
            self.common_alert_label.text = f"\n[b]Most Common Alert:[/b] {mc}"

        # ---------- LAST 5 TRIPS ----------
        last5 = trips[-5:]
        if not last5:
            self.last5_label.text = "\n[b]Last 5 Trips Summary[/b]\nNot enough data."
        else:
            avg_speed = sum(t.get("avg_speed", 0) or 0 for t in last5) / len(last5)
            avg_score = sum(t.get("score", 0) or 0 for t in last5) / len(last5)

            total_last5 = 0
            for t in last5:
                a = self.safe_alerts(t)
                total_last5 += (a["speeding"] + a["brakes"] + a["harsh_accel"])

            self.last5_label.text = (
                f"\n[b]Last 5 Trips Summary[/b]\n"
                f"Average Speed: {avg_speed:.1f} km/h\n"
                f"Average Score: {avg_score:.1f}/100\n"
                f"Total Alerts (Last 5 Trips): {total_last5}"
            )

        # ---------- CHART ----------
        weekly_data = self.aggregate_weekly_alerts(trips)
        tex = self.generate_weekly_chart(weekly_data)

        self.chart.texture = tex if tex else None
