"""Licenca offline assinada Ed25519 para um computador.

Chave PRIVADA nunca entra no EXE nem no repositorio. Apenas esta chave
PUBLICA e incluida no aplicativo. Licenca: texto base64url(payload).base64url(assinatura).
"""
import base64
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PUBLIC_KEY_B64 = "TW7DSypYau16IqcjG5ZX4siJaIjWYPcTQ11IpsNgmH8"
PRODUTO = "LESK_TOOLS"
VERSAO = 1


def _b64decode(texto):
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def codigo_pc():
    """Retorna somente resumo SHA-256 do MachineGuid, nunca a identificacao bruta."""
    if sys.platform != "win32":
        raise RuntimeError("Ativacao disponivel apenas no Windows.")
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as chave:
        guid, _ = winreg.QueryValueEx(chave, "MachineGuid")
    return hashlib.sha256(("LESK-TOOLS|v1|" + str(guid)).encode()).hexdigest()[:24].upper()


def caminho_licenca():
    raiz = pathlib.Path(os.environ.get("APPDATA") or pathlib.Path.home())
    return raiz / "LESKTools" / "license.lesk"


def validar_token(token, identificador=None, hoje=None):
    if not isinstance(token, str) or len(token) > 4096:
        raise ValueError("Licenca invalida.")
    try:
        partes = token.strip().split(".")
        if len(partes) != 2:
            raise ValueError("Formato invalido.")
        bruto, assinatura = (_b64decode(parte) for parte in partes)
        chave = Ed25519PublicKey.from_public_bytes(_b64decode(PUBLIC_KEY_B64))
        chave.verify(assinatura, bruto)
        dados = json.loads(bruto)
        if not isinstance(dados, dict) or dados.get("produto") != PRODUTO or dados.get("versao") != VERSAO:
            raise ValueError("Licenca de outro aplicativo.")
        codigo = identificador or codigo_pc()
        if dados.get("dispositivo") != codigo:
            raise ValueError("Esta licenca pertence a outro computador.")
        validade = dados.get("validade")
        if validade:
            expira = dt.date.fromisoformat(validade)
            if expira < (hoje or dt.date.today()):
                raise ValueError("Licenca vencida.")
        return dados
    except InvalidSignature as e:
        raise ValueError("Assinatura da licenca invalida.") from e
    except (TypeError, KeyError, UnicodeError, json.JSONDecodeError) as e:
        raise ValueError("Licenca malformada.") from e
    except (ValueError, base64.binascii.Error) as e:
        raise ValueError(str(e)) from e


def licenca_instalada():
    try:
        return validar_token(caminho_licenca().read_text(encoding="ascii"))
    except (OSError, ValueError, RuntimeError):
        return None


def instalar_licenca(token):
    dados = validar_token(token)
    caminho = caminho_licenca()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temp = caminho.with_suffix(".tmp")
    temp.write_text(token.strip(), encoding="ascii")
    temp.replace(caminho)
    return dados


def pedir_ativacao():
    """Abre dialogo antes de iniciar qualquer automacao."""
    if licenca_instalada():
        return True
    import customtkinter as ctk
    from tkinter import filedialog, messagebox

    janela = ctk.CTk()
    janela.title("LESK Tools · Ativacao")
    janela.geometry("470x320")
    janela.resizable(False, False)
    liberado = {"ok": False}
    ctk.CTkLabel(janela, text="LESK TOOLS · LICENCA", font=("Segoe UI", 19, "bold"),
                 text_color="#45d99a").pack(pady=(18, 10))
    ctk.CTkLabel(janela, text="Envie este codigo ao administrador da guild:").pack()
    try:
        codigo = codigo_pc()
    except Exception as erro:
        codigo = "INDISPONIVEL"
        messagebox.showerror("Ativacao", str(erro))
    campo_codigo = ctk.CTkEntry(janela, width=330, justify="center")
    campo_codigo.insert(0, codigo)
    campo_codigo.configure(state="readonly")
    campo_codigo.pack(pady=8)
    ctk.CTkButton(janela, text="Copiar codigo do PC",
                  command=lambda: (janela.clipboard_clear(), janela.clipboard_append(codigo))).pack(pady=4)

    def importar():
        arquivo = filedialog.askopenfilename(parent=janela, title="Escolha licenca LESK",
                                            filetypes=[("Licenca LESK", "*.lesk"), ("Todos", "*.*")])
        if not arquivo:
            return
        try:
            token = pathlib.Path(arquivo).read_text(encoding="ascii")
            instalar_licenca(token)
        except (OSError, RuntimeError, ValueError) as erro:
            messagebox.showerror("Licenca rejeitada", str(erro), parent=janela)
            return
        liberado["ok"] = True
        messagebox.showinfo("Ativado", "Licenca aceita neste computador.", parent=janela)
        janela.destroy()

    ctk.CTkButton(janela, text="Importar arquivo de licenca (.lesk)",
                  command=importar).pack(pady=(15, 5))
    ctk.CTkLabel(janela, text="Sem chave valida, as automacoes ficam bloqueadas.",
                 text_color="#aab5bf").pack(pady=8)
    janela.mainloop()
    return liberado["ok"]
