"""Seletor visual de um único botão; não emite entradas de mouse."""
import math
import tkinter as tk


class MouseSelector:
    def __init__(self, parent, command=None):
        self.command = command
        self._valor = "Esquerdo"
        self._disabled = False
        self.canvas = tk.Canvas(parent, width=220, height=136,
                                bg="#242424", highlightthickness=0,
                                takefocus=True, cursor="hand2")
        # Silhueta compacta: topo arredondado, laterais e base contínuas.
        self.canvas.create_polygon(
            66, 43, 66, 18, 86, 5, 110, 5, 134, 5, 154, 18,
            154, 43, 154, 87, 148, 113, 130, 125, 110, 128,
            90, 125, 72, 113, 66, 87,
            smooth=True, fill="#2c3035", outline="#555e68", width=2)
        self._areas = {}
        self._textos = {}
        for nome, inicio, fim, x in (("Esquerdo", -180, -90, 30),
                                     ("Direito", -90, 0, 190)):
            arco = []
            for graus in range(inicio, fim + 1, 5):
                angulo = math.radians(graus)
                arco.extend((110 + 40 * math.cos(angulo),
                             43 + 34 * math.sin(angulo)))
            if nome == "Esquerdo":
                pontos = arco + [107, 58, 70, 58]
            else:
                pontos = arco + [150, 58, 113, 58]
            tag = "botao_" + nome
            self._areas[nome] = self.canvas.create_polygon(
                *pontos, fill="#353a41", outline="#555e68", width=1, tags=tag)
            self._textos[nome] = self.canvas.create_text(
                x, 43, text=nome, font=("Segoe UI", 9), tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda event, valor=nome: self._escolher(valor))
        # Rodinha e divisão dos botões; não são alvos de automação.
        self.canvas.create_line(110, 13, 110, 60, fill="#242424", width=3)
        self.canvas.create_polygon(106, 23, 114, 23, 114, 41, 106, 41,
                                   smooth=True, fill="#909aa5", outline="")
        self._legenda = self.canvas.create_text(
            110, 88, text="", fill="#9aa5b1", font=("Segoe UI", 8))
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
            self.canvas.itemconfigure(area, fill="#194a38" if selecionado else "#353a41",
                                      outline="#45d99a" if selecionado else "#555e68")
            self.canvas.itemconfigure(self._textos[nome],
                                      fill="#45d99a" if selecionado else "#9aa5b1")
        self.canvas.itemconfigure(self._legenda,
                                  text="EM USO" if self._disabled else "SELECIONE")
