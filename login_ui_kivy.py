# -*- coding: utf-8 -*-
import io
import sys
import requests
import main
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from analytics_screen import AnalyticsScreen
from sensors_listeners import SensorListener
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
#from kivy.core.text import LabelBase

import main
from analytics_screen import AnalyticsScreen
from sensors_listeners import SensorListener   # ⬅️ ADD THIS
from trip_screen import TripRecordingScreen    # if you’re using this screen

# Register emoji-friendly font
#LabelBase.register(name="EmojiFont", fn_regular="C:\\Windows\\Fonts\\seguiemj.ttf")
#LabelBase.register(name="EmojiFont", fn_regular="/System/Library/Fonts/Apple Color Emoji.ttc")

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

        self.email_input = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=40)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=40)

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

        # 👇 later you can make this reflect real state (e.g., load from file)
        self.has_saved_trip = True    # assume there is a previous trip for demo

        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        self.label = Label(text="Welcome!", font_size=24)
        self.layout.add_widget(self.label)

        # --- Buttons on the dashboard ---
        btn_trip = Button(text="🚗 Start Trip Recording", size_hint_y=None, height=45)
        btn_trip.bind(on_press=self.start_trip)
        self.layout.add_widget(btn_trip)

        btn_analytics = Button(text="📊 View Analytics", size_hint_y=None, height=45)
        btn_analytics.bind(on_press=self.open_analytics)
        self.layout.add_widget(btn_analytics)

        btn_logout = Button(text="🔒 Logout", size_hint_y=None, height=45)
        btn_logout.bind(on_press=self.logout)
        self.layout.add_widget(btn_logout)

        self.add_widget(self.layout)

    # -------- Helper methods --------
    def set_user(self, email, uid):
        self.label.text = f"👋 Welcome, {email}!\nUser ID: {uid}"

    def start_trip(self, instance):
        """
        Called when the user taps 'Start Trip Recording'.
        If there is a saved trip, show a 'Resume or New' popup.
        Otherwise just start a fresh trip.
        """
        if self.has_saved_trip:
            self._show_resume_dialog()
        else:
            self._run_trip_flow(resume=False)

    def _show_resume_dialog(self):
        """Build and display the 'resume trip' popup."""
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)

        msg = Label(
            text="We found a previous trip.\nWould you like to resume it or start a new one?",
            font_size=16,
            #font_name="EmojiFont"
        )
        content.add_widget(msg)

        # Buttons row
        btn_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        btn_resume = Button(text="🔁 Resume trip")
        btn_new = Button(text="🆕 New trip")
        btn_row.add_widget(btn_resume)
        btn_row.add_widget(btn_new)
        content.add_widget(btn_row)

        popup = Popup(
            title="Resume trip?",
            content=content,
            size_hint=(0.85, 0.45),
            auto_dismiss=True,
        )

        # Wire the buttons
        btn_resume.bind(on_press=lambda *_: self._on_resume_trip(popup))
        btn_new.bind(on_press=lambda *_: self._on_new_trip(popup))

        popup.open()

    def _on_resume_trip(self, popup):
        popup.dismiss()
        self._run_trip_flow(resume=True)

    def _on_new_trip(self, popup):
        popup.dismiss()
        # if user chooses a brand-new trip, we clear the saved flag
        self.has_saved_trip = False
        self._run_trip_flow(resume=False)

    def _run_trip_flow(self, resume: bool):
        """
        Runs your existing 'start trip' backend logic and shows the output
        in a Kivy popup. We just add a little header to distinguish
        Resume vs New.
        """
        try:
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            if resume:
                print("🔁 Resuming previous trip...")
            else:
                print("🆕 Starting a new trip...")

            # Your existing permission / sensor pipeline
            main.main()

            result_output = sys.stdout.getvalue().strip()
            sys.stdout = old_stdout

            Popup(
                title="Trip Recording",
                content=Label(text=result_output, font_size=16),
                size_hint=(0.75, 0.45)
            ).open()

        except Exception as e:
            sys.stdout = old_stdout
            Popup(
                title="Error",
                content=Label(
                    text=f"Failed to start trip: {e}",
                    font_size=16,
                    #font_name="EmojiFont"
                ),
                size_hint=(0.75, 0.35)
            ).open()

    # -------- Navigation buttons --------
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
        self.sensor_listener = SensorListener()  # ✅ Add sensor manager

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(AnalyticsScreen(name="analytics"))
        sm.add_widget(TripSummaryScreen(name="trip_summary"))
        sm.add_widget(TripRecordingScreen(name="trip"))  # Live telemetry screen

        return sm

    # Called from TripRecordingScreen
    def start_trip_recording(self):
        print("DriverApp → Starting sensors...")
        self.sensor_listener.start_listeners()

    def stop_trip_recording(self):
        print("DriverApp → Stopping sensors...")
        self.sensor_listener.stop_listeners()


if __name__ == "__main__":
    DriverApp().run()
