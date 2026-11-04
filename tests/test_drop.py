import unittest
from unittest.mock import Mock
from drop import LKDrop
from automation import Automations


class Scheduler:
    def __init__(self):
        self.jobs = {}
        self.all = []
        self.delays = []
        self.n = 0

    def after(self, ms, fn):
        self.n += 1
        self.jobs[self.n] = fn
        self.all.append(fn)
        self.delays.append(ms)
        return self.n

    def after_cancel(self, job):
        self.jobs.pop(job, None)

    def step(self):
        job = min(self.jobs)
        self.jobs.pop(job)()


class DropTests(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()
        self.io = Mock()
        self.io.foco.return_value = 100
        self.io.posicao.return_value = (10, 20)
        self.drop = LKDrop(self.scheduler, self.io, lambda: 200)
        self.drop.marcar("box")
        self.io.posicao.return_value = (30, 40)
        self.drop.marcar("ground")
        self.io.reset_mock()

    def cycle(self):
        self.assertTrue(self.drop.iniciar())
        while self.drop.ciclos < 1:
            self.scheduler.step()

    def test_sequence_no_space(self):
        self.drop.recolher = False
        self.cycle()
        self.assertEqual([c[0] for c in self.io.method_calls if c[0] != "foco"],
                         ["mover", "mouse_down", "mouse_up", "mover", "mouse_down", "mouse_up"])
        self.assertEqual(self.scheduler.delays, [50, 100, 50, 50, 100, 50, 50])

    def test_sequence_five_spaces(self):
        self.cycle()
        self.assertEqual(self.io.espaco_down.call_count, 5)
        self.assertEqual(self.io.espaco_up.call_count, 5)
        self.assertEqual(self.scheduler.delays.count(180), 9)
        self.assertEqual(self.scheduler.delays.count(100), 2)

    def test_capture_focus_validation_and_reset(self):
        self.io.foco.return_value = 200
        self.drop.marcar("box")
        self.assertEqual(self.drop.alvo, 100)
        self.io.foco.return_value = 0
        self.drop.marcar("box")
        self.assertEqual(self.drop.alvo, 100)
        self.io.foco.return_value = 300
        self.drop.marcar("box")
        self.assertEqual(set(self.drop.pontos), {"box"})
        self.assertFalse(self.drop.iniciar())

    def test_capture_ignored_while_running(self):
        self.drop.iniciar()
        before = dict(self.drop.pontos)
        self.drop.marcar("ground")
        self.assertEqual(self.drop.pontos, before)

    def test_start_invalid_interval_and_focus(self):
        for value in (True, 19, 5001, 50.0, "50"):
            self.drop.intervalo = value
            self.assertFalse(self.drop.iniciar())
        self.drop.intervalo = 50
        self.io.foco.return_value = 300
        self.assertFalse(self.drop.iniciar())
        self.io.mouse_down.assert_not_called()

    def test_focus_loss_at_every_callback(self):
        # Every scheduled phase, including held mouse/key releases and gaps.
        for phase in range(16):
            with self.subTest(phase=phase):
                self.setUp()
                self.drop.iniciar()
                for _ in range(phase):
                    self.scheduler.step()
                self.io.reset_mock()
                mouse, key = self.drop.mouse_preso, self.drop.espaco_preso
                self.io.foco.return_value = 300
                self.scheduler.step()
                self.assertFalse(self.drop.ligado)
                self.assertFalse(self.drop.mouse_preso or self.drop.espaco_preso)
                self.assertEqual(self.io.mouse_up.call_count, int(mouse))
                self.assertEqual(self.io.espaco_up.call_count, int(key))
                self.io.mouse_down.assert_not_called()
                self.io.espaco_down.assert_not_called()
                self.io.mover.assert_not_called()
                self.assertFalse(self.scheduler.jobs)

    def test_stale_callbacks_do_not_release_new_generation(self):
        for held_phase in (1, 6):
            with self.subTest(phase=held_phase):
                self.setUp()
                self.drop.iniciar()
                for _ in range(held_phase):
                    self.scheduler.step()
                stale = list(self.scheduler.all)
                self.assertTrue(self.drop.parar())
                self.drop.iniciar()
                for _ in range(held_phase):
                    self.scheduler.step()
                self.io.reset_mock()
                for callback in stale:
                    callback()
                self.assertEqual(self.io.method_calls, [])

    def test_cleanup_release_failure_blocks_restart(self):
        self.drop.iniciar()
        self.scheduler.step()
        self.io.mouse_up.side_effect = RuntimeError("failure")
        self.assertFalse(self.drop.parar())
        self.assertTrue(self.drop.mouse_preso)
        self.assertFalse(self.drop.iniciar())
        self.io.mouse_up.side_effect = None
        self.assertTrue(self.drop.parar())
        self.assertFalse(self.drop.mouse_preso)

    def test_input_failure_cleans_up(self):
        self.io.mouse_down.side_effect = RuntimeError("down failed")
        self.drop.iniciar()
        self.scheduler.step()
        self.assertFalse(self.drop.ligado)
        self.io.mouse_up.assert_called_once()

    def test_routing_exclusive_tabs_hotkeys_and_capture(self):
        clicker = Mock()
        clicker.desligar.return_value = True
        controller = Automations(clicker, self.drop)
        controller.comando("box")
        controller.comando("alternar")
        clicker.alternar.assert_called_once()
        controller.selecionar("LK Drop")
        controller.comando("alternar")
        self.assertTrue(self.drop.ligado)
        self.scheduler.step()
        self.assertTrue(self.drop.mouse_preso)
        controller.selecionar("Auto Click")
        self.assertFalse(self.drop.mouse_preso)
        self.assertFalse(self.scheduler.jobs)
        controller.selecionar("LK Drop")
        controller.comando("alternar")
        for _ in range(6):
            self.scheduler.step()
        self.assertTrue(self.drop.espaco_preso)
        controller.comando("parar")
        self.assertFalse(self.drop.espaco_preso)
        controller.comando("alternar")
        controller.comando("alternar")
        self.assertFalse(self.drop.ligado)

    def test_failed_other_engine_release_prevents_start(self):
        clicker = Mock()
        clicker.desligar.return_value = False
        controller = Automations(clicker, self.drop)
        controller.selecionar("LK Drop")
        controller.comando("alternar")
        self.assertFalse(self.drop.ligado)

    def test_failed_drop_release_prevents_auto_start(self):
        self.drop.iniciar()
        self.scheduler.step()
        self.io.mouse_up.side_effect = RuntimeError("release failed")
        clicker = Mock()
        controller = Automations(clicker, self.drop)
        controller.comando("alternar")
        clicker.alternar.assert_not_called()
        self.assertFalse(self.drop.ligado)
