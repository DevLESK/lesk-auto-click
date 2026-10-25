import importlib.util
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import Mock, patch, call

# Carregar com backend simulado: nunca importar/acionar o mouse real.
mouse = Mock()
class FailSafeException(Exception):
    pass
mouse.FailSafeException = FailSafeException
spec = importlib.util.spec_from_file_location("clicker_em_teste", Path(__file__).resolve().parents[1] / "clicker.py")
modulo = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"pyautogui": mouse}):
    spec.loader.exec_module(modulo)
AutoClicker = modulo.AutoClicker


class TestClicker(unittest.TestCase):
    def setUp(self):
        mouse.reset_mock(side_effect=True, return_value=True)
        mouse.FailSafeException = FailSafeException
        self.clicker = AutoClicker()

    def tearDown(self):
        mouse.mouseUp.side_effect = None
        self.clicker.parar()

    def test_inicia_desligado(self):
        self.clicker._passo()
        mouse.click.assert_not_called()
        mouse.mouseDown.assert_not_called()

    def test_dois_botoes_repetidos(self):
        for botao in ("left", "right"):
            self.clicker.configurar(botao, "repetir")
            self.clicker.ligar()
            self.clicker._passo()
            mouse.mouseDown.assert_called_with(button=botao, _pause=False)
            mouse.mouseUp.assert_called_with(button=botao, _pause=False)
            self.clicker.desligar()
        mouse.click.assert_not_called()

    def test_dois_botoes_pressionados_uma_vez(self):
        for botao in ("left", "right"):
            mouse.reset_mock()
            self.clicker.configurar(botao, "pressionar")
            self.clicker.alternar()
            for _ in range(5):
                self.clicker._passo()
            mouse.mouseDown.assert_called_once_with(button=botao, _pause=False)
            self.clicker.alternar()
            mouse.mouseUp.assert_called_once_with(button=botao, _pause=False)
            mouse.click.assert_not_called()

    def test_parada_e_fechamento(self):
        self.clicker.configurar("right", "pressionar")
        self.clicker.ligar()
        self.clicker._passo()
        self.assertTrue(self.clicker.parar())
        self.clicker.ligar()
        self.clicker._passo()
        mouse.mouseDown.assert_called_once()
        mouse.mouseUp.assert_called_once()
        self.assertFalse(self.clicker.ligado)

    def test_falha_depois_de_pressionar_libera(self):
        self.clicker.configurar("right", "pressionar")
        mouse.mouseDown.side_effect = RuntimeError("falha simulada")
        self.clicker.ligar()
        self.clicker._passo()
        self.assertFalse(self.clicker.ligado)
        self.assertIn("falha simulada", self.clicker.erro)
        mouse.mouseUp.assert_called_once()

    def test_failsafe_nao_impede_liberacao(self):
        self.clicker.configurar("right", "pressionar")
        self.clicker.ligar()
        self.clicker._passo()
        mouse.mouseUp.side_effect = FailSafeException()
        mouse.position.return_value = (0, 0)
        self.assertTrue(self.clicker.desligar())
        mouse.platformModule._mouseUp.assert_called_once_with(0, 0, "right")

    def test_falha_liberacao_pode_ser_retentada(self):
        self.clicker.configurar("right", "pressionar")
        self.clicker.ligar()
        self.clicker._passo()
        mouse.mouseUp.side_effect = RuntimeError("indisponível")
        self.assertFalse(self.clicker.desligar())
        self.assertEqual(self.clicker._pressionado, "right")
        mouse.mouseUp.side_effect = None
        self.assertTrue(self.clicker.desligar())
        self.assertIsNone(self.clicker._pressionado)

    def test_bloqueia_troca_ativa(self):
        self.clicker.ligar()
        with self.assertRaises(RuntimeError):
            self.clicker.configurar("right", "pressionar")

    def test_intervalos_invalidos(self):
        for valor in (0, -1, True, "a", float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                self.clicker.definir_intervalo(valor)

    def test_alternancia_rapida(self):
        self.clicker.configurar("right", "pressionar")
        for _ in range(100):
            self.clicker.alternar()
            self.clicker._passo()
            self.clicker.alternar()
            self.clicker._passo()
        self.assertEqual(mouse.mouseDown.call_count, 100)
        self.assertEqual(mouse.mouseUp.call_count, 100)
        self.assertIsNone(self.clicker._pressionado)

    def test_parada_serializada_com_pressao_em_andamento(self):
        entrou = threading.Event()
        liberar = threading.Event()
        def pressionar(**kwargs):
            entrou.set()
            self.assertTrue(liberar.wait(2))
        mouse.mouseDown.side_effect = pressionar
        self.clicker.configurar("right", "pressionar")
        self.clicker.ligar()
        self.clicker.iniciar()
        self.assertTrue(entrou.wait(2))
        parada = threading.Thread(target=self.clicker.parar)
        parada.start()
        liberar.set()
        parada.join(2)
        self.assertFalse(parada.is_alive())
        mouse.mouseUp.assert_called_once()
        self.assertFalse(self.clicker._thread.is_alive())

    def test_iniciar_idempotente(self):
        self.clicker.iniciar()
        thread = self.clicker._thread
        self.clicker.iniciar()
        self.assertIs(thread, self.clicker._thread)
        self.clicker.parar()
        self.assertFalse(thread.is_alive())

    def test_clique_repetido_tem_pressao_curta_e_libera(self):
        self.clicker.ligar()
        with patch.object(self.clicker._encerrar, "wait") as espera:
            intervalo = self.clicker._passo()
        espera.assert_called_once_with(0.05)
        self.assertEqual(intervalo, 0.05)
        self.assertEqual(mouse.mock_calls, [
            call.mouseDown(button="left", _pause=False),
            call.mouseUp(button="left", _pause=False)])
        self.assertIsNone(self.clicker._pressionado)

    def test_falha_no_clique_repetido_tenta_soltar(self):
        mouse.mouseDown.side_effect = RuntimeError("falha no clique")
        self.clicker.ligar()
        self.clicker._passo()
        self.assertFalse(self.clicker.ligado)
        mouse.mouseUp.assert_called_once_with(button="left", _pause=False)
