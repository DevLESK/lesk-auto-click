# TASKS

## Sprint 001

### Objetivo
Robustez do carregamento das configurações.

### Status
☑ Concluída

### Responsável
Lesk Core / Codex

### Arquivo alterado
- config.py

### Testes realizados
- Apagar config.json e confirmar recriação automática.
- Colocar JSON inválido e confirmar recriação automática.
- Remover uma chave e confirmar preenchimento automático.
- Confirmar preservação de configurações válidas e chaves extras.
- Compilar os arquivos Python principais.
- Iniciar o programa e confirmar ausência de erro imediato.

### Resultado
Aprovado.

### Data da conclusão
2026-07-10

---

## Sprint 002

### Objetivo
Criar testes automatizados para validar o comportamento de config.py sem alterar o funcionamento do aplicativo.

### Status
☑ Concluída

### Responsável
Lesk Core / Codex

### Arquivos alterados
- tests/test_config.py
- TASKS.md
- .ai/memory.md

### Testes realizados
- config.json inexistente.
- JSON inválido.
- Conteúdo JSON que não seja um objeto.
- Chave ausente.
- Preservação de valores válidos.
- Preservação de chaves extras.
- Confirmação de que o config.json real permaneceu intacto.

### Resultado
Aprovado.

### Data da conclusão
2026-07-10

---

## Tarefa 002

### Objetivo
Melhorar a arquitetura do projeto sem alterar seu funcionamento.

### Status
☑ Concluída na Sprint 003

---

## Sprint 003

### Objetivo
Reduzir a responsabilidade de gui.py sem alterar o comportamento do Auto Clicker.

### Status
☑ Concluída

### Responsável
Lesk Core / Codex

### Arquivos alterados
- gui.py
- ui_constants.py
- TASKS.md
- .ai/memory.md

### Testes realizados
- Testes automatizados existentes.
- Compilação dos arquivos Python.
- Inicialização rápida do aplicativo.

### Resultado
Aprovado.

### Data da conclusão
2026-07-10

---

## Tarefa 003

### Objetivo
Criar testes para validar o Auto Clicker.

### Status
☑ Concluída na Sprint 002

---

## Tarefa 004

### Objetivo
Melhorar a interface gráfica.

### Status
☐ Não iniciado

## Sprint 004 — Botão e modo selecionáveis

- Implementado em branch separada: esquerdo/direito, repetir/manter pressionado, F6 e parada F8.
- Controle serializado do mouse, encerramento e liberação em falhas controladas.
- Migração compatível das configurações; interface mantém atualizações na thread gráfica.
- Testes: 21 aprovados com backend de mouse e interface simulados; compilação Python e diff sem erros.
- Pendente: teste visual/atalhos no Windows, validação no Mu e geração/teste do executável.
- Estado: aguardando revisão; sem merge ou publicação de versão.


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
