import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
import requests
import threading
import json

# Camera4Kivy per la gestione nativa della telecamera
from camera4kivy import Preview

class ScannerRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.store = JsonStore('config.json')
        
        # Carica IP salvato o usa default
        self.pc_ip = self.store.get('pc')['ip'] if self.store.exists('pc') else "192.168.1.100"
        
        # --- UI HEADER ---
        header = BoxLayout(size_hint_y=0.15, padding=10, spacing=10)
        self.ip_input = TextInput(
            text=self.pc_ip, 
            multiline=False, 
            size_hint_x=0.7,
            font_size='18sp',
            padding_y=(10, 10)
        )
        save_btn = Button(
            text="CONNETTI PC", 
            size_hint_x=0.3,
            background_color=(0.1, 0.5, 0.8, 1)
        )
        save_btn.bind(on_press=self.save_ip)
        header.add_widget(self.ip_input)
        header.add_widget(save_btn)
        self.add_widget(header)
        
        # --- TELECAMERA ---
        # Preview con analisi automatica dei codici
        self.preview = Preview(
            letterbox_color=[0, 0, 0, 1]
        )
        # Collega il callback per quando viene trovato un codice
        self.preview.extracted_data = self.on_barcode_scanned
        self.add_widget(self.preview)
        
        # --- FOOTER STATUS ---
        self.status = Label(
            text="Inquadra DataMatrix UDI", 
            size_hint_y=0.1, 
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        self.add_widget(self.status)
        
        self.last_code = None

    def save_ip(self, instance):
        self.pc_ip = self.ip_input.text
        self.store.put('pc', ip=self.pc_ip)
        self.status.text = f"Connesso a: {self.pc_ip}"
        self.status.color = (0, 1, 0, 1)

    def on_barcode_scanned(self, preview, code_data):
        """Chiamato automaticamente quando viene rilevato un codice."""
        if code_data == self.last_code:
            return # Evita invii duplicati dello stesso codice
            
        self.last_code = code_data
        self.status.text = f"Codice Rilevato: {code_data}"
        self.send_to_pc(code_data)

    def send_to_pc(self, code):
        def _thread_send():
            try:
                url = f"http://{self.pc_ip}:8766"
                # Invia il codice al server del programma PC
                response = requests.post(url, json={"code": code}, timeout=2)
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.update_status(f"✅ INVIATO AL PC: {code}", (0, 1, 0, 1)))
                else:
                    Clock.schedule_once(lambda dt: self.update_status("❌ Errore Risposta PC", (1, 0, 0, 1)))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f"⚠️ PC NON TROVATO ({self.pc_ip})", (1, 0.5, 0, 1)))
        
        threading.Thread(target=_thread_send).start()

    def update_status(self, text, color):
        self.status.text = text
        self.status.color = color
        # Resetta l'ultimo codice dopo 3 secondi per permettere una nuova scansione dello stesso oggetto
        Clock.schedule_once(self.reset_last_code, 3)

    def reset_last_code(self, dt):
        self.last_code = None

class VScannerApp(App):
    def build(self):
        return ScannerRoot()

if __name__ == '__main__':
    VScannerApp().run()