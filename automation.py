"""Coordenação na thread Tk: uma automação por vez e um destino dos atalhos."""


class Automations:
    def __init__(self, clicker, drop):
        self.clicker, self.drop = clicker, drop
        self.aba = "Auto Click"

    def parar(self):
        # Sempre tentar ambos, mesmo se uma liberação falhar.
        auto_ok = self.clicker.desligar()
        drop_ok = self.drop.parar()
        return auto_ok and drop_ok

    def selecionar(self, aba):
        self.parar()
        self.aba = aba

    def comando(self, comando):
        if comando == "parar":
            self.parar()
        elif comando == "alternar":
            if self.aba == "Auto Click":
                if self.drop.parar():
                    self.clicker.alternar()
            elif self.drop.ligado:
                self.drop.parar()
            elif self.clicker.desligar():
                self.drop.iniciar()
        elif comando in ("box", "ground") and self.aba == "LK Drop":
            self.drop.marcar(comando)
