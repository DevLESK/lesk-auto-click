import unittest
from unittest.mock import Mock, patch

from mouse_selector import MouseSelector


class TestMouseSelector(unittest.TestCase):
    def setUp(self):
        self.foto = patch("mouse_selector.ImageTk.PhotoImage", return_value=Mock())
        self.foto.start()
        self.addCleanup(self.foto.stop)
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

    def test_clique_dentro_da_imagem(self):
        self.selector._clicar_imagem(Mock(x=135, y=30))
        self.assertEqual(self.selector.get(), "Direito")
        self.selector._clicar_imagem(Mock(x=80, y=115))
        self.assertEqual(self.selector.get(), "Direito")

    def test_imagem_tem_selecao_e_contorno_suave(self):
        esquerda = MouseSelector.renderizar_mouse("Esquerdo")
        direita = MouseSelector.renderizar_mouse("Direito")
        self.assertEqual(esquerda.size, (220, 172))
        self.assertNotEqual(esquerda.getpixel((90, 40)), direita.getpixel((90, 40)))
        self.assertEqual(esquerda.getpixel((0, 0)), (36, 36, 36))

    def test_recursos_funcionam_no_executavel(self):
        from pathlib import Path
        import mouse_selector
        MouseSelector.renderizar_mouse.cache_clear()
        with patch.object(mouse_selector.sys, "_MEIPASS", str(Path(mouse_selector.__file__).parent), create=True):
            imagem = MouseSelector.renderizar_mouse("Direito")
        self.assertEqual(imagem.size, (220, 172))
        MouseSelector.renderizar_mouse.cache_clear()
