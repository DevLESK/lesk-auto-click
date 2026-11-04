import base64
import datetime as dt
import json
import unittest
from unittest.mock import patch

import licensing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


def b64(dados):
    return base64.urlsafe_b64encode(dados).decode("ascii").rstrip("=")


class LicenseTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        pub = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.public_patch = patch.object(licensing, "PUBLIC_KEY_B64", b64(pub))
        self.public_patch.start()
        self.addCleanup(self.public_patch.stop)

    def token(self, dispositivo="A" * 24, validade=None):
        dados = dict(produto="LESK_TOOLS", versao=1,
                     dispositivo=dispositivo, validade=validade)
        corpo = json.dumps(dados, separators=(",", ":")).encode()
        return b64(corpo) + "." + b64(self.private.sign(corpo))

    def test_licenca_valida_para_este_pc(self):
        dados = licensing.validar_token(self.token(), identificador="A" * 24)
        self.assertEqual(dados["produto"], "LESK_TOOLS")

    def test_licenca_nao_funciona_em_outro_pc(self):
        with self.assertRaisesRegex(ValueError, "outro computador"):
            licensing.validar_token(self.token(), identificador="B" * 24)

    def test_licenca_adulterada_falha(self):
        token = self.token()
        payload, assinatura = token.split(".")
        with self.assertRaises(ValueError):
            licensing.validar_token(payload + "." + assinatura[:-2] + "AA",
                                    identificador="A" * 24)

    def test_licenca_expirada_falha(self):
        with self.assertRaisesRegex(ValueError, "vencida"):
            licensing.validar_token(self.token(validade="2020-01-01"),
                                    identificador="A" * 24, hoje=dt.date(2026, 11, 4))


if __name__ == "__main__":
    unittest.main()
