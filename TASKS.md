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
