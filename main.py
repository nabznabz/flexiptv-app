import uuid
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.videoplayer import VideoPlayer
import requests

def get_mac_address():
    # Retourne la MAC sous forme HH:HH:HH:HH:HH:HH
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='NabziP TV', font_size='32sp'))
        self.server_input = TextInput(hint_text='Adresse du serveur (ex: http://monserveur)', multiline=False)
        self.mac_input    = TextInput(hint_text='Adresse MAC', multiline=False)
        self.mac_input.text = get_mac_address()  # Pré-remplir la MAC détectée
        layout.add_widget(self.server_input)
        layout.add_widget(self.mac_input)
        btn = Button(text='Se connecter', size_hint_y=0.2)
        btn.bind(on_press=self.do_connect)
        layout.add_widget(btn)
        self.add_widget(layout)

    def do_connect(self, instance):
        app = App.get_running_app()
        app.server = self.server_input.text.strip('/')
        app.mac = self.mac_input.text
        app.root.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_items = []
        main_layout = BoxLayout(orientation='vertical')

        # Barre de recherche
        search_layout = BoxLayout(size_hint_y=0.1, padding=10, spacing=10)
        self.search_input = TextInput(hint_text='Rechercher chaînes, films...', multiline=False)
        search_btn = Button(text='Rechercher', size_hint_x=0.3)
        search_btn.bind(on_press=self.on_search)
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)

        # Boutons de catégories
        nav_layout = BoxLayout(size_hint_y=0.1, spacing=10, padding=10)
        for cat in ['Live', 'Films', 'Séries']:
            btn = Button(text=cat)
            btn.bind(on_press=lambda inst, c=cat: self.load_category(c.lower()))
            nav_layout.add_widget(btn)

        # Zone scrollable pour le contenu
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)

        main_layout.add_widget(search_layout)
        main_layout.add_widget(nav_layout)
        main_layout.add_widget(self.scroll)
        self.add_widget(main_layout)

        # Chargement par défaut de la catégorie Live
        Clock.schedule_once(lambda dt: self.load_category('live'), 0.5)

    def on_search(self, instance):
        q = self.search_input.text.lower()
        filtered = [i for i in self.current_items if q in i['name'].lower()]
        self.display_items(filtered)

    def load_category(self, category):
        app = App.get_running_app()
        try:
            url = f"{app.server}/api/playlist/{category}?mac={app.mac}"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()  # Doit renvoyer liste d’objets {'name':..., 'stream_url':...}
        except Exception as e:
            data = []
            print("Erreur récupération IPTV:", e)
        self.current_items = data
        self.display_items(data)

    def display_items(self, items):
        self.grid.clear_widgets()
        for it in items:
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
            box.add_widget(Label(text=it['name'], size_hint_y=0.7))
            btn = Button(text='▶', size_hint_y=0.3)
            btn.bind(on_press=lambda inst, url=it['stream_url']: self.open_player(url))
            box.add_widget(btn)
            self.grid.add_widget(box)

    def open_player(self, stream_url):
        app = App.get_running_app()
        app.stream_url = stream_url
        app.root.current = 'player'

class PlayerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.video = VideoPlayer(source='', state='stop', options={'allow_stretch': True}, size_hint_y=0.9)
        back = Button(text='← Retour', size_hint_y=0.1)
        back.bind(on_press=self.go_back)
        layout.add_widget(self.video)
        layout.add_widget(back)
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        self.video.source = app.stream_url
        self.video.state = 'play'

    def go_back(self, instance):
        App.get_running_app().root.current = 'main'

class IPTVApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(PlayerScreen(name='player'))
        return sm

if __name__ == '__main__':
    IPTVApp().run()

