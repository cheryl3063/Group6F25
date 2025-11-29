# -*- coding: utf-8 -*-
import io
import json
import os

import sys
import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from data_buffer import DataBuffer


# Import other project modules
from analytics_screen import AnalyticsScreen
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from sensors_listeners import SensorListener

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

        self.email_input = TextInput(
            hint_text="Email",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        self.password_input = TextInput(
            hint_text="Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )

        login_btn = Button(text="Login", size_hint_y=None, height=45)
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

        # Gmail validation
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

        except requests.exceptions.RequestException:
            self.show_popup(
                "Error",
                "Could not reach the server.\n"
                "Make sure the backend (Flask) is running on 127.0.0.1:5050."
            )

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
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        self.label = Label(text="Welcome!", font_size=24)
        self.layout.add_widget(self.label)

        # Trip Summary Button
        btn_summary = Button(text="🧾 Generate Trip Summary", size_hint_y=None, height=45)
        btn_summary.bind(on_press=self.open_trip_summary)
        self.layout.add_widget(btn_summary)

        # Start Trip Button
        btn_trip = Button(text="🚗 Start Trip Recording", size_hint_y=None, height=45)
        btn_trip.bind(on_press=lambda x: self.open_trip())
        self.layout.add_widget(btn_trip)

        # Analytics Button
        btn_analytics = Button(text="📊 View Analytics", size_hint_y=None, height=45)
        btn_analytics.bind(on_press=self.open_analytics)
        self.layout.add_widget(btn_analytics)

        # Logout Button
        btn_logout = Button(text="🔒 Logout", size_hint_y=None, height=45)
        btn_logout.bind(on_press=self.logout)
        self.layout.add_widget(btn_logout)

        self.add_widget(self.layout)

    def set_user(self, email, uid):
        self.label.text = f"👋 Welcome, {email}!\nUser ID: {uid}"

    def open_trip(self):
        self.manager.transition.direction = "left"
        self.manager.current = "trip"

    def open_analytics(self, instance):
        self.manager.transition.direction = "left"
        self.manager.current = "analytics"

    def logout(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = "login"

    def open_trip_summary(self, *_):
        """
        Open the Trip Summary screen using the **latest saved trip**
        from history.json. If no history exists, show a friendly message.
        """
        history_path = "history.json"

        if not os.path.exists(history_path):
            # No history yet → show empty state
            ts = self.manager.get_screen("trip_summary")
            ts.set_summary(None)
            self.manager.transition.direction = "left"
            self.manager.current = "trip_summary"
            return

        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except Exception as e:
            print(f"[Dashboard] Failed to read history.json: {e}")
            ts = self.manager.get_screen("trip_summary")
            ts.set_summary(None)
            self.manager.transition.direction = "left"
            self.manager.current = "trip_summary"
            return

        if not history:
            ts = self.manager.get_screen("trip_summary")
            ts.set_summary(None)
            self.manager.transition.direction = "left"
            self.manager.current = "trip_summary"
            return

        # Use the most recent trip summary
        last_summary = history[-1]

        ts = self.manager.get_screen("trip_summary")
        ts.set_summary(last_summary)
        self.manager.transition.direction = "left"
        self.manager.current = "trip_summary"


# -------------------------------------------------------------------
# MAIN APP CONTROLLER
# -------------------------------------------------------------------
class DriverApp(App):

    def build(self):
        self.sensor_listener = SensorListener()

        # 👉 create one shared DataBuffer instance
        self.data_buffer = DataBuffer()

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(AnalyticsScreen(name="analytics"))
        sm.add_widget(TripSummaryScreen(name="trip_summary"))

        # pass buffer into TripRecordingScreen
        sm.add_widget(TripRecordingScreen(name="trip", data_buffer=self.data_buffer))

        return sm


if __name__ == "__main__":
    DriverApp().run()
