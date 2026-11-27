"""Testes S02.1: instrumentação é opcional e não altera entradas simuladas."""
import csv
import os
import tempfile
import unittest
from unittest.mock import patch

import combo
from combo import LKCombo
from combo_diagnostico import DiagnosticoCombo
from test_combo_timing_diagnostic import CONFIG, RelogioAgendador, EntradaSimulada


class InstrumentacaoTests(unittest.TestCase):
    def setUp(self):
        self.agenda = RelogioAgendador()
        self.entrada = EntradaSimulada(self.agenda)
        self.clock = lambda: self.agenda.agora_ms * 1000000
        p = patch.object(combo.time, "monotonic", lambda: self.agenda.agora_ms / 1000)
        p.start()
        self.addCleanup(p.stop)

    def criar(self, diagnostico=None, **config):
        return LKCombo(self.agenda, self.entrada, lambda: 99,
                       {**CONFIG, **config}, diagnostico=diagnostico)

    def test_desligado_por_padrao_sem_mudar_sequencia(self):
        motor = self.criar()
        self.assertIsNone(motor.diagnostico)
        self.assertTrue(motor.iniciar())
        self.agenda.avancar(6)
        self.assertEqual([(t, tecla) for t, acao, tecla in self.entrada.eventos
                          if acao == "down"],
                         [(0, "1"), (10, "2"), (20, "3"), (35, "1")])
        self.assertTrue(motor.parar())

    def test_eventos_esperados_e_desvio_de_callback(self):
        diag = DiagnosticoCombo(relogio_ns=self.clock)
        motor = self.criar(diag)
        self.assertTrue(motor.iniciar())
        self.agenda.avancar(6, {6: 20})
        self.assertEqual(
            [e["tecla"] for e in diag.eventos if e["evento"] == "tecla_down"],
            ["1", "2", "3", "1"]
        )
        self.assertEqual(
            [e["tecla"] for e in diag.eventos if e["evento"] == "tecla_up"],
            ["1", "2", "3"]
        )
        self.assertEqual(
            [e["atraso_ms"] for e in diag.eventos if e["evento"] == "callback"],
            [0, 0, 0, 0, 0, 20]
        )
        self.assertTrue(motor.parar())
        self.assertFalse(self.entrada.pressionadas)

    def test_mesmas_entradas_com_e_sem_diagnostico(self):
        def executar(usar_diag, recarga):
            agenda = RelogioAgendador()
            entrada = EntradaSimulada(agenda)
            diag = DiagnosticoCombo(relogio_ns=lambda: agenda.agora_ms * 1000000) if usar_diag else None
            motor = LKCombo(agenda, entrada, lambda: 99,
                           {**CONFIG, "combo_recarga_ativa": recarga},
                           diagnostico=diag)
            self.assertTrue(motor.iniciar())
            agenda.avancar(8, {5: 20})
            motor.parar()
            self.assertFalse(entrada.pressionadas)
            return entrada.eventos
        for recarga in (False, True):
            with self.subTest(recarga=recarga):
                self.assertEqual(executar(False, recarga), executar(True, recarga))

    def test_parada_e_perda_de_foco(self):
        for falha_foco in (False, True):
            with self.subTest(falha_foco=falha_foco):
                self.setUp()
                diag = DiagnosticoCombo(relogio_ns=self.clock)
                motor = self.criar(diag)
                motor.iniciar()
                if falha_foco:
                    self.entrada.alvo = 77
                    self.agenda.passo()
                    self.assertFalse(motor.ligado)
                else:
                    self.assertTrue(motor.parar())
                self.assertFalse(self.entrada.pressionadas)
                self.assertFalse(self.agenda.pendentes)

    def test_callbacks_obsoletos_nao_geram_evento(self):
        diag = DiagnosticoCombo(relogio_ns=self.clock)
        motor = self.criar(diag)
        motor.iniciar()
        antigos = [f for _, f in self.agenda.pendentes.values()]
        motor.parar()
        motor.iniciar()
        antes = len(diag.eventos)
        for callback in antigos:
            callback()
        self.assertEqual(len(diag.eventos), antes)
        motor.parar()

    def test_limite_memoria_e_exportacao_explicita(self):
        diag = DiagnosticoCombo(limite=2, relogio_ns=lambda: 123)
        for tecla in ("1", "2", "3"):
            diag.registrar("tecla_down", tecla)
        self.assertEqual(len(diag.eventos), 2)
        self.assertEqual(diag.descartados, 1)
        with tempfile.TemporaryDirectory() as pasta:
            destino = os.path.join(pasta, "combo_diagnostico.csv")
            diag.exportar_csv(destino)
            with open(destino, encoding="utf-8", newline="") as arq:
                linhas = list(csv.DictReader(arq))
            self.assertEqual([e["tecla"] for e in linhas], ["2", "3"])
            self.assertEqual(list(linhas[0]), list(DiagnosticoCombo.CAMPOS))

    def test_erro_da_telemetria_nao_interrompe_motor(self):
        class ColetorFalho:
            def registrar(self, *args, **kwargs):
                raise RuntimeError("falha proposital")
            def relogio_ns(self):
                raise RuntimeError("falha proposital")
        motor = self.criar(ColetorFalho())
        self.assertTrue(motor.iniciar())
        self.agenda.avancar(6)
        self.assertTrue(motor.ligado)
        self.assertTrue(motor.parar())
        self.assertFalse(self.entrada.pressionadas)


if __name__ == "__main__":
    unittest.main()
