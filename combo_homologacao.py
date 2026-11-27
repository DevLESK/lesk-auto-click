"""Controle de homologação do Combo DL: acionamento explícito, sem captura externa.

A interface só expõe este controle quando LESK_TOOLS_DIAGNOSTICO=1.
A coleta usa apenas o módulo opcional de S02.1.
"""
from pathlib import Path

from combo_diagnostico import DiagnosticoCombo


class ColetaComboHomologacao:
    def __init__(self, combo, fabrica=DiagnosticoCombo):
        self.combo = combo
        self.fabrica = fabrica
        self.coletor = None

    def ativar(self):
        if self.combo.ligado:
            raise RuntimeError("Pare o Combo DL antes de iniciar a coleta.")
        self.coletor = self.fabrica()
        self.combo.diagnostico = self.coletor
        return self.coletor

    def desativar(self):
        if self.combo.ligado:
            raise RuntimeError("Pare o Combo DL antes de desativar a coleta.")
        self.combo.diagnostico = None

    def exportar(self, destino, configuracao):
        if self.combo.ligado:
            raise RuntimeError("Pare o Combo DL antes de exportar.")
        if not self.coletor or not self.coletor.eventos:
            raise ValueError("Nenhum evento coletado. Ative a coleta e teste o combo.")
        if self.combo.diagnostico is not None:
            raise RuntimeError("Desative a coleta antes de exportar.")

        arquivo = Path(destino)
        if arquivo.suffix.lower() != ".csv":
            raise ValueError("Selecione um arquivo .csv.")
        # Metadados são apenas configurações do Combo, nunca identidade do PC.
        chaves = (
            "combo_toque_ms", "combo_intervalo_ms",
            "combo_apos3_ms", "combo_recarga_ms", "combo_recarga_ativa",
        )
        valores = {chave: configuracao[chave] for chave in chaves}
        # Gerar o arquivo de eventos e um arquivo de perfil no mesmo diretório.
        self.coletor.exportar_csv(arquivo)
        perfil = arquivo.with_suffix(".perfil.txt")
        perfil.write_text(
            "LESK Tools — S02.2 — Perfil de homologação DL\n"
            + "".join(f"{chave}={valor}\n" for chave, valor in valores.items())
            + f"eventos_descartados={self.coletor.descartados}\n",
            encoding="utf-8",
        )
        return arquivo, perfil
