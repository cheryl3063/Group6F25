# login_ui_kivy.py
# -*- coding: utf-8 -*-
import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from analytics_screen import AnalyticsScreen
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from score_screen import ScoreScreen


API_URL = "http://127.0.0.1:5050/login"


# =====================================================================
#                         LOGIN SCREEN
# =====================================================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=35,
            spacing=20
        )

        root.add_widget(Label(
            text="🚗 Driver Analytics",
            font_size=32,
            bold=True
        ))

        root.add_widget(Label(
            text="Sign in to continue",
            font_size=20,
            color=(0.8, 0.8, 0.8, 1)
        ))

        self.email_input = TextInput(
            hint_text="Email Address",
            multiline=False,
            size_hint_y=None,
            height=55,
            font_size=18,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 0.6, 1, 1),
        )

        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint_y=None,
            height=55,
            font_size=18,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 0.6, 1, 1),
        )

        root.add_widget(self.email_input)
        root.add_widget(self.password_input)

        login_btn = Button(
            text="Sign In",
            size_hint_y=None,
            height=55,
            font_size=20,
            bold=True,
            background_color=(0.1, 0.5, 1, 1),
        )
        login_btn.bind(on_press=self.handle_login)

        root.add_widget(login_btn)
        self.add_widget(root)

    # ---------------- LOGIN ----------------
    def handle_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            return self.show_popup("Missing Info", "Please enter both email and password.")

        if not email.endswith("@gmail.com"):
            return self.show_popup("Invalid Email", "Email must end with @gmail.com.")

        print("🔓 Demo mode: bypassing login.")
        self.manager.current = "dashboard"

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=18),
            size_hint=(0.75, 0.35)
        )
        popup.open()


# =====================================================================
#                         DASHBOARD SCREEN
# =====================================================================
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Root
        root = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )

        # Card container
        card = BoxLayout(
            orientation='vertical',
            spacing=dp(18),
            padding=dp(25),
            size_hint=(0.9, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Glass background
        with card.canvas.before:
            Color(1, 1, 1, 0.08)
            self.card_bg = RoundedRectangle(radius=[25])

        def update_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size

        card.bind(pos=update_bg, size=update_bg)

        # Title
        title = Label(
            text="🏠 Dashboard",
            font_size=32,
            bold=True,
            color=(1, 1, 1, 1)
        )
        card.add_widget(title)

        # BUTTON FACTORY → with custom rounded background
        def make_button(text, icon):
            btn = Button(
                text=f"{icon}  {text}",
                font_size=20,
                size_hint_y=None,
                height=dp(60),
                background_normal='',
                background_color=(0.18, 0.18, 0.18, 0.85),
                color=(1, 1, 1, 1),
                bold=True,
            )

            # Rounded background
            with btn.canvas.before:
                Color(0.18, 0.18, 0.18, 0.85)
                btn._bg = RoundedRectangle(radius=[20])

            def update_btn_bg(*_):
                btn._bg.pos = btn.pos
                btn._bg.size = btn.size

            btn.bind(pos=update_btn_bg, size=update_btn_bg)
            return btn

        # Buttons
        btn_trip = make_button("Start Trip Recording", "🚗")
        btn_analytics = make_button("View Analytics", "📊")
        btn_summary = make_button("Trip Summary", "📄")
        btn_score = make_button("View Score", "⭐")
        btn_logout = make_button("Logout", "🔒")

        # Bind navigation
        btn_trip.bind(on_press=lambda *_: setattr(self.manager, "current", "trip"))
        btn_analytics.bind(on_press=lambda *_: setattr(self.manager, "current", "analytics"))
        btn_summary.bind(on_press=lambda *_: setattr(self.manager, "current", "trip_summary"))
        btn_score.bind(on_press=lambda *_: setattr(self.manager, "current", "score"))
        btn_logout.bind(on_press=lambda *_: setattr(self.manager, "current", "login"))

        # Add buttons
        card.add_widget(btn_trip)
        card.add_widget(btn_analytics)
        card.add_widget(btn_summary)
        card.add_widget(btn_score)
        card.add_widget(btn_logout)

        root.add_widget(card)
        self.add_widget(root)


# =====================================================================
#                           MAIN APP
# =====================================================================
class DriverApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TripRecordingScreen(name="trip"))
        sm.add_widget(AnalyticsScreen(name="analytics"))
        sm.add_widget(TripSummaryScreen(name="trip_summary"))
        sm.add_widget(ScoreScreen(name="score"))

        return sm


if __name__ == "__main__":
    DriverApp().run()
