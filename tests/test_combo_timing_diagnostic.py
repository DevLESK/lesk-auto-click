"""S02: diagnósticos determinísticos do LKCombo; não injeta teclas reais.

O relógio é virtual. Os atrasos abaixo são simulados e NÃO representam
medidas do Windows, do Tk ou do servidor MU.
"""
import unittest
from unittest.mock import patch

import combo
from combo import LKCombo


CONFIG = {
    "combo_toque_ms": 5,
    "combo_intervalo_ms": 5,
    "combo_apos3_ms": 10,
    "combo_recarga_ms": 10000,
    "combo_recarga_ativa": False,
}


class RelogioAgendador:
    """Executa callbacks no prazo simulado mais atraso adicional controlado."""

    def __init__(self):
        self.agora_ms = 0
        self.proximo_id = 0
        self.pendentes = {}
        self.historico = []
        self.cancelados = []

    def after(self, espera_ms, callback):
        self.proximo_id += 1
        identificador = self.proximo_id
        prazo = self.agora_ms + espera_ms
        self.pendentes[identificador] = (prazo, callback)
        self.historico.append((identificador, self.agora_ms, espera_ms, prazo))
        return identificador

    def after_cancel(self, identificador):
        if identificador in self.pendentes:
            self.cancelados.append(self.pendentes[identificador][1])
            del self.pendentes[identificador]

    def passo(self, atraso_ms=0):
        if not self.pendentes:
            raise AssertionError("Nenhum callback pendente")
        identificador = min(
            self.pendentes,
            key=lambda item: (self.pendentes[item][0], item),
        )
        prazo, callback = self.pendentes.pop(identificador)
        self.agora_ms = max(self.agora_ms, prazo) + atraso_ms
        callback()

    def avancar(self, quantidade, atrasos=None):
        atrasos = atrasos or {}
        for indice in range(1, quantidade + 1):
            self.passo(atrasos.get(indice, 0))


class EntradaSimulada:
    def __init__(self, relogio):
        self.relogio = relogio
        self.alvo = 42
        self.eventos = []
        self.pressionadas = set()

    def foco(self):
        return self.alvo

    def tecla_down(self, tecla):
        if tecla in self.pressionadas:
            raise AssertionError("Tecla pressionada em duplicidade")
        self.pressionadas.add(tecla)
        self.eventos.append((self.relogio.agora_ms, "down", tecla))

    def tecla_up(self, tecla):
        if tecla not in self.pressionadas:
            raise AssertionError("Soltura sem pressionamento")
        self.pressionadas.remove(tecla)
        self.eventos.append((self.relogio.agora_ms, "up", tecla))


class DiagnosticoComboDL(unittest.TestCase):
    def setUp(self):
        self.agenda = RelogioAgendador()
        self.entrada = EntradaSimulada(self.agenda)
        self.patch_relogio = patch.object(
            combo.time, "monotonic", lambda: self.agenda.agora_ms / 1000
        )
        self.patch_relogio.start()
        self.addCleanup(self.patch_relogio.stop)

    def iniciar(self, **ajustes):
        motor = LKCombo(
            self.agenda, self.entrada, lambda: 99, {**CONFIG, **ajustes}
        )
        self.assertTrue(motor.iniciar())
        return motor

    def pressao(self, tecla, ocorrencia=0):
        eventos = [t for t, acao, tcla in self.entrada.eventos
                   if acao == "down" and tcla == tecla]
        return eventos[ocorrencia]

    def eventos_down(self):
        return [(t, tecla) for t, acao, tecla in self.entrada.eventos
                if acao == "down"]

    def test_sequencia_1_2_3_1_sem_atraso(self):
        motor = self.iniciar()
        self.agenda.avancar(6)
        self.assertEqual(
            self.eventos_down()[:4],
            [(0, "1"), (10, "2"), (20, "3"), (35, "1")]
        )
        self.assertEqual(motor.ciclos, 1)
        self.assertEqual(self.entrada.pressionadas, {"1"})
        self.assertTrue(motor.parar())
        self.assertFalse(self.entrada.pressionadas)

    def test_varredura_atrasos_na_transicao_3_para_1(self):
        """Simula atraso no callback que seleciona 1 após liberar 3."""
        for atraso in (0, 5, 10, 20, 50):
            with self.subTest(atraso_ms=atraso):
                self.setUp()
                motor = self.iniciar()
                self.agenda.avancar(6, {6: atraso})
                liberacao_3 = next(
                    t for t, acao, tecla in self.entrada.eventos
                    if (acao, tecla) == ("up", "3")
                )
                retorno_1 = self.pressao("1", 1)
                self.assertEqual(liberacao_3, 25)
                self.assertEqual(retorno_1, 35 + atraso)
                self.assertEqual(
                    retorno_1 - liberacao_3, 10 + atraso
                )
                self.assertTrue(motor.parar())
                self.assertFalse(self.entrada.pressionadas)

    def test_atraso_ao_soltar_3_desloca_todo_o_retorno(self):
        for atraso in (0, 5, 10, 20, 50):
            with self.subTest(atraso_ms=atraso):
                self.setUp()
                motor = self.iniciar()
                self.agenda.avancar(6, {5: atraso})
                soltura_3 = next(
                    t for t, acao, tecla in self.entrada.eventos
                    if (acao, tecla) == ("up", "3")
                )
                self.assertEqual(soltura_3, 25 + atraso)
                self.assertEqual(self.pressao("1", 1), 35 + atraso)
                self.assertEqual(self.pressao("1", 1) - soltura_3, 10)
                self.assertTrue(motor.parar())

    def test_recarga_tem_sequencia_sem_duplicar_1(self):
        motor = self.iniciar(combo_recarga_ativa=True)
        self.agenda.avancar(8)
        self.assertEqual(
            self.eventos_down()[:5],
            [(0, "1"), (10, "2"), (20, "3"), (35, "1"),
             (10025, "2")]
        )
        self.assertTrue(motor.parar())
        self.assertFalse(self.entrada.pressionadas)

    def test_parada_durante_toque_e_durante_intervalo(self):
        for passos in (0, 1, 2, 3, 4, 5):
            with self.subTest(passos=passos):
                self.setUp()
                motor = self.iniciar()
                self.agenda.avancar(passos)
                self.assertTrue(motor.parar())
                self.assertFalse(self.entrada.pressionadas)
                self.assertFalse(self.agenda.pendentes)
                quantia = len(self.entrada.eventos)
                for callback in self.agenda.cancelados:
                    callback()
                self.assertEqual(len(self.entrada.eventos), quantia)

    def test_perda_de_foco_libera_tecla(self):
        motor = self.iniciar()
        self.entrada.alvo = 100
        self.agenda.passo(atraso_ms=50)
        self.assertFalse(motor.ligado)
        self.assertFalse(self.entrada.pressionadas)
        self.assertFalse(self.agenda.pendentes)

    def test_callback_antigo_nao_afeta_geracao_nova(self):
        motor = self.iniciar()
        antigos = [callback for _, callback in self.agenda.pendentes.values()]
        self.assertTrue(motor.parar())
        self.assertTrue(motor.iniciar())
        eventos_antes = list(self.entrada.eventos)
        for callback in antigos:
            callback()
        self.assertEqual(self.entrada.eventos, eventos_antes)
        self.assertEqual(self.entrada.pressionadas, {"1"})
        self.assertTrue(motor.parar())


if __name__ == "__main__":
    unittest.main()
