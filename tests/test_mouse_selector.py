import unittest
from unittest.mock import Mock, patch

from mouse_selector import MouseSelector


class TestMouseSelector(unittest.TestCase):
    def setUp(self):
        self.backend = patch("mouse_selector.tk.Canvas")
        self.canvas = self.backend.start().return_value
        self.addCleanup(self.backend.stop)
        self.callback = Mock()
        self.selector = MouseSelector(Mock(), command=self.callback)

    def test_selecao_exclusiva_sem_ativar_automacao(self):
        self.assertEqual(self.selector.get(), "Esquerdo")
        self.selector._escolher("Direito")
        self.assertEqual(self.selector.get(), "Direito")
        self.callback.assert_called_once_with("Direito")
        self.selector._escolher("Direito")
        self.callback.assert_called_once()

    def test_bloqueio_durante_execucao(self):
        self.selector.configure(state="disabled")
        self.selector._escolher("Direito")
        self.assertEqual(self.selector.get(), "Esquerdo")
        self.callback.assert_not_called()
        self.selector.configure(state="readonly")
        self.selector._escolher("Direito")
        self.callback.assert_called_once_with("Direito")

    def test_restaura_preferencia_sem_callback(self):
        self.selector.set("Direito")
        self.assertEqual(self.selector.get(), "Direito")
        self.callback.assert_not_called()

    def test_alvos_visuais_e_teclado(self):
        alvos = self.canvas.tag_bind.call_args_list
        self.assertEqual(len(alvos), 2)
        alvos[1].args[2](Mock())
        self.assertEqual(self.selector.get(), "Direito")
        teclas = {c.args[0]: c.args[1] for c in self.canvas.bind.call_args_list}
        teclas["<Left>"](Mock())
        self.assertEqual(self.selector.get(), "Esquerdo")
        teclas["<Right>"](Mock())
        self.assertEqual(self.selector.get(), "Direito")
