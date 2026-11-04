import json
import math
from json import JSONDecodeError

CONFIG = "config.json"

CONFIG_PADRAO = {
    "velocidade": "Média",
    "intervalo_clique": 0.05,
    "botao": "left",
    "modo": "repetir",
    "drop_intervalo_ms": 50,
    "drop_recolher": True,
    "combo_toque_ms": 5,
    "combo_intervalo_ms": 5,
    "combo_apos3_ms": 10,
    "combo_recarga_ms": 10000,
    "combo_recarga_ativa": True
}


def config_padrao():
    return CONFIG_PADRAO.copy()


def completar_config(config):
    config_completa = config_padrao()
    config_completa.update(config)
    for chave, valores in (("botao", ("left", "right")),
                           ("modo", ("repetir", "pressionar")),
                           ("velocidade", ("Lenta", "Média", "Rápida"))):
        if config_completa[chave] not in valores:
            config_completa[chave] = CONFIG_PADRAO[chave]
    intervalo = config_completa["intervalo_clique"]
    if (isinstance(intervalo, bool) or not isinstance(intervalo, (int, float))
            or not math.isfinite(intervalo) or intervalo <= 0):
        config_completa["intervalo_clique"] = CONFIG_PADRAO["intervalo_clique"]
    if (type(config_completa["drop_intervalo_ms"]) is not int
            or not 20 <= config_completa["drop_intervalo_ms"] <= 5000):
        config_completa["drop_intervalo_ms"] = 50
    if type(config_completa["drop_recolher"]) is not bool:
        config_completa["drop_recolher"] = True
    for chave, minimo, maximo in (
        ("combo_toque_ms", 0, 200),
        ("combo_intervalo_ms", 0, 200),
        ("combo_apos3_ms", 0, 100),
        ("combo_recarga_ms", 0, 15000),
    ):
        if type(config_completa[chave]) is not int or not minimo <= config_completa[chave] <= maximo:
            config_completa[chave] = CONFIG_PADRAO[chave]
    if type(config_completa["combo_recarga_ativa"]) is not bool:
        config_completa["combo_recarga_ativa"] = True
    return config_completa


def carregar_config():
    try:
        with open(CONFIG, "r", encoding="utf-8") as arquivo:
            config = json.load(arquivo)

    except (FileNotFoundError, JSONDecodeError):
        config = config_padrao()
        salvar_config(config)
        return config

    if not isinstance(config, dict):
        config = config_padrao()
        salvar_config(config)
        return config

    config_completa = completar_config(config)

    if config_completa != config:
        salvar_config(config_completa)

    return config_completa


def salvar_config(config):
    with open(CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(
            config,
            arquivo,
            indent=4,
            ensure_ascii=False
        )
