"""Coordenação na thread Tk: uma automação por vez e um destino dos atalhos."""


class Automations:
    def __init__(self, clicker, drop, combo=None):
        self.clicker, self.drop, self.combo = clicker, drop, combo
        self.aba = "Auto Click"

    def parar(self):
        # Sempre tentar ambos, mesmo se uma liberação falhar.
        auto_ok = self.clicker.desligar()
        drop_ok = self.drop.parar()
        combo_ok = self.combo.parar() if self.combo is not None else True
        return auto_ok and drop_ok and combo_ok

    def selecionar(self, aba):
        self.parar()
        self.aba = aba

    def comando(self, comando):
        if comando == "parar":
            self.parar()
        elif comando == "alternar":
            if self.aba == "LK Combo" and self.combo is not None:
                if self.combo.ligado:
                    self.combo.parar()
                elif self.clicker.desligar() and self.drop.parar():
                    self.combo.iniciar()
            elif self.aba == "Auto Click":
                if self.drop.parar() and (self.combo is None or self.combo.parar()):
                    self.clicker.alternar()
            elif self.drop.ligado:
                self.drop.parar()
            elif self.clicker.desligar() and (self.combo is None or self.combo.parar()):
                self.drop.iniciar()
        elif comando in ("box", "ground") and self.aba == "LK Drop":
            self.drop.marcar(comando)
