"""Seletor visual de um único botão; não emite entradas de mouse."""
import tkinter as tk

from PIL import Image, ImageDraw, ImageTk


class MouseSelector:
    def __init__(self, parent, command=None):
        self.command = command
        self._valor = "Esquerdo"
        self._disabled = False
        self.canvas = tk.Canvas(parent, width=220, height=110,
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
        if 70 <= event.x <= 150 and 4 <= event.y <= 52:
            self._escolher("Esquerdo" if event.x < 110 else "Direito")

    @staticmethod
    def renderizar_mouse(valor):
        """Rasterizar em 4x e reduzir suaviza o contorno no Tk/Windows."""
        escala = 4
        imagem = Image.new("RGB", (220 * escala, 108 * escala), "#242424")
        desenho = ImageDraw.Draw(imagem)

        def curva(inicio, trechos):
            pontos = [inicio]
            atual = inicio
            for c1, c2, fim in trechos:
                for passo in range(1, 33):
                    t = passo / 32
                    u = 1 - t
                    pontos.append((u**3 * atual[0] + 3*u*u*t*c1[0] +
                                   3*u*t*t*c2[0] + t**3*fim[0],
                                   u**3 * atual[1] + 3*u*u*t*c1[1] +
                                   3*u*t*t*c2[1] + t**3*fim[1]))
                atual = fim
            return [(round(x * escala), round(y * escala)) for x, y in pontos]

        corpo = curva((110, 4), [
            ((84, 4), (76, 15), (76, 37)),
            ((76, 57), (68, 72), (73, 87)),
            ((77, 102), (93, 105), (110, 105)),
            ((127, 105), (143, 102), (147, 87)),
            ((152, 72), (144, 57), (144, 37)),
            ((144, 15), (136, 4), (110, 4))])
        sombra = [(x, y + 2 * escala) for x, y in corpo]
        desenho.polygon(sombra, fill="#171b1e")
        desenho.polygon(corpo, fill="#2c3239")
        desenho.line(corpo + [corpo[0]], fill="#65717d", width=escala)
        esquerda = curva((107, 9), [
            ((87, 9), (81, 18), (81, 36)),
            ((81, 42), (80, 47), (79, 51)),
            ((86, 54), (98, 54), (107, 52)),
            ((107, 40), (107, 21), (107, 9))])
        direita = [(220 * escala - x, y) for x, y in esquerda]
        for nome, pontos in (("Esquerdo", esquerda), ("Direito", direita)):
            escolhido = nome == valor
            desenho.polygon(pontos, fill="#1d5c44" if escolhido else "#39434e")
            desenho.line(pontos + [pontos[0]],
                          fill="#45d99a" if escolhido else "#6c7b89", width=escala)
        desenho.rounded_rectangle((106*escala, 18*escala, 114*escala, 37*escala),
                                  radius=4*escala, fill="#141a20", outline="#6c7884", width=escala)
        desenho.rounded_rectangle((108*escala, 21*escala, 112*escala, 33*escala),
                                  radius=2*escala, fill="#a1acb7")
        # Detalhes discretos de pegada e encaixe, sem texto dentro do mouse.
        desenho.arc((78*escala, 61*escala, 142*escala, 98*escala),
                     start=12, end=168, fill="#414d58", width=escala)
        return imagem.resize((220, 108), Image.Resampling.LANCZOS)

    def _desenhar(self):
        self._foto = ImageTk.PhotoImage(self.renderizar_mouse(self._valor), master=self.canvas)
        self.canvas.itemconfigure(self._imagem, image=self._foto)
        for nome, texto in self._textos.items():
            self.canvas.itemconfigure(texto,
                                      fill="#45d99a" if nome == self._valor else "#aab5bf")
