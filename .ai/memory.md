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
