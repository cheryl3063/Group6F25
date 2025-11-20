# -*- coding: utf-8 -*-
import io
import sys
import requests

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from score_screen import ScoreScreen
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from analytics_screen import AnalyticsScreen
from sensors_listeners import SensorListener
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from score_screen import ScoreScreen   # ✅ FIXED: This was missing

API_URL = "http://127.0.0.1:5050/login"


# -------------------------------------------------------------------
# LOGIN SCREEN
# -------------------------------------------------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        layout.add_widget(Label(text="Driver Analytics", font_size=28, bold=True))
        layout.add_widget(Label(text="Login to continue", font_size=18))

        self.email_input = TextInput(hint_text="Email", multiline=False, height=40, size_hint_y=None)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, height=40, size_hint_y=None)

        login_btn = Button(text="Login", height=45, size_hint_y=None)
        login_btn.bind(on_press=self.handle_login)

        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def handle_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            return self.show_popup("Error", "Please enter both email and password.")

        if not email.endswith("@gmail.com"):
            return self.show_popup("Error", "Email must end with @gmail.com.")

        try:
            # For now, bypass backend login to allow UI testing
            print("⚠️ Bypassing backend login (demo mode).")
            self.manager.current = "dashboard"

        except requests.exceptions.RequestException as e:
            self.show_popup("Error", f"Connection error: {e}")

    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message, font_size=16),
            size_hint=(0.75, 0.35)
        ).open()


# -------------------------------------------------------------------
# DASHBOARD SCREEN
# -------------------------------------------------------------------
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

        btn_score = Button(text="⭐ View Score", height=45, size_hint_y=None)
        btn_score.bind(on_press=self.go_score)
        layout.add_widget(btn_score)

        btn_logout = Button(text="🔒 Logout", height=45, size_hint_y=None)
        btn_logout.bind(on_press=self.logout)
        layout.add_widget(btn_logout)

        self.add_widget(layout)

    def go_trip(self, instance):
        self.manager.current = "trip"

    def go_analytics(self, instance):
        self.manager.current = "analytics"

    def go_score(self, instance):
        self.manager.current = "score"

    def logout(self, instance):
        self.manager.current = "login"


# -------------------------------------------------------------------
# MAIN APP CONTROLLER
# -------------------------------------------------------------------
class DriverApp(App):

    def build(self):
        sm = ScreenManager(transition=FadeTransition())

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TripRecordingScreen(name="trip"))
        sm.add_widget(AnalyticsScreen(name="analytics"))
        sm.add_widget(TripSummaryScreen(name="trip_summary"))
        sm.add_widget(ScoreScreen(name="score"))     # ✅ FIXED: Added properly

        return sm


if __name__ == "__main__":
    DriverApp().run()
