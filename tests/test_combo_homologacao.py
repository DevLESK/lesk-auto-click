"""S02.2: testes da coleta explícita em homologação (sem Windows real)."""
import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from combo_homologacao import ColetaComboHomologacao


CONFIG = {
    "combo_toque_ms": 5,
    "combo_intervalo_ms": 5,
    "combo_apos3_ms": 10,
    "combo_recarga_ms": 10000,
    "combo_recarga_ativa": True,
}


class MotorFalso:
    def __init__(self):
        self.ligado = False
        self.pressionada = None
        self.diagnostico = None
        self.config = dict(CONFIG)


class ColetaHomologacaoTests(unittest.TestCase):
    def setUp(self):
        self.motor = MotorFalso()
        self.coleta = ColetaComboHomologacao(self.motor, fabrica=lambda: __import__(
            "combo_diagnostico").DiagnosticoCombo(relogio_ns=lambda: 123456789)
        )

    def test_desligado_por_padrao(self):
        self.assertIsNone(self.motor.diagnostico)
        self.assertIsNone(self.coleta.coletor)

    def test_ativacao_explicita_reusa_coletor_s02_1(self):
        diag = self.coleta.ativar()
        self.assertIs(self.motor.diagnostico, diag)
        diag.registrar("tecla_down", "1")
        self.assertEqual(len(self.coleta.coletor.eventos), 1)
        self.coleta.desativar()
        self.assertIsNone(self.motor.diagnostico)
        self.assertEqual(len(self.coleta.coletor.eventos), 1)

    def test_nao_ativa_nem_desativa_enquanto_combo_ativo(self):
        self.motor.ligado = True
        with self.assertRaises(RuntimeError):
            self.coleta.ativar()
        self.motor.ligado = False
        self.coleta.ativar()
        self.motor.ligado = True
        with self.assertRaises(RuntimeError):
            self.coleta.desativar()
        self.assertIsNotNone(self.motor.diagnostico)

    def test_nunca_exporta_com_combo_ativo_ou_tecla_presa(self):
        self.coleta.ativar()
        self.coleta.coletor.registrar("tecla_down", "3")
        self.coleta.desativar()
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "coleta.csv"
            self.motor.ligado = True
            with self.assertRaises(RuntimeError):
                self.coleta.exportar(destino)
            self.motor.ligado = False
            self.motor.pressionada = "3"
            with self.assertRaises(RuntimeError):
                self.coleta.exportar(destino)
            self.assertFalse(destino.exists())
            self.motor.pressionada = None
            self.coleta.exportar(destino)
            self.assertTrue(destino.exists())

    def test_nao_exporta_antes_de_desativar(self):
        self.coleta.ativar()
        self.coleta.coletor.registrar("tecla_up", "3")
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "dados.csv"
            with self.assertRaises(RuntimeError):
                self.coleta.exportar(destino)
            self.assertFalse(destino.exists())

    def test_nao_exporta_sem_amostras(self):
        self.coleta.ativar()
        self.coleta.desativar()
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaises(ValueError):
                self.coleta.exportar(Path(pasta) / "vazio.csv")

    def test_exporta_csv_e_perfil_da_ativacao_sem_identificadores(self):
        self.coleta.ativar()
        self.coleta.coletor.registrar("tecla_down", "1", espera_ms=10)
        self.motor.config["combo_toque_ms"] = 99  # mudança posterior não adultera perfil medido
        self.coleta.desativar()
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "combo.csv"
            csv_path, perfil_path = self.coleta.exportar(destino)
            with csv_path.open(encoding="utf-8", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo))
            self.assertEqual(linhas[0]["evento"], "tecla_down")
            self.assertEqual(linhas[0]["tecla"], "1")
            perfil = perfil_path.read_text(encoding="utf-8")
            self.assertIn("combo_toque_ms=5", perfil)
            self.assertIn("combo_recarga_ativa=True", perfil)
            self.assertNotIn("99", perfil)
            self.assertNotIn("licen", perfil.lower())
            self.assertNotIn("machineguid", perfil.lower())

    def test_ativacao_nova_zera_registro_anterior(self):
        primeiro = self.coleta.ativar()
        primeiro.registrar("tecla_down", "1")
        self.coleta.desativar()
        segundo = self.coleta.ativar()
        self.assertIsNot(primeiro, segundo)
        self.assertFalse(segundo.eventos)
        self.coleta.desativar()

    def test_exportacao_nao_aceita_outro_formato(self):
        self.coleta.ativar()
        self.coleta.coletor.registrar("tecla_down", "1")
        self.coleta.desativar()
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaises(ValueError):
                self.coleta.exportar(Path(pasta) / "arquivo.txt")

    def test_gate_ambiental_usa_valor_exato(self):
        # A GUI só deve construir controles quando esta variável for exatamente "1".
        with patch.dict(os.environ, {"LESK_TOOLS_DIAGNOSTICO": "0"}):
            self.assertNotEqual(os.environ.get("LESK_TOOLS_DIAGNOSTICO"), "1")
        with patch.dict(os.environ, {"LESK_TOOLS_DIAGNOSTICO": "1"}):
            self.assertEqual(os.environ.get("LESK_TOOLS_DIAGNOSTICO"), "1")


if __name__ == "__main__":
    unittest.main()
