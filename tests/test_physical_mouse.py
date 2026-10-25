import unittest
from unittest.mock import Mock
from physical_mouse import PhysicalMouseListener


class TestPhysicalMouse(unittest.TestCase):
    def test_distingue_botoes_fisicos(self):
        callback = Mock()
        listener = PhysicalMouseListener(callback)
        listener._receber(0x0201, 0)
        listener._receber(0x0204, 0)
        self.assertEqual([c.args[0] for c in callback.call_args_list], ["left", "right"])

    def test_ignora_eventos_injetados_e_solturas(self):
        callback = Mock()
        listener = PhysicalMouseListener(callback)
        for mensagem in (0x0201, 0x0204):
            listener._receber(mensagem, 1)
            listener._receber(mensagem, 3)
        for mensagem in (0x0200, 0x0202, 0x0205):
            listener._receber(mensagem, 0)
        callback.assert_not_called()

    def test_parada_antes_de_iniciar(self):
        PhysicalMouseListener(Mock()).stop()
