import os
import sys
import queue

import customtkinter as ctk
import keyboard

from clicker import AutoClicker
from mouse_selector import MouseSelector
from physical_mouse import PhysicalMouseListener
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

    conteudo = ctk.CTkFrame(janela, fg_color="transparent")
    conteudo.pack(fill="both", expand=True, padx=16, pady=8)
    conteudo.grid_columnconfigure(0, weight=1)

    titulo = ctk.CTkLabel(
        conteudo,
        height=22,
        text=TEXTO_TITULO,
        font=FONTE_TITULO,
        text_color=COR_VERDE_NEON
    )
    titulo.grid(row=0, column=0, pady=(0, 2))

    status_label = ctk.CTkLabel(
        conteudo,
        height=20,
        text=TEXTO_STATUS_DESLIGADO,
        font=FONTE_STATUS,
        text_color=COR_VERMELHO_STATUS
    )
    status_label.grid(row=1, column=0)

    comandos = queue.SimpleQueue()
    fechando = False
    mouse_fisico = PhysicalMouseListener(lambda botao: comandos.put(("fisico", botao)))

    estilo_seletor = dict(
        width=COMBO_LARGURA, height=COMBO_ALTURA, corner_radius=COMBO_RAIO_BORDA,
        fg_color="#30363e", border_color="#48525d", border_width=1,
        button_color="#30363e", button_hover_color="#414d58",
        dropdown_fg_color="#30363e", dropdown_hover_color="#20523f",
        text_color="#e4e9ee", text_color_disabled="#84919d",
        font=("Segoe UI", 12), dropdown_font=("Segoe UI", 12))

    def criar_seletor(texto, opcoes, chave):
        ctk.CTkLabel(conteudo, text=texto, height=18,
                     font=FONTE_VELOCIDADE, text_color=COR_VERDE_LABEL).grid(
                         row=3, column=0, pady=(0, 2))
        combo = ctk.CTkComboBox(conteudo, values=list(opcoes), state="readonly",
                              **estilo_seletor)
        combo.set(next(nome for nome, valor in opcoes.items() if valor == config[chave]))
        combo.grid(row=4, column=0)
        return combo

    combo_botao = MouseSelector(conteudo)
    combo_botao.set(next(nome for nome, valor in BOTOES.items() if valor == config["botao"]))
    combo_botao.canvas.grid(row=2, column=0, pady=(2, 0))
    combo_modo = criar_seletor("Modo", MODOS, "modo")

    velocidade_label = ctk.CTkLabel(
        conteudo,
        height=18,
        text=TEXTO_VELOCIDADE,
        font=FONTE_VELOCIDADE,
        text_color=COR_VERDE_LABEL
    )
    velocidade_label.grid(row=5, column=0, pady=(6, 2))

    combo_velocidade = ctk.CTkComboBox(
        conteudo, values=VELOCIDADES, state="readonly", **estilo_seletor)
    combo_velocidade.grid(row=6, column=0)

    combo_velocidade.set(config.get("velocidade", VELOCIDADE_PADRAO))

    ultimo_estado = None

    def atualizar_titulo():
        nonlocal ultimo_estado
        ligado, erro = clicker.estado()
        estado_visual = (ligado, erro, config["modo"], config["botao"])
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
                text="● Ativo · " + ("Direito" if config["botao"] == "right" else "Esquerdo"),
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

    atalhos = ctk.CTkFrame(conteudo, fg_color="transparent")
    atalhos.grid(row=7, column=0, sticky="ew", pady=(10, 0))
    atalhos.grid_columnconfigure((0, 1), weight=1, uniform="atalhos")
    for coluna, tecla, descricao, cor, fundo in (
        (0, "F6", "Liga / desliga", "#45d99a", "#203c32"),
        (1, "F8", "Parar", "#ff8282", "#3d292d"),
    ):
        bloco = ctk.CTkFrame(atalhos, fg_color=fundo, border_color=cor,
                             border_width=1, corner_radius=8)
        bloco.grid(row=0, column=coluna, sticky="ew",
                   padx=(0, 4) if coluna == 0 else (4, 0))
        ctk.CTkLabel(bloco, text=tecla, height=20, text_color=cor,
                     font=("Segoe UI", 15, "bold")).pack(pady=(3, 0))
        ctk.CTkLabel(bloco, text=descricao, height=16,
                     text_color="#e4e9ee", font=("Segoe UI", 10)).pack(pady=(0, 4))

    def processar_comandos():
        if fechando:
            return
        while not comandos.empty():
            comando = comandos.get()
            if isinstance(comando, tuple):
                # Só o MESMO botão físico interrompe o modo pressionado.
                # O outro botão e todos os cliques no modo repetir são livres.
                ligado, _erro = clicker.estado()
                if (ligado and config["modo"] == "pressionar"
                        and comando[1] == config["botao"]):
                    clicker.desligar()
            elif comando == "alternar":
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

    keyboard.add_hotkey(ATALHO_ALTERNAR, alternar)
    keyboard.add_hotkey(ATALHO_PARAR, lambda: comandos.put("parar"))
    atualizar_titulo()
    janela.after(50, processar_comandos)

    janela.protocol("WM_DELETE_WINDOW", fechar)
    try:
        mouse_fisico.start()
        janela.mainloop()
    finally:
        mouse_fisico.stop()
        clicker.parar()
        keyboard.unhook_all_hotkeys()
