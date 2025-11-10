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
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.text import LabelBase

# Import other project modules
import main
from analytics_screen import AnalyticsScreen
from trip_screen import TripRecordingScreen  # ✅ Added new telemetry screen

# Register emoji font
LabelBase.register(name="EmojiFont", fn_regular="C:\\Windows\\Fonts\\seguiemj.ttf")

API_URL = "http://127.0.0.1:5000/login"

# -------------------------------------------------------------------
# LOGIN SCREEN
# -------------------------------------------------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        layout.add_widget(Label(text="Driver Analytics", font_size=28, bold=True, font_name="EmojiFont"))
        layout.add_widget(Label(text="Login to continue", font_size=18, font_name="EmojiFont"))

        self.email_input = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=40)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=40)

        login_btn = Button(text="Login", size_hint_y=None, height=45, font_name="EmojiFont")
        login_btn.bind(on_press=self.handle_login)

        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def handle_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.show_popup("Error", "Please enter both email and password.")
            return
        if not email.endswith("@gmail.com"):
            self.show_popup("Error", "Please enter a valid Gmail address ending with '@gmail.com'.")
            return

        try:
            resp = requests.post(API_URL, json={"email": email, "password": password}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                uid = data.get("uid", "N/A")
                self.manager.get_screen("dashboard").set_user(email, uid)
                self.manager.transition.direction = "left"
                self.manager.current = "dashboard"
            else:
                msg = resp.json().get("error") or resp.text
                self.show_popup("Error", msg)
        except requests.exceptions.RequestException as e:
            self.show_popup("Error", f"Connection error: {e}")

    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message, font_size=16, font_name="EmojiFont"),
            size_hint=(0.75, 0.35)
        ).open()

# -------------------------------------------------------------------
# DASHBOARD SCREEN
# -------------------------------------------------------------------
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        self.label = Label(text="Welcome!", font_size=24, font_name="EmojiFont")
        self.layout.add_widget(self.label)

        btn_trip = Button(text="🚗 Start Trip Recording", size_hint_y=None, height=45, font_name="EmojiFont")
        btn_trip.bind(on_press=lambda x: self.open_trip())
        self.layout.add_widget(btn_trip)

        btn_analytics = Button(text="📊 View Analytics", size_hint_y=None, height=45, font_name="EmojiFont")
        btn_analytics.bind(on_press=self.open_analytics)
        self.layout.add_widget(btn_analytics)

        btn_logout = Button(text="🔒 Logout", size_hint_y=None, height=45, font_name="EmojiFont")
        btn_logout.bind(on_press=self.logout)
        self.layout.add_widget(btn_logout)

        self.add_widget(self.layout)

    def set_user(self, email, uid):
        self.label.text = f"👋 Welcome, {email}!\nUser ID: {uid}"

    def open_trip(self):
        """Navigate to the live telemetry screen"""
        self.manager.transition.direction = "left"
        self.manager.current = "trip"

    def open_analytics(self, instance):
        self.manager.transition.direction = "left"
        self.manager.current = "analytics"

    def logout(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = "login"

# -------------------------------------------------------------------
# MAIN APP CONTROLLER
# -------------------------------------------------------------------
class DriverApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(AnalyticsScreen(name="analytics"))
        sm.add_widget(TripRecordingScreen(name="trip"))  # ✅ Added Telemetry UI
        return sm

if __name__ == "__main__":
    DriverApp().run()
