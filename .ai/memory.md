# Memória do Projeto

Projeto: Auto Clicker

Objetivo:
Manter e evoluir um Auto Clicker em Python com foco em estabilidade, clareza e segurança.

Tecnologias:
- Python
- CustomTkinter
- PyAutoGUI
- Keyboard
- PyInstaller

Decisões atuais:
- O F6 deve continuar ligando e desligando o clicker.
- As configurações devem ser preservadas.
- Alterações devem ser pequenas.
- Nenhuma publicação deve ocorrer sem aprovação.
- O Codex deve entregar diff, testes, riscos e próximos passos.

## Decisões e histórico

- A Sprint 001 fortaleceu carregar_config().
- config.json agora é recriado quando ausente ou inválido.
- Chaves ausentes são preenchidas.
- Configurações válidas e chaves extras são preservadas.
- A entrega foi aprovada.
- Toda entrega futura deve incluir resumo, arquivos, diff, motivo técnico, testes, resultados, riscos e próximos passos.
- A Sprint 002 criou testes automatizados para config.py usando unittest.
- Os testes de config.py usam diretório temporário e não alteram permanentemente o config.json real do projeto.
- A Sprint 002 validou arquivo ausente, JSON inválido, JSON não objeto, chave ausente, valores válidos e chaves extras.
- A Sprint 003 reduziu a responsabilidade de gui.py sem alterar o comportamento do Auto Clicker.
- ui_constants.py centraliza textos fixos, cores, fontes, dimensões, ícone, hotkey, velocidades e intervalos.
- caminho_recurso() permanece em gui.py.
- main.py, clicker.py, config.py, config.json, AutoClick.spec e requirements.txt não foram alterados na Sprint 003.

- Sprint 004: seleção esquerdo/direito e repetir/pressionar; F6 preservado e F8 para parada.
- Configurações antigas recebem padrões; início sempre desligado.
- Operações de mouse serializadas para impedir pressão após parada; liberação tentada nas saídas controladas.
- Testes automatizados simulam mouse e GUI. Validação Windows/Mu e executável permanecem pendentes.
- Sem QWE, atualizador, novas dependências, merge ou Release nesta etapa.


Correção após teste manual: André relatou janela engasgando ao arrastar e F6 demorado.
A interface reconfigurava widgets 20 vezes por segundo mesmo sem mudança de estado.
Agora só redesenha quando ligado/erro/modo mudam. Cliques repetidos não usam a
pausa automática adicional do PyAutoGUI dentro do lock; o intervalo configurado
continua controlando a cadência. Teste de regressão cobre polls ociosos sem redraw.
Validação de fluidez no Windows permanece pendente.

F6 ainda não ativou no teste manual de André na versão c456370. Restaurado disparo ao pressionar (comportamento original) e adicionado botão Ligar / Desligar para uso e diagnóstico independente do atalho. Validação real permanece pendente.


Seletor visual aprovado por André: desenho de mouse clicável, seleção exclusiva
esquerda/direita em verde, bloqueada durante execução. F6 alterna o escolhido;
F8 somente para. Sem automação simultânea ou ativação por clique físico no jogo.
Adicionado mouse_selector.py com Canvas do Tkinter, sem dependências novas.
25 testes simulados aprovados, compilação e diff verificados.
André confirmou versão anterior funcional no Roblox/Mu com elevação; nova
interface aguarda inspeção visual e teste manual no Windows. Sem merge/Release.

Ajuste visual solicitado: janela 280x420 (antes 320x600), mouse compacto com silhueta arredondada, seleção verde discreta e espaçamento reduzido. Título LESK AUTO CLICK. Sem alterações no motor/atalhos; validação visual no Windows pendente.

André informou clique repetido funcional fora do Mu e sem registro dentro dele, mesmo com VS Code elevado. Hipótese de duração insuficiente: substituído clique instantâneo por mouseDown, pressão de 50 ms e mouseUp; modo pressionado preservado. Não há confirmação de correção no Mu. Testes simulados de sequência/liberação e falhas adicionados.

Acabamento após screenshot de André: mouse rasterizado em 4x com Pillow já existente e redução LANCZOS; legenda fora do corpo; seletores unificados; organização em grid com botão de 32 px e margens. Janela 280x420 preservada. Mouse visualmente inspecionado; janela completa no Windows pendente. 29 testes passaram. Motor e atalhos não alterados.

Pedido de André: removidos nomes laterais e legenda textual do mouse; seleção indicada visualmente pelo verde. Janela reduzida para 280x400 aproveitando a remoção da legenda.

Refinamento solicitado: mouse com silhueta ergonômica em curvas Bézier, botões separados, rodinha detalhada, contornos suaves e verde exclusivo na seleção. Sem alterações funcionais ou de tamanho da janela.

Implementação da arte Gamer aprovada: dois PNGs transparentes com LK verde metálico e braços do K em branco. Seletor usa imagem correspondente ao botão escolhido, sem textos laterais. Campos Modo/Velocidade alinhados em duas linhas e título LK AUTO CLICK. Janela 280x400. Incluídos recursos no AutoClick.spec e resolução por _MEIPASS para o executável. 30 testes simulados passaram; aparência completa/escala no Windows e novo executável pendentes. Motor e atalhos preservados.
