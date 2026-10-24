import json
import math
from json import JSONDecodeError

CONFIG = "config.json"

CONFIG_PADRAO = {
    "velocidade": "Média",
    "intervalo_clique": 0.05,
    "botao": "left",
    "modo": "repetir"
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
