"""Seletor visual de um único botão; não emite entradas de mouse."""
import tkinter as tk
import sys
from pathlib import Path
from functools import lru_cache

from PIL import Image, ImageTk


class MouseSelector:
    def __init__(self, parent, command=None):
        self.command = command
        self._valor = "Esquerdo"
        self._disabled = False
        self.canvas = tk.Canvas(parent, width=220, height=180,
                                bg="#242424", highlightthickness=1,
                                highlightbackground="#242424",
                                takefocus=True, cursor="hand2")
        self._imagem = self.canvas.create_image(110, 90)
        self._areas = {"Esquerdo": "left", "Direito": "right"}
        self._textos = {}
        for nome, x, box in (("Esquerdo", 31, (57, 6, 106, 92)),
                             ("Direito", 189, (114, 6, 163, 92))):
            tag = "botao_" + nome
            # Áreas transparentes mantêm a seleção clicável sobre a imagem.
            self.canvas.create_rectangle(*box, fill="", outline="", tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda event, valor=nome: self._escolher(valor))
        # O Canvas não detecta o interior de retângulos sem preenchimento:
        # testar as coordenadas também garante toda a metade superior clicável.
        self.canvas.bind("<Button-1>", self._clicar_imagem)
        self.canvas.bind("<Left>", lambda event: self._escolher("Esquerdo"))
        self.canvas.bind("<Right>", lambda event: self._escolher("Direito"))
        self.canvas.bind("<FocusIn>", lambda event: self.canvas.configure(
            highlightthickness=1, highlightbackground="#39FF14"))
        self.canvas.bind("<FocusOut>", lambda event: self.canvas.configure(
            highlightthickness=1, highlightbackground="#242424"))
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

    def _clicar_imagem(self, event):
        if 57 <= event.x <= 163 and 6 <= event.y <= 92:
            self._escolher("Esquerdo" if event.x < 110 else "Direito")

    @staticmethod
    @lru_cache(maxsize=2)
    def renderizar_mouse(valor):
        arquivos = {"Esquerdo": "mouse_left.png", "Direito": "mouse_right.png"}
        if valor not in arquivos:
            raise ValueError("Botão inválido")
        raiz = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        with Image.open(raiz / "assets" / arquivos[valor]) as original:
            arte = original.convert("RGBA")
            # Aproveitar a área visual removendo apenas margens transparentes.
            caixa = arte.getchannel("A").getbbox()
            if caixa:
                arte = arte.crop(caixa)
        arte.thumbnail((144, 176), Image.Resampling.LANCZOS)
        imagem = Image.new("RGB", (220, 180), "#242424")
        imagem.paste(arte, ((220 - arte.width) // 2, (180 - arte.height) // 2), arte)
        return imagem

    def _desenhar(self):
        self._foto = ImageTk.PhotoImage(self.renderizar_mouse(self._valor), master=self.canvas)
        self.canvas.itemconfigure(self._imagem, image=self._foto)
        for nome, texto in self._textos.items():
            self.canvas.itemconfigure(texto,
                                      fill="#45d99a" if nome == self._valor else "#aab5bf")
