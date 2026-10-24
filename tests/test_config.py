import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self._config_original = config.CONFIG
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.json"
        config.CONFIG = str(self.config_path)

    def tearDown(self):
        config.CONFIG = self._config_original
        self.temp_dir.cleanup()

    def ler_config_json(self):
        with self.config_path.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def test_recria_config_quando_arquivo_nao_existe(self):
        resultado = config.carregar_config()

        self.assertEqual(resultado, config.CONFIG_PADRAO)
        self.assertTrue(self.config_path.exists())
        self.assertEqual(self.ler_config_json(), config.CONFIG_PADRAO)

    def test_recria_config_quando_json_invalido(self):
        self.config_path.write_text("{ json invalido", encoding="utf-8")

        resultado = config.carregar_config()

        self.assertEqual(resultado, config.CONFIG_PADRAO)
        self.assertEqual(self.ler_config_json(), config.CONFIG_PADRAO)

    def test_recria_config_quando_conteudo_nao_e_objeto(self):
        self.config_path.write_text('["valor"]', encoding="utf-8")

        resultado = config.carregar_config()

        self.assertEqual(resultado, config.CONFIG_PADRAO)
        self.assertEqual(self.ler_config_json(), config.CONFIG_PADRAO)

    def test_preenche_chave_ausente(self):
        dados = {"velocidade": "Rápida"}
        self.config_path.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

        resultado = config.carregar_config()

        self.assertEqual(resultado["velocidade"], "Rápida")
        self.assertEqual(resultado["intervalo_clique"], config.CONFIG_PADRAO["intervalo_clique"])
        self.assertEqual(self.ler_config_json(), resultado)

    def test_preserva_valores_validos(self):
        dados = {"velocidade": "Lenta", "intervalo_clique": 0.2}
        self.config_path.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

        resultado = config.carregar_config()

        self.assertEqual(resultado, dados)
        self.assertEqual(self.ler_config_json(), dados)

    def test_preserva_chaves_extras(self):
        dados = {
            "velocidade": "Rápida",
            "intervalo_clique": 0.01,
            "tema": "customizado",
        }
        self.config_path.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

        resultado = config.carregar_config()

        self.assertEqual(resultado, dados)
        self.assertEqual(self.ler_config_json(), dados)


if __name__ == "__main__":
    unittest.main()