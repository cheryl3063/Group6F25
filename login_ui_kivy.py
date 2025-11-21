# login_ui_kivy.py
# -*- coding: utf-8 -*-
import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from analytics_screen import AnalyticsScreen
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from score_screen import ScoreScreen

API_URL = "http://127.0.0.1:5050/login"


# ---------------------------------------------------------
# LOGIN SCREEN (cleaner layout + accessibility polish)
# ---------------------------------------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=35,
            spacing=20
        )

        # Title section
        root.add_widget(Label(
            text="🚗 Driver Analytics",
            font_size=32,
            bold=True,
            halign="center",
            valign="middle",
        ))

        root.add_widget(Label(
            text="Sign in to continue",
            font_size=20,
            color=(0.8, 0.8, 0.8, 1),
            halign="center"
        ))

        # Inputs
        self.email_input = TextInput(
            hint_text="Email Address",
            multiline=False,
            size_hint_y=None,
            height=55,
            font_size=18,
            padding_y=(14, 14),
            background_normal='',
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
            padding_y=(14, 14),
            background_normal='',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 0.6, 1, 1),
        )

        root.add_widget(self.email_input)
        root.add_widget(self.password_input)

        # Login button
        login_btn = Button(
            text="Sign In",
            size_hint_y=None,
            height=55,
            font_size=20,
            bold=True,
            background_normal='',
            background_color=(0.1, 0.5, 1, 1),
        )
        login_btn.bind(on_press=self.handle_login)
        root.add_widget(login_btn)

        self.add_widget(root)

    # ------------------------------------------------------
    # Login Logic (unchanged)
    # ------------------------------------------------------
    def handle_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            return self.show_popup("Missing Info", "Please enter both email and password.")

        if not email.endswith("@gmail.com"):
            return self.show_popup("Invalid Email", "Email must end with @gmail.com.")

        # TEMP bypass for UI testing
        print("🔓 Demo mode: bypassing login.")
        self.manager.current = "dashboard"

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=18),
            size_hint=(0.75, 0.35)
        )
        popup.open()


# ---------------------------------------------------------
# DASHBOARD SCREEN (same as before, but nicer visuals)
# ---------------------------------------------------------
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        self.label = Label(text="Welcome!", font_size=24)
        layout.add_widget(self.label)

        btn_trip = Button(text="🚗 Start Trip Recording", height=45, size_hint_y=None)
        btn_trip.bind(on_press=self.go_trip)
        layout.add_widget(btn_trip)

        btn_analytics = Button(text="📊 View Analytics", height=45, size_hint_y=None)
        btn_analytics.bind(on_press=self.go_analytics)
        layout.add_widget(btn_analytics)

        # ⭐ NEW BUTTON
        btn_summary = Button(text="📄 Trip Summary", height=45, size_hint_y=None)
        btn_summary.bind(on_press=lambda *_: setattr(self.manager, "current", "trip_summary"))
        layout.add_widget(btn_summary)

        btn_score = Button(text="⭐ View Score", height=45, size_hint_y=None)
        btn_score.bind(on_press=self.go_score)
        layout.add_widget(btn_score)

        btn_logout = Button(text="🔒 Logout", height=45, size_hint_y=None)
        btn_logout.bind(on_press=self.logout)
        layout.add_widget(btn_logout)

        self.add_widget(layout)


    # -------------------------------
    #   MISSING METHODS (ADD THESE)
    # -------------------------------
    def go_trip(self, *args):
        self.manager.current = "trip"

    def go_analytics(self, *args):
        self.manager.current = "analytics"

    def go_score(self, *args):
        self.manager.current = "score"

    def logout(self, *args):
        self.manager.current = "login"


        # Create a container for rounded card
        container = BoxLayout(padding=dp(10))
        with container.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.15, 0.15, 0.15, 1)  # soft dark grey card
            self.bg_card = RoundedRectangle(radius=[20])

        # Auto-update card size
        def update_card(*args):
            self.bg_card.pos = container.pos
            self.bg_card.size = container.size

        container.bind(pos=update_card, size=update_card)

        container.add_widget(self.layout)
        self.add_widget(container)

# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------
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
