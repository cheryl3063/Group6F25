from kivy.app import App
from kivy.uix.label import Label

class T(App):
    def build(self):
        return Label(text="Kivy OK ✅")

T().run()
