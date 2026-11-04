import os
import sys
import queue

import customtkinter as ctk
import keyboard

from automation import Automations
from drop import LKDrop
from combo import LKCombo, validar_combo
from licensing import pedir_ativacao
from drop_windows import WindowsInput
from clicker import AutoClicker
from mouse_selector import MouseSelector
from physical_mouse import PhysicalMouseListener
from config import carregar_config, salvar_config
from ui_constants import (
    ARQUIVO_ICONE,
    ATALHO_PARAR,
    ATALHO_DIREITO,
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
    if not pedir_ativacao():
        return
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

    abas = ctk.CTkTabview(janela)
    abas.pack(fill="both", expand=True, padx=0, pady=0)
    auto_aba = abas.add("Auto Click")
    drop_aba = abas.add("LK Drop")
    combo_aba = abas.add("LK Combo")
    entrada = WindowsInput()
    drop = LKDrop(janela, entrada, lambda: entrada.raiz(janela.winfo_id()),
                  config["drop_intervalo_ms"], config["drop_recolher"])
    combo = LKCombo(janela, entrada, lambda: entrada.raiz(janela.winfo_id()),
                    {chave: config[chave] for chave in (
                        "combo_toque_ms", "combo_intervalo_ms", "combo_apos3_ms",
                        "combo_recarga_ms", "combo_recarga_ativa")})
    controle = Automations(clicker, drop, combo)
    abas.configure(command=lambda: controle.selecionar(abas.get()))

    conteudo = ctk.CTkFrame(auto_aba, fg_color="transparent")
    conteudo.pack(fill="both", expand=True, padx=16, pady=8)
    conteudo.grid_columnconfigure((0, 1), weight=1, uniform="opcoes")

    titulo = ctk.CTkLabel(
        conteudo,
        height=22,
        text=TEXTO_TITULO,
        font=FONTE_TITULO,
        text_color=COR_VERDE_NEON
    )
    titulo.grid(row=0, column=0, columnspan=2, pady=(0, 2))

    status_label = ctk.CTkLabel(
        conteudo,
        height=20,
        text=TEXTO_STATUS_DESLIGADO,
        font=FONTE_STATUS,
        text_color=COR_VERMELHO_STATUS
    )
    status_label.grid(row=1, column=0, columnspan=2)

    comandos = queue.SimpleQueue()
    fechando = False
    mouse_fisico = PhysicalMouseListener(lambda botao: comandos.put(("fisico", botao)))

    estilo_seletor = dict(
        width=COMBO_LARGURA, height=COMBO_ALTURA, corner_radius=COMBO_RAIO_BORDA,
        justify="center",
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
        combo.grid(row=4, column=0, sticky="ew", padx=(0, 4))
        return combo

    combo_botao = MouseSelector(conteudo)
    combo_botao.set(next(nome for nome, valor in BOTOES.items() if valor == config["botao"]))
    combo_botao.canvas.grid(row=2, column=0, columnspan=2, pady=(2, 0))
    combo_modo = criar_seletor("Modo", MODOS, "modo")

    velocidade_label = ctk.CTkLabel(
        conteudo,
        height=18,
        text=TEXTO_VELOCIDADE,
        font=FONTE_VELOCIDADE,
        text_color=COR_VERDE_LABEL
    )
    velocidade_label.grid(row=3, column=1, pady=(0, 2))

    combo_velocidade = ctk.CTkComboBox(
        conteudo, values=VELOCIDADES, state="readonly", **estilo_seletor)
    combo_velocidade.grid(row=4, column=1, sticky="ew", padx=(4, 0))

    combo_velocidade.set(config.get("velocidade", VELOCIDADE_PADRAO))

    drop_frame = ctk.CTkFrame(drop_aba, fg_color="transparent")
    drop_frame.pack(fill="both", expand=True, padx=12, pady=8)
    drop_frame.grid_columnconfigure((0, 1), weight=1, uniform="pontos")
    ctk.CTkLabel(drop_frame, text="LK DROP", font=FONTE_TITULO,
                 text_color=COR_VERDE_NEON).grid(row=0, column=0, columnspan=2, pady=(0, 8))
    pontos_labels = {}
    for coluna, ponto, texto in ((0, "box", "F2 · Box"), (1, "ground", "F3 · Chão")):
        bloco = ctk.CTkFrame(drop_frame, fg_color="#30363e", corner_radius=8)
        bloco.grid(row=1, column=coluna, sticky="ew", padx=4, pady=8)
        ctk.CTkLabel(bloco, text=texto, text_color=COR_VERDE_NEON).pack(pady=(10, 0))
        pontos_labels[ponto] = ctk.CTkLabel(bloco, text="Não marcado")
        pontos_labels[ponto].pack(pady=(0, 10))
    ctk.CTkLabel(drop_frame, text="Intervalo entre ações (ms)").grid(
        row=2, column=0, columnspan=2, pady=(12, 2))
    intervalo_drop = ctk.StringVar(value=str(drop.intervalo))
    campo_intervalo = ctk.CTkEntry(drop_frame, textvariable=intervalo_drop,
                                  width=120, justify="center")
    campo_intervalo.grid(row=3, column=0, columnspan=2)
    recolher_drop = ctk.BooleanVar(value=drop.recolher)

    def salvar_drop(*_args):
        if drop.ligado:
            return
        try:
            valor = int(intervalo_drop.get())
            if not 20 <= valor <= 5000:
                raise ValueError
        except ValueError:
            drop.status = "Use intervalo inteiro entre 20 e 5000 ms."
            return
        drop.intervalo, drop.recolher = valor, bool(recolher_drop.get())
        config["drop_intervalo_ms"] = valor
        config["drop_recolher"] = drop.recolher
        salvar_config(config)

    campo_intervalo.bind("<FocusOut>", salvar_drop)
    campo_intervalo.bind("<Return>", salvar_drop)
    check_recolher = ctk.CTkCheckBox(drop_frame, text="Recolher com Espaço (5 vezes)",
                                   variable=recolher_drop, command=salvar_drop)
    check_recolher.grid(row=4, column=0, columnspan=2, pady=18)
    status_drop = ctk.CTkLabel(drop_frame, text=drop.status, wraplength=320,
                              text_color=COR_VERDE_LABEL, height=50)
    status_drop.grid(row=5, column=0, columnspan=2, pady=8)
    ctk.CTkLabel(drop_frame, text="F6  Liga / desliga     •     F9  Para tudo",
                 font=("Segoe UI", 14, "bold"), text_color=COR_VERDE_NEON).grid(
                     row=6, column=0, columnspan=2, pady=10)
    # Terceira aba: valores ajustaveis por 1 ms; sem pressionar o mouse direito.
    combo_frame = ctk.CTkScrollableFrame(combo_aba, fg_color="transparent")
    combo_frame.pack(fill="both", expand=True, padx=10, pady=6)
    combo_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(combo_frame, text="LK COMBO · DL / BK", font=FONTE_TITULO,
                 text_color=COR_VERDE_NEON).grid(
                     row=0, column=0, columnspan=4, pady=(2, 10))

    campos_combo = {}
    controles_combo = (
        ("Toque na tecla (ms)", "combo_toque_ms", 200),
        ("Entre magias (ms)", "combo_intervalo_ms", 200),
        ("Apos magia 3 (ms)", "combo_apos3_ms", 100),
        ("Recarga magia 3 (ms)", "combo_recarga_ms", 15000),
    )
    botao_repetir = {"after": None}

    def interromper_repeticao(_evento=None):
        if botao_repetir["after"] is not None:
            janela.after_cancel(botao_repetir["after"])
            botao_repetir["after"] = None

    def passo_combo(chave, limite, delta):
        if combo.ligado:
            return
        try:
            anterior = int(campos_combo[chave].get())
        except ValueError:
            anterior = 0
        campos_combo[chave].set(str(max(0, min(limite, anterior + delta))))

    def manter_pressionado(chave, limite, delta):
        interromper_repeticao()
        def repetir():
            if combo.ligado:
                interromper_repeticao()
                return
            passo_combo(chave, limite, delta)
            botao_repetir["after"] = janela.after(35, repetir)
        botao_repetir["after"] = janela.after(300, repetir)

    for linha, (texto, chave, limite) in enumerate(controles_combo, 1):
        ctk.CTkLabel(combo_frame, text=texto, anchor="w").grid(
            row=linha, column=0, sticky="w", padx=4, pady=8)
        variavel = ctk.StringVar(value=str(config[chave]))
        campos_combo[chave] = variavel
        ctk.CTkEntry(combo_frame, textvariable=variavel, width=100,
                     justify="center").grid(row=linha, column=1, sticky="ew", padx=4)
        for coluna, sinal, passo in ((2, "-", -1), (3, "+", 1)):
            botao = ctk.CTkButton(combo_frame, text=sinal, width=35,
                                  command=lambda c=chave, l=limite, d=passo:
                                      passo_combo(c, l, d))
            botao.grid(row=linha, column=coluna, padx=2)
            botao.bind("<ButtonPress-1>", lambda e, c=chave, l=limite, d=passo:
                       manter_pressionado(c, l, d), add="+")
            botao.bind("<ButtonRelease-1>", interromper_repeticao, add="+")
            botao.bind("<Leave>", interromper_repeticao, add="+")

    recarga_combo = ctk.BooleanVar(value=config["combo_recarga_ativa"])
    ctk.CTkCheckBox(combo_frame, text="Ativar recarga da magia 3",
                    variable=recarga_combo).grid(
                        row=5, column=0, columnspan=4, sticky="w", padx=4, pady=8)
    status_combo = ctk.CTkLabel(combo_frame, text=combo.status,
                               wraplength=350, text_color=COR_VERDE_LABEL)
    status_combo.grid(row=7, column=0, columnspan=4, pady=8)
    ctk.CTkLabel(combo_frame, text="F6 Liga/desliga · F9 Para tudo\n"
                 "Segure o botao direito do mouse no MU.",
                 font=("Segoe UI", 12), text_color=COR_VERDE_NEON).grid(
                     row=8, column=0, columnspan=4, pady=8)

    def salvar_combo():
        if combo.ligado:
            return False
        try:
            novos = {chave: int(campos_combo[chave].get())
                     for _, chave, _ in controles_combo}
            novos["combo_recarga_ativa"] = bool(recarga_combo.get())
            validar_combo(novos)
            combo.configurar(novos)
        except (ValueError, RuntimeError) as erro:
            combo.status = "Ajuste invalido: " + str(erro)
            status_combo.configure(text=combo.status)
            return False
        config.update(novos)
        salvar_config(config)
        combo.status = "Ajustes salvos. Volte ao MU e pressione F6."
        status_combo.configure(text=combo.status)
        return True

    ctk.CTkButton(combo_frame, text="Salvar ajustes",
                  command=salvar_combo).grid(row=6, column=0, columnspan=4, pady=10)
    ultimo_combo = None
    ultimo_drop = None
    ultimo_estado = None

    def atualizar_titulo():
        nonlocal ultimo_estado, ultimo_drop, ultimo_combo
        estado_drop = (drop.ligado, drop.status, tuple(drop.pontos.items()))
        if estado_drop != ultimo_drop:
            ultimo_drop = estado_drop
            status_drop.configure(text=drop.status)
            for ponto, label in pontos_labels.items():
                label.configure(text=str(drop.pontos.get(ponto, "Não marcado")))
            campo_intervalo.configure(state="disabled" if drop.ligado else "normal")
            check_recolher.configure(state="disabled" if drop.ligado else "normal")
        estado_combo = (combo.ligado, combo.status)
        if estado_combo != ultimo_combo:
            ultimo_combo = estado_combo
            status_combo.configure(text=combo.status)
        ligado, erro = clicker.estado()
        estado_visual = (ligado, erro, config["modo"], config["botao"],
                         controle.aba, estado_drop, estado_combo)
        if estado_visual == ultimo_estado:
            return
        ultimo_estado = estado_visual
        combo_botao.configure(state="disabled" if ligado else "readonly")
        combo_modo.configure(state="disabled" if ligado else "readonly")
        combo_velocidade.configure(
            state="disabled" if config["modo"] == "pressionar" else "readonly"
        )
        if controle.aba == "LK Drop":
            janela.title("LK Drop · " + ("Ativo" if drop.ligado else "Parado"))
        elif controle.aba == "LK Combo":
            janela.title("LK Combo · " + ("Ativo" if combo.ligado else "Parado"))
        if ligado:
            if controle.aba == "Auto Click":
                janela.title(TITULO_LIGADO)
            status_label.configure(
                text="● Ativo · " + ("Direito" if config["botao"] == "right" else "Esquerdo"),
                text_color=COR_VERDE_NEON
            )
        else:
            if controle.aba == "Auto Click":
                janela.title(TITULO_DESLIGADO)
            status_label.configure(
                text="Erro: use F9 para liberar" if erro else TEXTO_STATUS_DESLIGADO,
                text_color=COR_VERMELHO_STATUS
            )

    def alternar():
        comandos.put("esquerdo")

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
    atalhos.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    atalhos.grid_columnconfigure((0, 1, 2), weight=1, uniform="atalhos")
    for coluna, tecla, descricao, cor, fundo in (
        (0, "F6", "Esquerdo", "#45d99a", "#203c32"),
        (1, "F8", "Direito", "#45d99a", "#203c32"),
        (2, "F9", "Parar tudo", "#ff8282", "#3d292d"),
    ):
        bloco = ctk.CTkFrame(atalhos, fg_color=fundo, border_color=cor,
                             border_width=1, corner_radius=8)
        bloco.grid(row=0, column=coluna, sticky="ew",
                   padx=4)
        ctk.CTkLabel(bloco, text=tecla, height=20, text_color=cor,
                     font=("Segoe UI", 15, "bold")).pack(pady=(3, 0))
        ctk.CTkLabel(bloco, text=descricao, height=18,
                     text_color="#e4e9ee", font=("Segoe UI", 11)).pack(pady=(0, 6))

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
            else:
                if comando == "esquerdo" and controle.aba == "LK Drop" and not drop.ligado:
                    salvar_drop()
                    try:
                        drop.intervalo = int(intervalo_drop.get())
                    except ValueError:
                        drop.intervalo = 0
                if comando == "esquerdo" and controle.aba == "LK Combo" and not combo.ligado:
                    if not salvar_combo():
                        continue
                resultado = controle.comando(comando)
                if (resultado and comando in ("esquerdo", "direito")
                        and controle.aba == "Auto Click"):
                    # Atalho escolhe botao sem passar pelo seletor visual desabilitado.
                    if config["botao"] != clicker.botao:
                        config["botao"] = clicker.botao
                        combo_botao.set("Esquerdo" if clicker.botao == "left" else "Direito")
                        salvar_config(config)
        atualizar_titulo()
        janela.after(50, processar_comandos)

    def fechar():
        nonlocal fechando
        if not controle.parar() or not clicker.parar():
            atualizar_titulo()
            return
        fechando = True
        keyboard.unhook_all_hotkeys()
        janela.destroy()

    # Capturas são enfileiradas: nenhum callback do keyboard acessa Tk.
    keyboard.add_hotkey("F2", lambda: comandos.put("box"))
    keyboard.add_hotkey("F3", lambda: comandos.put("ground"))
    keyboard.add_hotkey(ATALHO_ALTERNAR, alternar)
    keyboard.add_hotkey(ATALHO_DIREITO, lambda: comandos.put("direito"))
    keyboard.add_hotkey(ATALHO_PARAR, lambda: comandos.put("parar"))
    atualizar_titulo()
    janela.after(50, processar_comandos)

    janela.protocol("WM_DELETE_WINDOW", fechar)
    try:
        mouse_fisico.start()
        janela.mainloop()
    finally:
        mouse_fisico.stop()
        drop.parar()
        combo.parar()
        clicker.parar()
        keyboard.unhook_all_hotkeys()
