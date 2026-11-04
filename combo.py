"""Motor do combo DL/BK, executado exclusivamente pela thread Tk.

Nao envia movimento do mouse nem segura o botao direito.
Apenas as teclas 1,2,3 sao pressionadas e liberadas; F8 para tudo.
"""
import time


LIMITES = {
    "combo_toque_ms": (0, 200),
    "combo_intervalo_ms": (0, 200),
    "combo_apos3_ms": (0, 100),
    "combo_recarga_ms": (0, 15000),
}


def validar_combo(config):
    for chave, (minimo, maximo) in LIMITES.items():
        valor = config[chave]
        if type(valor) is not int or not minimo <= valor <= maximo:
            raise ValueError(f"{chave}: use inteiro de {minimo} a {maximo} ms.")
    if type(config["combo_recarga_ativa"]) is not bool:
        raise ValueError("combo_recarga_ativa deve ser verdadeiro/falso.")


class LKCombo:
    def __init__(self, scheduler, entrada, janela_propria, config):
        self.scheduler, self.entrada = scheduler, entrada
        self.janela_propria = janela_propria
        self.config = dict(config)
        self.ligado = False
        self.geracao = 0
        self.pendentes = set()
        self.alvo = None
        self.pressionada = None
        self.terceira_liberada_em = 0.0
        self.ciclos = 0
        self.status = "Configure os tempos e pressione F6 no jogo."

    def configurar(self, config):
        if self.ligado:
            raise RuntimeError("Pare o combo antes de alterar os valores.")
        validar_combo(config)
        self.config = dict(config)

    def parar(self, mensagem="Parado. F6 inicia / F8 para tudo."):
        self.ligado = False
        self.geracao += 1
        for identificador in tuple(self.pendentes):
            self.scheduler.after_cancel(identificador)
        self.pendentes.clear()
        if self.pressionada is not None:
            tecla = self.pressionada
            try:
                self.entrada.tecla_up(tecla)
            except Exception as erro:
                self.status = f"Erro ao liberar tecla {tecla}: {erro}. Use F8."
                return False
            self.pressionada = None
        self.status = mensagem
        return True

    def iniciar(self):
        if not self.parar():
            return False
        try:
            validar_combo(self.config)
            self.alvo = self.entrada.foco()
            if not self.alvo or self.alvo == self.janela_propria():
                self.status = "Entre no jogo e pressione F6."
                return False
            self.ligado, self.ciclos = True, 0
            self.status = "Combo executando. F8 para."
            self._pressionar("1", self.geracao)
            return True
        except Exception as erro:
            self.parar(f"Falha ao iniciar: {erro}")
            return False

    def _agendar(self, espera_ms, acao, geracao):
        def callback():
            self.pendentes.discard(identificador)
            if not self.ligado or self.geracao != geracao:
                return
            try:
                if self.entrada.foco() != self.alvo:
                    self.parar("Pausado: saiu da janela do jogo.")
                else:
                    acao()
            except Exception as erro:
                self.parar(f"Erro no combo: {erro}")
        identificador = self.scheduler.after(max(1, int(espera_ms)), callback)
        self.pendentes.add(identificador)

    def _pressionar(self, tecla, geracao):
        if not self.ligado or geracao != self.geracao:
            return
        self.pressionada = tecla  # registra antes da entrada: pode falhar apos pressionar
        self.entrada.tecla_down(tecla)
        self._agendar(self.config["combo_toque_ms"],
                      lambda: self._soltar(tecla, geracao), geracao)

    def _soltar(self, tecla, geracao):
        self.entrada.tecla_up(tecla)
        self.pressionada = None
        if tecla == "1" and self.config["combo_recarga_ativa"] and self.ciclos:
            restante = self.config["combo_recarga_ms"] - int(
                (time.monotonic() - self.terceira_liberada_em) * 1000
            )
            self._agendar(max(0, restante), lambda: self._pressionar("2", geracao), geracao)
        elif tecla == "1":
            self._agendar(self.config["combo_intervalo_ms"],
                          lambda: self._pressionar("2", geracao), geracao)
        elif tecla == "2":
            self._agendar(self.config["combo_intervalo_ms"],
                          lambda: self._pressionar("3", geracao), geracao)
        elif tecla == "3":
            self.ciclos += 1
            self.terceira_liberada_em = time.monotonic()
            self.status = f"Combo ativo: {self.ciclos} ciclos · F8 para"
            espera = self.config["combo_apos3_ms"]
            self._agendar(espera, lambda: self._pressionar("1", geracao), geracao)
