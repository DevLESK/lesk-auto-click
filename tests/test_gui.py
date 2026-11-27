"""Teste de integracao dos atalhos no painel, sem entradas reais de Windows."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


class FakeClicker:
    def __init__(self):
        self.botao = "left"
        self.modo = "repetir"
        self.ligado = False
        self.historico = []
        self.falhar_liberacao = False

    def iniciar(self):
        pass

    def estado(self):
        return self.ligado, None

    def configurar(self, botao, modo):
        if self.ligado:
            raise RuntimeError("Troca com mouse ativo")
        self.botao, self.modo = botao, modo
        self.historico.append(("config", botao))

    def ligar(self):
        self.ligado = True
        self.historico.append(("ligar", self.botao))

    def desligar(self):
        self.historico.append(("soltar", self.botao))
        if self.falhar_liberacao:
            return False
        self.ligado = False
        return True

    def parar(self):
        return self.desligar()


class TestGui(unittest.TestCase):
    def test_hotkeys_f6_f8_f9_e_outras_abas(self):
        ctk, keyboard = Mock(), Mock()
        clicker = FakeClicker()
        combos = [Mock(), Mock(), Mock()]
        seletor_module, physical_module = Mock(), Mock()
        seletor_module.MouseSelector.return_value = combos[0]
        ctk.CTkComboBox.side_effect = combos[1:]
        janela = ctk.CTk.return_value
        config = {
            "intervalo_clique": 0.05, "velocidade": "Média",
            "botao": "left", "modo": "repetir",
            "drop_intervalo_ms": 50, "drop_recolher": True,
            "combo_toque_ms": 5, "combo_intervalo_ms": 5,
            "combo_apos3_ms": 10, "combo_recarga_ms": 10000,
            "combo_recarga_ativa": False,
        }
        config_module, clicker_module = Mock(), Mock()
        config_module.carregar_config.return_value = config
        clicker_module.AutoClicker.return_value = clicker
        licencia = Mock()
        licencia.pedir_ativacao.return_value = True
        combo_modulo = Mock()
        combo = combo_modulo.LKCombo.return_value
        combo.ligado = False
        combo.status = "Parado"
        combo.parar.return_value = True

        def ligar_combo():
            combo.ligado = True
            return True
        def parar_combo():
            combo.ligado = False
            return True
        combo.iniciar.side_effect = ligar_combo
        combo.parar.side_effect = parar_combo

        spec = importlib.util.spec_from_file_location(
            "gui_em_teste", Path(__file__).resolve().parents[1] / "gui.py")
        gui = importlib.util.module_from_spec(spec)

        with patch.dict(sys.modules, {
            "customtkinter": ctk,
            "keyboard": keyboard,
            "clicker": clicker_module,
            "config": config_module,
            "mouse_selector": seletor_module,
            "physical_mouse": physical_module,
            "drop_windows": Mock(),
            "licensing": licencia,
            "combo": combo_modulo,
        }):
            spec.loader.exec_module(gui)
            io = gui.WindowsInput.return_value
            io.foco.return_value = 100
            io.raiz.return_value = 200
            io.posicao.return_value = (10, 20)
            ctk.StringVar.return_value.get.return_value = "50"
            ctk.BooleanVar.return_value.get.return_value = True

            def executar_interface():
                hotkeys = {c.args[0]: c.args[1] for c in keyboard.add_hotkey.call_args_list}
                self.assertEqual(set(hotkeys), {"F2", "F3", "F6", "F8", "F9"})
                self.assertNotIn("trigger_on_release", next(
                    c for c in keyboard.add_hotkey.call_args_list
                    if c.args[0] == "F6").kwargs)

                def poll():
                    janela.after.call_args.args[1]()

                hotkeys["F6"]()
                poll()
                self.assertTrue(clicker.ligado)
                self.assertEqual(clicker.botao, "left")

                hotkeys["F8"]()
                poll()
                self.assertTrue(clicker.ligado)
                self.assertEqual(clicker.botao, "right")
                self.assertEqual(config["botao"], "right")
                combos[0].set.assert_any_call("Direito")
                self.assertEqual(clicker.historico[-3:],
                                 [("soltar", "left"), ("config", "right"),
                                  ("ligar", "right")])

                tabs = ctk.CTkTabview.return_value
                trocar = tabs.configure.call_args.kwargs["command"]
                clicker.falhar_liberacao = True
                tabs.get.return_value = "LK Drop"
                trocar()
                self.assertTrue(clicker.ligado)
                tabs.set.assert_called_with("Auto Click")
                clicker.falhar_liberacao = False

                hotkeys["F8"]()
                poll()
                self.assertFalse(clicker.ligado)

                hotkeys["F6"]()
                poll()
                self.assertEqual(clicker.botao, "left")
                hotkeys["F9"]()
                poll()
                self.assertFalse(clicker.ligado)

                tabs = ctk.CTkTabview.return_value
                trocar = tabs.configure.call_args.kwargs["command"]
                tabs.get.return_value = "LK Drop"
                trocar()
                poll()
                for tecla in ("F2", "F3", "F6"):
                    hotkeys[tecla]()
                    poll()
                self.assertEqual(janela.title.call_args.args[0], "LK Drop · Ativo")
                hotkeys["F8"]()  # F8 fora da aba Auto Click nao interrompe.
                poll()
                self.assertEqual(janela.title.call_args.args[0], "LK Drop · Ativo")
                hotkeys["F9"]()
                poll()
                self.assertEqual(janela.title.call_args.args[0], "LK Drop · Parado")

                tabs.get.return_value = "LK Combo"
                trocar()
                poll()
                hotkeys["F6"]()
                poll()
                self.assertTrue(combo.ligado)
                hotkeys["F8"]()
                poll()
                self.assertTrue(combo.ligado)
                hotkeys["F9"]()
                poll()
                self.assertFalse(combo.ligado)

                fechar = janela.protocol.call_args.args[1]
                fechar()
                janela.destroy.assert_called_once()

            janela.mainloop.side_effect = executar_interface
            gui.iniciar_aplicacao()
        physical_module.PhysicalMouseListener.return_value.start.assert_called_once()
        physical_module.PhysicalMouseListener.return_value.stop.assert_called_once()
        self.assertTrue(keyboard.unhook_all_hotkeys.called)


if __name__ == "__main__":
    unittest.main()
