# LESK Tools — S02.2: preparar coleta no Windows (somente homologação)

## Objetivo
Registrar atrasos de agendamento e chamadas das teclas do Combo DL, sem mudar o motor. O instrumento mede **o processo LESK Tools**, não a aceitação das magias pelo MU.

## Restrição importante
A S02.2 foi implementada somente na branch de homologação `feat/lesk-tools-s02-2-coleta-windows`. **Não há merge nem Release autorizados.** Não utilizar artefatos da CI como distribuição para a guild.

## Como habilitar os controles — teste futuro
No Windows, com uma versão de homologação construída especificamente a partir desta branch e devidamente aprovada pelo Tech Lead:

1. Fechar o LESK Tools.
2. No Prompt de Comando da sessão de teste, definir `set LESK_TOOLS_DIAGNOSTICO=1`.
3. Iniciar o aplicativo nessa mesma sessão. Por padrão (sem a variável ou com outro valor), os controles **não aparecem**.
4. Entrar na aba **LK Combo**, ajustar e salvar o perfil de tempos antes de iniciar a coleta.
5. Com o Combo parado, clicar **Ligar / desligar coleta (homologação)** para ativar.
6. Voltar ao MU e acionar o Combo DL normalmente (F6). Se ocorrer a falha visual, registrar a observação separadamente.
7. Parar com **F9** e verificar que as entradas foram liberadas. Voltar à aba LK Combo.
8. Clicar **Ligar / desligar coleta** novamente para desativar.
9. Clicar **Exportar CSV após F9** e escolher o destino. O programa grava `nome.csv` e `nome.perfil.txt`.

O CSV tem `tempo_ns,evento,tecla,espera_ms,atraso_ms`; o perfil registra somente o tempo de toque, intervalo, após terceira magia, recarga e se ela está ativa, além de eventos descartados.

## Segurança e limitações
- A coleta é sempre **desligada por padrão**. Não usa keylogger ou captura de outros aplicativos.
- A exportação é proibida enquanto o Combo está ligado, se a coleta ainda está ligada ou se houver tecla marcada como pressionada.
- Os registros ficam só na memória, limitados a 20.000 eventos por padrão, e são descartados ao fechar o aplicativo sem exportar.
- Uma nova ativação inicia um registro novo. Exporte o anterior antes de iniciar outra coleta.
- O perfil corresponde aos valores do Combo no **momento da ativação da coleta**.
- O CSV contém tempo monotônico, sem relógio de parede. Para correlacionar falhas visuais, anotar manualmente a ocorrência e, se houver vídeo, relacionar por um evento observável; não pressupor sincronização automática.
- O motor não reconhece diretamente se a cavalada foi cortada, portanto o arquivo CSV isolado não comprova a falha.
- O controle é um recurso de homologação, não uma melhoria do Combo, do AutoClick ou do Drop.
- Não existe executável autorizado para compartilhamento: validar primeiro teclado, foco, F9, interface real e impacto de latência no Windows.
