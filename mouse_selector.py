"""Seletor visual de um único botão; não emite entradas de mouse."""
import math
import tkinter as tk


class MouseSelector:
    def __init__(self, parent, command=None):
        self.command = command
        self._valor = "Esquerdo"
        self._disabled = False
        self.canvas = tk.Canvas(parent, width=240, height=198,
                                bg="#242424", highlightthickness=0,
                                takefocus=True, cursor="hand2")
        # Corpo arredondado do mouse, com dois alvos independentes na parte superior.
        self.canvas.create_polygon(
            50, 80, 50, 45, 78, 10, 120, 10, 162, 10, 190, 45,
            190, 80, 190, 136, 170, 178, 120, 184, 70, 178, 50, 136,
            smooth=True, fill="#303438", outline="#626970", width=2)
        self._areas = {}
        self._textos = {}
        for nome, inicio, fim, x in (("Esquerdo", -180, -90, 84),
                                     ("Direito", -90, 0, 156)):
            arco = []
            for graus in range(inicio, fim + 1, 5):
                angulo = math.radians(graus)
                arco.extend((120 + 66 * math.cos(angulo),
                             76 + 62 * math.sin(angulo)))
            if nome == "Esquerdo":
                pontos = arco + [116, 96, 54, 96]
            else:
                pontos = arco + [186, 96, 124, 96]
            tag = "botao_" + nome
            self._areas[nome] = self.canvas.create_polygon(
                *pontos, fill="#363c42", outline="#626970", width=2, tags=tag)
            self._textos[nome] = self.canvas.create_text(
                x, 63, text=nome, font=("Segoe UI", 10, "bold"), tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda event, valor=nome: self._escolher(valor))
        self.canvas.create_rectangle(116, 34, 124, 58, fill="#a7adb3", outline="")
        self._legenda = self.canvas.create_text(
            120, 140, text="", fill="#dce1e5", font=("Segoe UI", 10))
        self.canvas.bind("<Left>", lambda event: self._escolher("Esquerdo"))
        self.canvas.bind("<Right>", lambda event: self._escolher("Direito"))
        self.canvas.bind("<FocusIn>", lambda event: self.canvas.configure(
            highlightthickness=1, highlightbackground="#39FF14"))
        self.canvas.bind("<FocusOut>", lambda event: self.canvas.configure(
            highlightthickness=0))
        self._desenhar()

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def get(self):
        return self._valor

    def set(self, valor):
        if valor not in self._areas:
            raise ValueError("Botão inválido")
        self._valor = valor
        self._desenhar()

    def configure(self, state=None, command=None):
        if command is not None:
            self.command = command
        if state is not None:
            self._disabled = state == "disabled"
            self.canvas.configure(cursor="arrow" if self._disabled else "hand2")
            self._desenhar()

    def _escolher(self, valor):
        if self._disabled:
            return
        self.canvas.focus_set()
        if valor == self._valor:
            return
        self.set(valor)
        if self.command:
            self.command(valor)

    def _desenhar(self):
        for nome, area in self._areas.items():
            selecionado = nome == self._valor
            self.canvas.itemconfigure(area, fill="#39FF14" if selecionado else "#363c42")
            self.canvas.itemconfigure(self._textos[nome],
                                      fill="#102008" if selecionado else "#dce1e5")
        self.canvas.itemconfigure(self._legenda,
                                  text=self._valor + (" • em uso" if self._disabled else " • selecionado"))
