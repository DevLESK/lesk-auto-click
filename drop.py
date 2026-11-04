"""Motor LK Drop. Todas as chamadas são feitas pela thread da interface."""


class LKDrop:
    def __init__(self, scheduler, entrada, janela_propria, intervalo=50, recolher=True):
        self.scheduler, self.entrada = scheduler, entrada
        self.janela_propria = janela_propria
        self.intervalo, self.recolher = intervalo, recolher
        self.pontos, self.alvo = {}, None
        self.ligado, self.geracao, self.ciclos = False, 0, 0
        self.mouse_preso = self.espaco_preso = False
        self.pendentes = set()
        self.status = "F2 marca a box · F3 marca o chão"

    def marcar(self, ponto):
        if self.ligado or ponto not in ("box", "ground"):
            return
        try:
            alvo = self.entrada.foco()
            if not alvo or alvo == self.janela_propria():
                self.status = "Marque o ponto com o jogo em primeiro plano."
                return
            posicao = self.entrada.posicao()
        except Exception as erro:
            self.status = "Não foi possível marcar: " + str(erro)
            return
        if alvo != self.alvo:
            self.pontos.clear()
        self.alvo = alvo
        self.pontos[ponto] = posicao
        self.status = "Ponto marcado. F6 inicia quando ambos estiverem prontos."

    def parar(self, mensagem="Parado — troque a pilha e use F6 para retomar."):
        self.ligado = False
        self.geracao += 1
        for identificador in self.pendentes:
            self.scheduler.after_cancel(identificador)
        self.pendentes.clear()
        erros = []
        for atributo, liberar in (("mouse_preso", self.entrada.mouse_up),
                                   ("espaco_preso", self.entrada.espaco_up)):
            if getattr(self, atributo):
                try:
                    liberar()
                    setattr(self, atributo, False)
                except Exception as erro:
                    erros.append(str(erro))
        self.status = "Erro ao liberar: use F8. " + "; ".join(erros) if erros else mensagem
        return not erros

    def iniciar(self):
        if not self.parar():
            return False
        if set(self.pontos) != {"box", "ground"}:
            self.status = "Marque a box com F2 e o chão com F3."
            return False
        if (type(self.intervalo) is not int or not 20 <= self.intervalo <= 5000):
            self.status = "Use intervalo inteiro entre 20 e 5000 ms."
            return False
        if self.entrada.foco() != self.alvo:
            self.status = "Volte ao jogo e pressione F6."
            return False
        self.ligado, self.ciclos = True, 0
        self.status = "Executando — F8 para parar."
        self._executar(0, self.geracao)
        return self.ligado

    def _agendar(self, ms, acao, token):
        def executar():
            self.pendentes.discard(identificador)
            # Verifique antes de qualquer entrada, inclusive liberações antigas.
            if token != self.geracao or not self.ligado:
                return
            try:
                if self.entrada.foco() != self.alvo:
                    self.parar("Pausado: saiu do jogo. F6 retoma.")
                else:
                    acao()
            except Exception as erro:
                self.parar("Erro: " + str(erro))
        identificador = self.scheduler.after(ms, executar)
        self.pendentes.add(identificador)

    def _executar(self, fase, token):
        try:
            if self.entrada.foco() != self.alvo:
                self.parar("Pausado: saiu do jogo. F6 retoma.")
                return
            if fase in (0, 2):
                self.entrada.mover(*self.pontos["box" if fase == 0 else "ground"])
            elif fase in (1, 3):
                self.mouse_preso = True
                self.entrada.mouse_down()
                self._agendar(100, lambda: self._soltar_mouse(fase, token), token)
                return
            elif fase == 4:
                if self.recolher:
                    self._recolher(5, token)
                else:
                    self._terminar_ciclo(token)
                return
            self._agendar(self.intervalo, lambda: self._executar(fase + 1, token), token)
        except Exception as erro:
            self.parar("Erro: " + str(erro))

    def _soltar_mouse(self, fase, token):
        self.entrada.mouse_up()
        self.mouse_preso = False
        self._agendar(self.intervalo, lambda: self._executar(fase + 1, token), token)

    def _recolher(self, restantes, token):
        self.espaco_preso = True
        self.entrada.espaco_down()
        self._agendar(180, lambda: self._soltar_espaco(restantes, token), token)

    def _soltar_espaco(self, restantes, token):
        self.entrada.espaco_up()
        self.espaco_preso = False
        if restantes > 1:
            self._agendar(180, lambda: self._recolher(restantes - 1, token), token)
        else:
            self._terminar_ciclo(token)

    def _terminar_ciclo(self, token):
        self.ciclos += 1
        self.status = f"Executando — {self.ciclos} ciclos · F8 para parar"
        self._agendar(self.intervalo, lambda: self._executar(0, token), token)
