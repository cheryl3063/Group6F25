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
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.animation import Animation

from analytics_screen import AnalyticsScreen
from trip_screen import TripRecordingScreen
from trip_summary_screen import TripSummaryScreen
from score_screen import ScoreScreen


API_URL = "http://127.0.0.1:5050/login"


# =====================================================================
#                    TOP MENU MIXIN (Hamburger Menu)
# =====================================================================
class TopMenuMixin:
    def build_top_menu(self, layout):
        """Call inside your screen to attach a menu button + animated panel."""
        parent = FloatLayout()
        parent.add_widget(layout)

        # --- MENU BUTTON ---
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

        # --- HIDDEN MENU PANEL ---
        self.menu_panel = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=0,
            pos_hint={"top": 1},
            padding=dp(12),
            spacing=dp(10)
        )

        with self.menu_panel.canvas.before:
            Color(0.1, 0.1, 0.1, 0.95)
            self.menu_bg = RoundedRectangle(radius=[0])

        def update_bg(*_):
            self.menu_bg.pos = self.menu_panel.pos
            self.menu_bg.size = self.menu_panel.size

        self.menu_panel.bind(pos=update_bg, size=update_bg)

        # BUTTON FACTORY
        def menu_btn(text, target):
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(55),
                background_color=(0.2, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                font_size=20
            )
            btn.bind(on_press=lambda *_: self.goto(target))
            return btn

        # Add menu options
        self.menu_panel.add_widget(menu_btn("🏠 Dashboard", "dashboard"))
        self.menu_panel.add_widget(menu_btn("🚗 Trip Recording", "trip"))
        self.menu_panel.add_widget(menu_btn("📊 Analytics", "analytics"))
        self.menu_panel.add_widget(menu_btn("📄 Trip Summary", "trip_summary"))
        self.menu_panel.add_widget(menu_btn("⭐ Score", "score"))
        self.menu_panel.add_widget(menu_btn("🔒 Logout", "login"))

        parent.add_widget(self.menu_panel)
        return parent

    # --- ANIMATION LOGIC ---
    def toggle_menu(self, *_):
        if self.menu_panel.height == 0:
            Animation(height=dp(330), d=0.25).start(self.menu_panel)
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

        root = BoxLayout(orientation='vertical', padding=35, spacing=20)

        root.add_widget(Label(text="🚗 Driver Analytics", font_size=32, bold=True))
        root.add_widget(Label(text="Sign in to continue",
                              font_size=20,
                              color=(0.8, 0.8, 0.8, 1)))

        self.email_input = TextInput(
            hint_text="Email Address",
            multiline=False,
            height=55,
            size_hint_y=None,
            font_size=18,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )

        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            height=55,
            size_hint_y=None,
            password=True,
            font_size=18,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )

        root.add_widget(self.email_input)
        root.add_widget(self.password_input)

        login_btn = Button(
            text="Sign In",
            height=55,
            size_hint_y=None,
            font_size=20,
            background_color=(0.1, 0.5, 1, 1)
        )
        login_btn.bind(on_press=self.handle_login)
        root.add_widget(login_btn)

        self.add_widget(root)

    def handle_login(self, instance):
        print("🔓 Demo login: bypassing auth.")
        self.manager.current = "dashboard"

    def show_popup(self, title, message):
        Popup(title=title, content=Label(text=message), size_hint=(0.75, 0.35)).open()


# =====================================================================
#                         DASHBOARD SCREEN
# =====================================================================
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )

        # Dashboard card
        card = BoxLayout(
            orientation='vertical',
            spacing=dp(18),
            padding=dp(25),
            size_hint=(0.9, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        with card.canvas.before:
            Color(1, 1, 1, 0.08)
            self.card_bg = RoundedRectangle(radius=[25])

        card.bind(pos=lambda *_: self._update_bg(card),
                  size=lambda *_: self._update_bg(card))

        title = Label(text="🏠 Dashboard", font_size=32, bold=True)
        card.add_widget(title)

        # Buttons
        def make_btn(text, icon, target):
            btn = Button(
                text=f"{icon}  {text}",
                font_size=20,
                height=dp(60),
                size_hint_y=None,
                background_color=(0.18, 0.18, 0.18, 0.85),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda *_: setattr(self.manager, "current", target))
            return btn

        card.add_widget(make_btn("Start Trip Recording", "🚗", "trip"))
        card.add_widget(make_btn("View Analytics", "📊", "analytics"))
        card.add_widget(make_btn("Trip Summary", "📄", "trip_summary"))
        card.add_widget(make_btn("View Score", "⭐", "score"))
        card.add_widget(make_btn("Logout", "🔒", "login"))

        root.add_widget(card)
        self.add_widget(root)

    def _update_bg(self, card):
        self.card_bg.pos = card.pos
        self.card_bg.size = card.size


# =====================================================================
#                        MAIN APP
# =====================================================================
class DriverApp(App):
    def build(self):
        sm = ScreenManager()
        sm.transition = FadeTransition(duration=0.35)

        sm.add_widget(LoginScreen(name="login"))

        # Add dashboard
        sm.add_widget(DashboardScreen(name="dashboard"))

        # Add screens with animated menu
        sm.add_widget(self.wrap_with_menu(TripRecordingScreen(name="trip")))
        sm.add_widget(self.wrap_with_menu(AnalyticsScreen(name="analytics")))
        sm.add_widget(self.wrap_with_menu(TripSummaryScreen(name="trip_summary")))
        sm.add_widget(self.wrap_with_menu(ScoreScreen(name="score")))

        return sm

    def wrap_with_menu(self, screen):
        """Attach top hamburger menu to a screen."""
        if not isinstance(screen, TopMenuMixin):
            screen.__class__ = type(
                screen.__class__.__name__,
                (TopMenuMixin, screen.__class__),
                {}
            )

        original_layout = screen.children[0]
        screen.remove_widget(original_layout)

        wrapped = screen.build_top_menu(original_layout)
        screen.add_widget(wrapped)
        return screen


if __name__ == "__main__":
    DriverApp().run()
