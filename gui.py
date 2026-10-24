import os
import sys
import queue

import customtkinter as ctk
import keyboard

from clicker import AutoClicker
from config import carregar_config, salvar_config
from ui_constants import (
    ARQUIVO_ICONE,
    ATALHO_PARAR,
    BOTOES,
    MODOS,
    ATALHO_ALTERNAR,
    COMBO_ALTURA,
    COMBO_LARGURA,
    COMBO_RAIO_BORDA,
    COR_CINZA,
    COR_VERDE_HOVER,
    COR_VERDE_LABEL,
    COR_VERDE_NEON,
    COR_VERMELHO_STATUS,
    FONTE_ATALHO,
    FONTE_STATUS,
    FONTE_TITULO,
    FONTE_VELOCIDADE,
    GEOMETRIA_JANELA,
    INTERVALOS_POR_VELOCIDADE,
    JANELA_REDIMENSIONAVEL,
    MODO_APARENCIA,
    PADDING_ATALHO,
    PADDING_STATUS,
    PADDING_TITULO,
    PADDING_VELOCIDADE,
    TEMA_COR,
    TEXTO_ATALHO,
    TEXTO_STATUS_DESLIGADO,
    TEXTO_STATUS_LIGADO,
    TEXTO_TITULO,
    TEXTO_VELOCIDADE,
    TITULO_DESLIGADO,
    TITULO_LIGADO,
    VELOCIDADE_PADRAO,
    VELOCIDADES,
)


def caminho_recurso(nome_arquivo):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nome_arquivo)

    return os.path.join(os.path.abspath("."), nome_arquivo)


def iniciar_aplicacao():
    config = carregar_config()

    clicker = AutoClicker(config["intervalo_clique"], config["botao"], config["modo"])
    clicker.iniciar()

    ctk.set_appearance_mode(MODO_APARENCIA)
    ctk.set_default_color_theme(TEMA_COR)

    janela = ctk.CTk()

    try:
        janela.iconbitmap(caminho_recurso(ARQUIVO_ICONE))
    except Exception:
        pass

    janela.title(TITULO_DESLIGADO)
    janela.geometry(GEOMETRIA_JANELA)
    janela.resizable(*JANELA_REDIMENSIONAVEL)

    titulo = ctk.CTkLabel(
        janela,
        text=TEXTO_TITULO,
        font=FONTE_TITULO,
        text_color=COR_VERDE_NEON
    )
    titulo.pack(pady=PADDING_TITULO)

    status_label = ctk.CTkLabel(
        janela,
        text=TEXTO_STATUS_DESLIGADO,
        font=FONTE_STATUS,
        text_color=COR_VERMELHO_STATUS
    )
    status_label.pack(pady=PADDING_STATUS)

    comandos = queue.SimpleQueue()
    fechando = False

    def criar_seletor(texto, opcoes, chave):
        ctk.CTkLabel(janela, text=texto, font=FONTE_VELOCIDADE).pack(pady=(10, 3))
        combo = ctk.CTkComboBox(janela, values=list(opcoes), state="readonly",
                              width=COMBO_LARGURA)
        combo.set(next(nome for nome, valor in opcoes.items() if valor == config[chave]))
        combo.pack()
        return combo

    combo_botao = criar_seletor("Botão", BOTOES, "botao")
    combo_modo = criar_seletor("Modo", MODOS, "modo")

    velocidade_label = ctk.CTkLabel(
        janela,
        text=TEXTO_VELOCIDADE,
        font=FONTE_VELOCIDADE,
        text_color=COR_VERDE_LABEL
    )
    velocidade_label.pack(pady=PADDING_VELOCIDADE)

    combo_velocidade = ctk.CTkComboBox(
        janela,
        values=VELOCIDADES,
        width=COMBO_LARGURA,
        height=COMBO_ALTURA,
        corner_radius=COMBO_RAIO_BORDA,
        button_color=COR_VERDE_NEON,
        button_hover_color=COR_VERDE_HOVER,
        dropdown_hover_color=COR_VERDE_HOVER
    )
    combo_velocidade.pack()

    combo_velocidade.set(config.get("velocidade", VELOCIDADE_PADRAO))

    ultimo_estado = None

    def atualizar_titulo():
        nonlocal ultimo_estado
        ligado, erro = clicker.estado()
        estado_visual = (ligado, erro, config["modo"])
        if estado_visual == ultimo_estado:
            return
        ultimo_estado = estado_visual
        combo_botao.configure(state="disabled" if ligado else "readonly")
        combo_modo.configure(state="disabled" if ligado else "readonly")
        combo_velocidade.configure(
            state="disabled" if config["modo"] == "pressionar" else "readonly"
        )
        if ligado:
            janela.title(TITULO_LIGADO)
            status_label.configure(
                text=TEXTO_STATUS_LIGADO,
                text_color=COR_VERDE_NEON
            )
        else:
            janela.title(TITULO_DESLIGADO)
            status_label.configure(
                text="Erro: use F8 para liberar" if erro else TEXTO_STATUS_DESLIGADO,
                text_color=COR_VERMELHO_STATUS
            )

    def alternar():
        comandos.put("alternar")

    def alternar_tkinter():
        clicker.alternar()
        atualizar_titulo()

    def mudar_opcoes(_valor):
        clicker.configurar(BOTOES[combo_botao.get()], MODOS[combo_modo.get()])
        config["botao"], config["modo"] = clicker.botao, clicker.modo
        salvar_config(config)
        atualizar_titulo()

    combo_botao.configure(command=mudar_opcoes)
    combo_modo.configure(command=mudar_opcoes)

    def mudar_velocidade(velocidade):
        intervalo = INTERVALOS_POR_VELOCIDADE[velocidade]

        clicker.definir_intervalo(intervalo)

        config["velocidade"] = velocidade
        config["intervalo_clique"] = intervalo
        salvar_config(config)

    combo_velocidade.configure(command=mudar_velocidade)

    atalho_label = ctk.CTkLabel(
        janela,
        text=TEXTO_ATALHO,
        font=FONTE_ATALHO,
        text_color=COR_CINZA
    )
    atalho_label.pack(pady=PADDING_ATALHO)

    def processar_comandos():
        if fechando:
            return
        while not comandos.empty():
            comando = comandos.get()
            if comando == "alternar":
                alternar_tkinter()
            else:
                clicker.desligar()
        atualizar_titulo()
        janela.after(50, processar_comandos)

    def fechar():
        nonlocal fechando
        if not clicker.parar():
            atualizar_titulo()
            return
        fechando = True
        keyboard.unhook_all_hotkeys()
        janela.destroy()

    keyboard.add_hotkey(ATALHO_ALTERNAR, alternar, trigger_on_release=True)
    keyboard.add_hotkey(ATALHO_PARAR, lambda: comandos.put("parar"),
                        trigger_on_release=True)
    atualizar_titulo()
    janela.after(50, processar_comandos)

    janela.protocol("WM_DELETE_WINDOW", fechar)
    try:
        janela.mainloop()
    finally:
        clicker.parar()
        keyboard.unhook_all_hotkeys()
