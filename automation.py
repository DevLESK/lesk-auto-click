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

    def _alternar_botao(self, botao):
        """Atalho dedicado: solta o anterior antes de ligar o novo."""
        ligado, _erro = self.clicker.estado()
        if ligado and self.clicker.botao == botao:
            return self.clicker.desligar()
        if not self.parar():
            return False
        # Modo repetir/pressionar e velocidade configurados no painel nao mudam.
        self.clicker.configurar(botao, self.clicker.modo)
        self.clicker.ligar()
        return True

    def comando(self, comando):
        if comando in ("esquerdo", "direito"):
            if self.aba == "Auto Click":
                return self._alternar_botao("left" if comando == "esquerdo" else "right")
            # F6 continua a alternar a funcao da aba Drop ou Combo.
            # F8 e dedicado ao direito: fora da aba Auto Click nao faz nada.
            return self.comando("alternar") if comando == "esquerdo" else False
        if comando == "parar":
            return self.parar()
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
