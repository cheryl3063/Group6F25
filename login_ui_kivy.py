# login_ui_kivy.py
# -*- coding: utf-8 -*-
import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.animation import Animation

from analytics_screen import AnalyticsScreen
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from trip_history_screen import TripHistoryScreen
from score_screen import ScoreScreen
from insights_screen import InsightsScreen

API_URL = "http://127.0.0.1:5050/login"


# =====================================================================
#                    TOP MENU MIXIN (Hamburger Menu)
# =====================================================================
class TopMenuMixin:
    def build_top_menu(self, layout):
        parent = FloatLayout()
        parent.add_widget(layout)

        self.menu_btn = Button(
            text="☰",
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            pos_hint={"right": 0.98, "top": 0.98},
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=28,
        )
        self.menu_btn.bind(on_press=self.toggle_menu)
        parent.add_widget(self.menu_btn)

        self.menu_panel = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=0,
            pos_hint={"top": 1},
            padding=dp(12),
            spacing=dp(10),
        )

        with self.menu_panel.canvas.before:
            Color(0.08, 0.08, 0.08, 0.97)
            self.menu_bg = RoundedRectangle(radius=[0])

        def update_bg(*_):
            self.menu_bg.pos = self.menu_panel.pos
            self.menu_bg.size = self.menu_panel.size

        self.menu_panel.bind(pos=update_bg, size=update_bg)

        def menu_btn(text, target):
            b = Button(
                text=text,
                size_hint_y=None,
                height=dp(52),
                background_color=(0.18, 0.18, 0.18, 1),
                color=(1, 1, 1, 1),
                font_size=18
            )
            b.bind(on_press=lambda *_: self.goto(target))
            return b

        self.menu_panel.add_widget(menu_btn("🏠 Dashboard", "dashboard"))
        self.menu_panel.add_widget(menu_btn("🚗 Trip Recording", "trip"))
        self.menu_panel.add_widget(menu_btn("📊 Analytics", "analytics"))
        self.menu_panel.add_widget(menu_btn("📈 Insights & Trends", "insights"))
        self.menu_panel.add_widget(menu_btn("📄 Trip Summary", "trip_summary"))
        self.menu_panel.add_widget(menu_btn("⭐ Score", "score"))
        self.menu_panel.add_widget(menu_btn("📚 History", "history"))
        self.menu_panel.add_widget(menu_btn("🔒 Logout", "login"))

        parent.add_widget(self.menu_panel)
        return parent

    def toggle_menu(self, *_):
        if self.menu_panel.height == 0:
            Animation(height=dp(340), d=0.25).start(self.menu_panel)
        else:
            Animation(height=0, d=0.25).start(self.menu_panel)

    def goto(self, screen_name):
        self.manager.current = screen_name
        Animation(height=0, d=0.2).start(self.menu_panel)


# =====================================================================
#                         LOGIN SCREEN
# =====================================================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation='vertical', padding=dp(32), spacing=dp(20))

        root.add_widget(Label(
            text="🚗 Driver Analytics",
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=dp(48)
        ))
        root.add_widget(Label(
            text="Sign in to continue",
            font_size=18,
            size_hint_y=None,
            height=dp(30)
        ))

        self.email_input = TextInput(
            hint_text="Email Address",
            multiline=False,
            height=dp(40),
            size_hint_y=None,
            font_size=20,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )

        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            height=dp(40),
            size_hint_y=None,
            password=True,
            font_size=20,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )

        root.add_widget(self.email_input)
        root.add_widget(self.password_input)

        login_btn = Button(
            text="Sign In",
            height=dp(52),
            size_hint_y=None,
            font_size=18,
            background_color=(0.1, 0.5, 1, 1),
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_press=self.handle_login)
        root.add_widget(login_btn)

        self.add_widget(root)

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
                try:
                    msg = resp.json().get("error")
                except Exception:
                    msg = resp.text
                self.show_popup("Error", msg)

        except requests.exceptions.RequestException as e:
            self.show_popup("Error", f"Connection error: {e}")

    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.75, 0.35)
        ).open()


# =====================================================================
#                         DASHBOARD SCREEN
# =====================================================================
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(20)
        )

        self.label = Label(
            text="🏠 Dashboard",
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(self.label)

        card = BoxLayout(
            orientation="vertical",
            spacing=dp(18),
            padding=dp(20),
            size_hint=(1, None),
            height=dp(420),
        )

        with card.canvas.before:
            Color(0.12, 0.12, 0.12, 0.9)
            self.card_bg = RoundedRectangle(radius=[20])

        def update_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size

        card.bind(pos=update_bg, size=update_bg)

        def make_btn(text, icon, target):
            btn = Button(
                text=f"{icon}  {text}",
                font_size=20,
                height=dp(46),
                size_hint_y=None,
                background_color=(0.18, 0.18, 0.18, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda *_: setattr(self.manager, "current", target))
            return btn

        card.add_widget(make_btn("Start Trip Recording", "🚗", "trip"))
        card.add_widget(make_btn("View Analytics", "📊", "analytics"))
        card.add_widget(make_btn("Insights & Trends", "📈", "insights"))
        card.add_widget(make_btn("Trip History", "📚", "history"))
        card.add_widget(make_btn("Driver Score", "⭐", "score"))

        logout_btn = Button(
            text="🔒  Logout",
            font_size=20,
            height=dp(56),
            size_hint_y=None,
            background_color=(0.30, 0.12, 0.12, 1),
            color=(1, 1, 1, 1)
        )
        logout_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "login"))
        card.add_widget(logout_btn)

        root.add_widget(card)
        self.add_widget(root)

    def set_user(self, email, uid):
        self.label.text = f"🏠 Dashboard\n👋 {email} (ID: {uid})"


# =====================================================================
#                        MAIN APP
# =====================================================================
class DriverApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.35))

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))

        # Hybrid: trip + summary + history without menu
        sm.add_widget(TripRecordingScreen(name="trip"))
        sm.add_widget(TripSummaryScreen(name="trip_summary"))
        sm.add_widget(TripHistoryScreen(name="history"))

        # Analytics / score / insights with hamburger menu
        sm.add_widget(self.wrap_with_menu(AnalyticsScreen(name="analytics")))
        sm.add_widget(self.wrap_with_menu(ScoreScreen(name="score")))
        sm.add_widget(self.wrap_with_menu(InsightsScreen(name="insights")))

        return sm

    def wrap_with_menu(self, screen):
        original_class = screen.__class__

        screen.__class__ = type(
            original_class.__name__,
            (TopMenuMixin, original_class),
            {}
        )

        original_layout = screen.children[0]
        screen.remove_widget(original_layout)

        wrapped = screen.build_top_menu(original_layout)
        screen.add_widget(wrapped)

        return screen


if __name__ == "__main__":
    DriverApp().run()
