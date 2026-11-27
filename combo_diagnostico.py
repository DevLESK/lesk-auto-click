"""Coletor opcional e limitado de eventos do Combo DL.

Não captura teclado global, identificador do PC, licença ou janela.
Nenhuma gravação em disco acontece no ciclo de execução.
"""
import csv
import time
from collections import deque


class DiagnosticoCombo:
    CAMPOS = ("tempo_ns", "evento", "tecla", "espera_ms", "atraso_ms")

    def __init__(self, limite=20000, relogio_ns=None):
        if type(limite) is not int or not 1 <= limite <= 100000:
            raise ValueError("limite deve estar entre 1 e 100000")
        self.relogio_ns = relogio_ns or time.perf_counter_ns
        self.eventos = deque(maxlen=limite)
        self.descartados = 0

    def registrar(self, evento, tecla="", espera_ms=None, atraso_ms=None):
        if len(self.eventos) == self.eventos.maxlen:
            self.descartados += 1
        self.eventos.append({
            "tempo_ns": self.relogio_ns(),
            "evento": evento,
            "tecla": tecla,
            "espera_ms": espera_ms,
            "atraso_ms": atraso_ms,
        })

    def exportar_csv(self, caminho):
        """Chamar com o combo parado; nunca dentro de callback do motor."""
        with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=self.CAMPOS)
            writer.writeheader()
            writer.writerows(self.eventos)
