"""Atalhos de mouse sem entrada real: transicoes, exclusividade e emergencia."""
import unittest
from automation import Automations


class ClickerFalso:
    def __init__(self, modo):
        self.botao = "left"
        self.modo = modo
        self.ligado = False
        self.liberacao_falha = False
        self.eventos = []

    def estado(self):
        return self.ligado, None

    def desligar(self):
        self.eventos.append(("soltar", self.botao))
        if self.liberacao_falha:
            return False
        self.ligado = False
        return True

    def configurar(self, botao, modo):
        if self.ligado:
            raise AssertionError("Nao pode reconfigurar mouse pressionado")
        self.botao, self.modo = botao, modo
        self.eventos.append(("configurar", botao, modo))

    def ligar(self):
        if self.ligado:
            raise AssertionError("Tentativa de dois botoes simultaneos")
        self.ligado = True
        self.eventos.append(("ligar", self.botao))


class OutroMotor:
    def __init__(self):
        self.ligado = False
        self.falha = False
        self.paradas = 0
        self.inicios = 0

    def parar(self):
        self.paradas += 1
        if self.falha:
            return False
        self.ligado = False
        return True

    def iniciar(self):
        self.inicios += 1
        self.ligado = True
        return True


class TestAtalhos(unittest.TestCase):
    def montar(self, modo="repetir"):
        clicker, drop, combo = ClickerFalso(modo), OutroMotor(), OutroMotor()
        return Automations(clicker, drop, combo), clicker, drop, combo

    def test_f6_liga_e_desliga_esquerdo(self):
        for modo in ("repetir", "pressionar"):
            with self.subTest(modo=modo):
                controle, clicker, _, _ = self.montar(modo)
                self.assertTrue(controle.comando("esquerdo"))
                self.assertEqual((clicker.botao, clicker.modo, clicker.ligado),
                                 ("left", modo, True))
                self.assertTrue(controle.comando("esquerdo"))
                self.assertFalse(clicker.ligado)

    def test_f8_liga_e_desliga_direito(self):
        for modo in ("repetir", "pressionar"):
            with self.subTest(modo=modo):
                controle, clicker, _, _ = self.montar(modo)
                self.assertTrue(controle.comando("direito"))
                self.assertEqual((clicker.botao, clicker.modo, clicker.ligado),
                                 ("right", modo, True))
                self.assertTrue(controle.comando("direito"))
                self.assertFalse(clicker.ligado)

    def test_alternancia_rapida_soltar_antes_de_trocar(self):
        controle, clicker, _, _ = self.montar("pressionar")
        for _ in range(30):
            self.assertTrue(controle.comando("esquerdo"))
            self.assertTrue(controle.comando("direito"))
        self.assertEqual((clicker.botao, clicker.ligado), ("right", True))
        eventos = clicker.eventos
        for i, evento in enumerate(eventos):
            if evento[0] == "configurar":
                if i:
                    self.assertEqual(eventos[i-1][0], "soltar")

    def test_f9_parada_geral_desliga_todas_automacoes(self):
        controle, clicker, drop, combo = self.montar("pressionar")
        self.assertTrue(controle.comando("direito"))
        drop.ligado = combo.ligado = True
        self.assertTrue(controle.comando("parar"))
        self.assertFalse(clicker.ligado or drop.ligado or combo.ligado)

    def test_f6_drop_e_combo_f8_nao_interfere(self):
        controle, clicker, drop, combo = self.montar()
        controle.selecionar("LK Drop")
        controle.comando("esquerdo")
        self.assertTrue(drop.ligado)
        self.assertEqual(drop.inicios, 1)
        controle.comando("direito")
        self.assertTrue(drop.ligado)
        self.assertEqual(drop.inicios, 1)
        controle.selecionar("LK Combo")
        self.assertFalse(drop.ligado)
        controle.comando("esquerdo")
        self.assertTrue(combo.ligado)
        controle.comando("direito")
        self.assertTrue(combo.ligado)
        controle.comando("parar")
        self.assertFalse(combo.ligado)

    def test_troca_de_aba_para_mouse(self):
        controle, clicker, _, _ = self.montar()
        controle.comando("direito")
        controle.selecionar("LK Drop")
        self.assertFalse(clicker.ligado)

    def test_falha_ao_soltar_impede_troca(self):
        controle, clicker, _, _ = self.montar()
        controle.comando("esquerdo")
        clicker.liberacao_falha = True
        antes = len([e for e in clicker.eventos if e[0] == "ligar"])
        self.assertFalse(controle.comando("direito"))
        self.assertTrue(clicker.ligado)
        self.assertEqual(clicker.botao, "left")
        self.assertEqual(len([e for e in clicker.eventos if e[0] == "ligar"]), antes)

    def test_falha_ao_parar_drop_impede_start_mouse(self):
        controle, clicker, drop, _ = self.montar()
        drop.falha = True
        self.assertFalse(controle.comando("direito"))
        self.assertFalse(clicker.ligado)


if __name__ == "__main__":
    unittest.main()
