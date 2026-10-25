"""Seletor visual de um único botão; não emite entradas de mouse."""
import tkinter as tk

from PIL import Image, ImageChops, ImageDraw, ImageTk


class MouseSelector:
    def __init__(self, parent, command=None):
        self.command = command
        self._valor = "Esquerdo"
        self._disabled = False
        self.canvas = tk.Canvas(parent, width=220, height=130,
                                bg="#242424", highlightthickness=1,
                                highlightbackground="#242424",
                                takefocus=True, cursor="hand2")
        self._imagem = self.canvas.create_image(110, 54)
        self._areas = {"Esquerdo": "left", "Direito": "right"}
        self._textos = {}
        for nome, x, box in (("Esquerdo", 31, (71, 5, 108, 51)),
                             ("Direito", 189, (112, 5, 149, 51))):
            tag = "botao_" + nome
            # Áreas transparentes mantêm a seleção clicável sobre a imagem.
            self.canvas.create_rectangle(*box, fill="", outline="", tags=tag)
            self._textos[nome] = self.canvas.create_text(
                x, 35, text=nome, font=("Segoe UI", 9), tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda event, valor=nome: self._escolher(valor))
        self._legenda = self.canvas.create_text(
            110, 120, text="", fill="#aab5bf", font=("Segoe UI", 9))
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
        if 70 <= event.x <= 150 and 4 <= event.y <= 52:
            self._escolher("Esquerdo" if event.x < 110 else "Direito")

    @staticmethod
    def renderizar_mouse(valor):
        """Rasterizar em 4x e reduzir suaviza o contorno no Tk/Windows."""
        escala = 4
        imagem = Image.new("RGB", (220 * escala, 108 * escala), "#242424")
        desenho = ImageDraw.Draw(imagem)
        corpo = (70 * escala, 4 * escala, 150 * escala, 104 * escala)
        mascara = Image.new("L", imagem.size)
        ImageDraw.Draw(mascara).rounded_rectangle(corpo, radius=38 * escala, fill=255)
        imagem.paste("#30363e", mask=mascara)
        metade = Image.new("L", imagem.size)
        x1, x2 = (70, 109) if valor == "Esquerdo" else (111, 150)
        ImageDraw.Draw(metade).rectangle((x1 * escala, 4 * escala,
                                         x2 * escala, 51 * escala), fill=255)
        imagem.paste("#20523f", mask=ImageChops.multiply(mascara, metade))
        desenho.rounded_rectangle(corpo, radius=38 * escala,
                                  outline="#687480", width=escala)
        desenho.line((70 * escala, 52 * escala, 150 * escala, 52 * escala),
                      fill="#687480", width=escala)
        desenho.line((110 * escala, 5 * escala, 110 * escala, 52 * escala),
                      fill="#242424", width=2 * escala)
        desenho.rounded_rectangle((106 * escala, 19 * escala, 114 * escala, 36 * escala),
                                  radius=4 * escala, fill="#a7b3be")
        return imagem.resize((220, 108), Image.Resampling.LANCZOS)

    def _desenhar(self):
        self._foto = ImageTk.PhotoImage(self.renderizar_mouse(self._valor), master=self.canvas)
        self.canvas.itemconfigure(self._imagem, image=self._foto)
        for nome, texto in self._textos.items():
            self.canvas.itemconfigure(texto,
                                      fill="#45d99a" if nome == self._valor else "#aab5bf")
        self.canvas.itemconfigure(self._legenda,
                                  text=f"Botão {self._valor.lower()}" +
                                  (" • em uso" if self._disabled else " selecionado"))
