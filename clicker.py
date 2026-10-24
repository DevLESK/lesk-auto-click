import math
import threading

import pyautogui


class AutoClicker:
    def __init__(self, intervalo_clique=0.05, botao="left", modo="repetir"):
        self.ligado = False
        self.rodando = True
        self.intervalo_clique = intervalo_clique
        self.botao = botao
        self.modo = modo
        self.erro = None
        self._pressionado = None
        self._lock = threading.RLock()
        self._encerrar = threading.Event()
        self._thread = None
        self.definir_intervalo(intervalo_clique)
        self.configurar(botao, modo)

    def iniciar(self):
        with self._lock:
            if self.rodando and self._thread is None:
                self._thread = threading.Thread(target=self._clicar, daemon=True)
                self._thread.start()

    def _soltar(self):
        if self._pressionado is not None:
            # A liberação precisa funcionar mesmo com o cursor no canto de failsafe.
            try:
                pyautogui.mouseUp(button=self._pressionado, _pause=False)
            except pyautogui.FailSafeException:
                # Não desativar o failsafe globalmente. Somente liberar o botão
                # que esta instância pressionou, usando o backend já carregado.
                pyautogui.platformModule._mouseUp(
                    *pyautogui.position(), self._pressionado
                )
            self._pressionado = None

    def _passo(self):
        """Uma operação serializada; também permite testes sem cliques reais."""
        with self._lock:
            if not self.rodando or not self.ligado:
                return 0.05
            try:
                if self.modo == "pressionar":
                    if self._pressionado is None:
                        # Registrar antes: a chamada pode pressionar e depois falhar.
                        self._pressionado = self.botao
                        pyautogui.mouseDown(button=self.botao, _pause=False)
                    return 0.05
                pyautogui.click(button=self.botao, _pause=False)
                return self.intervalo_clique
            except Exception as exc:
                self.erro = str(exc) or type(exc).__name__
                self.ligado = False
                try:
                    self._soltar()
                except Exception as liberar_exc:
                    self.erro += f"; falha ao liberar: {liberar_exc}"
                return 0.05

    def _clicar(self):
        try:
            while not self._encerrar.is_set():
                self._encerrar.wait(self._passo())
        finally:
            self.desligar()

    def ligar(self):
        with self._lock:
            if self.rodando:
                self._soltar()
                self.erro = None
                self.ligado = True

    def desligar(self):
        with self._lock:
            self.ligado = False
            try:
                self._soltar()
            except Exception as exc:
                self.erro = f"Falha ao liberar botão: {exc}"
                return False
            return True

    def alternar(self):
        with self._lock:
            if self.ligado:
                self.desligar()
            else:
                self.ligar()

    def configurar(self, botao, modo):
        if botao not in ("left", "right") or modo not in ("repetir", "pressionar"):
            raise ValueError("Botão ou modo inválido")
        with self._lock:
            if self.ligado:
                raise RuntimeError("Desligue antes de mudar botão ou modo")
            self._soltar()
            self.botao, self.modo = botao, modo

    def definir_intervalo(self, intervalo):
        if (isinstance(intervalo, bool) or not isinstance(intervalo, (int, float))
                or not math.isfinite(intervalo) or intervalo <= 0):
            raise ValueError("Intervalo deve ser positivo e finito")
        with self._lock:
            self.intervalo_clique = intervalo

    def estado(self):
        with self._lock:
            return self.ligado, self.erro

    def parar(self):
        with self._lock:
            self.rodando = False
            liberado = self.desligar()
            self._encerrar.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join()
        return liberado
