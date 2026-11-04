import unittest

from combo import LKCombo, validar_combo


BASE = {
    "combo_toque_ms": 5,
    "combo_intervalo_ms": 5,
    "combo_apos3_ms": 10,
    "combo_recarga_ms": 10000,
    "combo_recarga_ativa": False,
}


class Agenda:
    def __init__(self):
        self.next_id = 0
        self.jobs = {}

    def after(self, ms, callback):
        self.next_id += 1
        self.jobs[self.next_id] = (ms, callback)
        return self.next_id

    def after_cancel(self, identificador):
        self.jobs.pop(identificador, None)

    def passar(self, n):
        for _ in range(n):
            if not self.jobs:
                break
            identificador = next(iter(self.jobs))
            _, callback = self.jobs.pop(identificador)
            callback()


class Entradas:
    def __init__(self):
        self.active = 42
        self.keys = []

    def foco(self):
        return self.active

    def tecla_down(self, tecla):
        self.keys.append(("down", tecla))

    def tecla_up(self, tecla):
        self.keys.append(("up", tecla))


class ComboTests(unittest.TestCase):
    def setUp(self):
        self.agenda = Agenda()
        self.entrada = Entradas()

    def criar(self, recarga=False):
        return LKCombo(self.agenda, self.entrada, lambda: 99,
                       {**BASE, "combo_recarga_ativa": recarga})

    def test_sem_recarga_sequencia_continua(self):
        combo = self.criar()
        self.assertTrue(combo.iniciar())
        self.agenda.passar(12)
        self.assertEqual([t for modo, t in self.entrada.keys if modo == "down"][:7],
                         ["1", "2", "3", "1", "2", "3", "1"])

    def test_com_recarga_sem_duplicar_um(self):
        combo = self.criar(recarga=True)
        self.assertTrue(combo.iniciar())
        self.agenda.passar(12)
        self.assertEqual([t for modo, t in self.entrada.keys if modo == "down"][:6],
                         ["1", "2", "3", "1", "2", "3"])

    def test_parar_libera_e_cancela_tarefas(self):
        combo = self.criar()
        combo.iniciar()
        self.assertTrue(combo.parar())
        self.assertEqual(self.entrada.keys, [("down", "1"), ("up", "1")])
        self.assertFalse(self.agenda.jobs)

    def test_pausar_ao_sair_do_jogo(self):
        combo = self.criar()
        combo.iniciar()
        self.entrada.active = 13
        self.agenda.passar(1)
        self.assertFalse(combo.ligado)
        self.assertFalse(self.agenda.jobs)
        self.assertEqual(self.entrada.keys[-1], ("up", "1"))

    def test_rejeita_valores_fora_de_faixa(self):
        with self.assertRaises(ValueError):
            validar_combo({**BASE, "combo_recarga_ms": 15001})
        with self.assertRaises(ValueError):
            validar_combo({**BASE, "combo_toque_ms": -1})


if __name__ == "__main__":
    unittest.main()
