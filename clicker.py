import threading
import time

import pyautogui


class AutoClicker:
    def __init__(self, intervalo_clique=0.05):
        self.ligado = False
        self.rodando = True
        self.intervalo_clique = intervalo_clique

    def iniciar(self):
        thread = threading.Thread(target=self._clicar, daemon=True)
        thread.start()

    def _clicar(self):
        while self.rodando:
            if self.ligado:
                pyautogui.click()
                time.sleep(self.intervalo_clique)
            else:
                time.sleep(0.1)

    def ligar(self):
        self.ligado = True

    def desligar(self):
        self.ligado = False

    def alternar(self):
        if self.ligado:
            self.desligar()
        else:
            self.ligar()

    def definir_intervalo(self, intervalo):
        self.intervalo_clique = intervalo

    def parar(self):
        self.rodando = False