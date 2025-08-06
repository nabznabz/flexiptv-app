from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='NabziP TV', font_size='32sp'))
        self.server_input = TextInput(hint_text='Adresse du serveur', multiline=False)
        self.mac_input = TextInput(hint_text='Adresse MAC', multiline=False)
        layout.add_widget(self.server_input)
        layout.add_widget(self.mac_input)
        btn = Button(text='Se connecter', size_hint_y=0.2)
        btn.bind(on_press=self.do_connect)
        layout.add_widget(btn)
        self.add_widget(layout)

    def do_connect(self, instance):
        app = App.get_running_app()
        app.server = self.server_input.text
        app.mac = self.mac_input.text
        app.root.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='Écran principal', font_size='24sp'))

class IPTVApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    IPTVApp().run()

