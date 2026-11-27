# S02.1 — Instrumentação opcional do Combo DL (diagnóstico)

## Limites
- Apenas diagnóstico experimental; não confirma reconhecimento das teclas pelo MU.
- `combo.py` preserva sequência 1→2→3→1, recarga, agendamento e limites existentes.
- Por padrão `LKCombo(...)` **não** instancia nem utiliza instrumentação.
- Não inclui botão na GUI, atalho ou gravação automática.
- Sem novas dependências, sem servidor, sem dados de PC/licença, sem captura de entradas externas.

## Como ativar num teste técnico Windows futuro
1. Trabalhar em cópia/branch de homologação, nunca na main.
2. Instanciar `DiagnosticoCombo()` de `combo_diagnostico` e passar `diagnostico=coletor` ao construtor existente de `LKCombo` num ambiente de teste controlado.
3. Executar o Combo DL nas mesmas condições e tempos do perfil atual, verificando foco e saída segura.
4. **Parar o combo antes de exportar**, e então executar `coletor.exportar_csv("combo_diagnostico.csv")`.
5. Comparar `agendar`, `callback`, `tecla_down` e `tecla_up` e os atrasos registrados, em especial perto de `3→1`. Identificar falha visual por gravação do MU com os mesmos horários.

A ativação acima é via integração técnica programática: a GUI atual **não possui chave para diagnóstico**. O teste com o executável existente não produzirá arquivos CSV.

## CSV
Campos: `tempo_ns,evento,tecla,espera_ms,atraso_ms`.
- `tempo_ns`: contador monotônico de alta resolução; não é horário de calendário.
- `agendar`: início de espera solicitado.
- `callback`: execução após prazo; `atraso_ms` indica atraso observado pelo processo.
- `tecla_down` e `tecla_up`: retorno da chamada de envio de entrada; **não** é confirmação do jogo.
- `tecla_up_parada`: tentativa de liberação realizada na parada.

O coletor guarda até 20.000 eventos por padrão e descarta os mais antigos ao exceder o limite, contabilizando `descartados`. A exportação escreve no disco somente quando invocada explicitamente e com o combo parado.

## Validação
`python -m unittest discover -s tests -v`

Os testes simulam agendamentos e atrasos; não medem desempenho real do Tk/Windows. A CI empacota um EXE experimental por configuração histórica do workflow; **não distribuir**.
