import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


class TestGui(unittest.TestCase):
    def test_atalhos_seletores_e_encerramento(self):
        ctk, keyboard, clicker = Mock(), Mock(), Mock()
        clicker.estado.return_value = (False, None)
        clicker.parar.return_value = True
        clicker.botao, clicker.modo = "right", "pressionar"
        combos = [Mock(), Mock(), Mock()]
        ctk.CTkComboBox.side_effect = combos
        janela = ctk.CTk.return_value
        config = {"intervalo_clique": 0.05, "velocidade": "Média",
                  "botao": "left", "modo": "repetir"}
        config_module, clicker_module = Mock(), Mock()
        config_module.carregar_config.return_value = config
        clicker_module.AutoClicker.return_value = clicker
        spec = importlib.util.spec_from_file_location("gui_em_teste", Path(__file__).resolve().parents[1] / "gui.py")
        gui = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"customtkinter": ctk, "keyboard": keyboard,
                                     "clicker": clicker_module, "config": config_module}):
            spec.loader.exec_module(gui)
            def executar_interface():
                hotkeys = {c.args[0]: c.args[1] for c in keyboard.add_hotkey.call_args_list}
                poll = janela.after.call_args.args[1]
                hotkeys["F6"]()
                clicker.alternar.assert_not_called()
                poll()
                clicker.alternar.assert_called_once()
                hotkeys["F8"]()
                poll()
                clicker.desligar.assert_called_once()
                combos[0].get.return_value = "Direito"
                combos[1].get.return_value = "Manter pressionado"
                mudar = next(c.kwargs["command"] for c in combos[0].configure.call_args_list if "command" in c.kwargs)
                mudar("Direito")
                clicker.configurar.assert_called_with("right", "pressionar")
                self.assertEqual(config["botao"], "right")
                combos[2].configure.assert_called_with(state="disabled")
                clicker.estado.return_value = (True, None)
                poll()
                combos[0].configure.assert_called_with(state="disabled")
                combos[1].configure.assert_called_with(state="disabled")
                fechar = janela.protocol.call_args.args[1]
                fechar()
                janela.destroy.assert_called_once()
            janela.mainloop.side_effect = executar_interface
            gui.iniciar_aplicacao()
        self.assertTrue(clicker.parar.called)
        self.assertTrue(keyboard.unhook_all_hotkeys.called)
