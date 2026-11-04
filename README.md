# Auto Clicker

> **LESK Tools — Sprint 1 (PR #4):** na aba **Auto Click**, **F6**
> liga/desliga o esquerdo e **F8** liga/desliga o direito.
> A troca solta o botao anterior automaticamente. **F9** e a parada geral
> para todos os modulos. Nas abas **LK Drop** e **LK Combo**, **F6**
> continua iniciando/parando a funcao selecionada; **F8** nao tem acao.
> Todas as automacoes param ao trocar de aba. As instrucoes historicas
> a seguir descrevem etapas anteriores; para este prototipo, prevalecem
> os atalhos deste aviso.


## Projeto

Auto Clicker desenvolvido em Python para automação de cliques.

## Objetivo

Criar um Auto Clicker estável, rápido, organizado e fácil de evoluir.

## Tecnologias

- Python
- CustomTkinter
- PyAutoGUI
- Keyboard
- PyInstaller

## Estrutura

main.py → inicia a aplicação

gui.py → interface

clicker.py → lógica dos cliques

config.py → configurações

config.json → preferências do usuário

## Status

Versão 1.0

## Próximas melhorias

- [ ] Melhorar interface
- [ ] Criar testes
- [ ] Adicionar logs
- [ ] Criar atualizador
- [ ] Melhorar arquitetura

## Seleção de botão e modo (em validação)

- Clique na metade **Esquerdo** ou **Direito** do desenho do mouse; a seleção fica verde. Depois escolha **Cliques repetidos** ou **Manter pressionado**.
- Selecionar o desenho não liga a automação. Apenas um botão é automatizado por vez; F6 controla esquerdo, F8 controla direito e F9 para.
- O seletor aceita foco por Tab e seleção pelas setas esquerda/direita.
- **F6** liga/desliga; **F8** interrompe e libera o botão. Os atalhos disparam ao pressionar a tecla, como na versão original; use toques curtos. A ativação é feita apenas pelos atalhos F6/F8, sem botão na janela.
- O aplicativo sempre inicia desligado. Posicione o mouse no destino antes de ativar.
- Botão e modo ficam bloqueados enquanto estiver ligado. A velocidade só se aplica aos cliques repetidos.
- Preferências antigas são completadas automaticamente com esquerdo/cliques repetidos; escolhas e chaves extras são preservadas.
- Os comandos afetam o cursor atual do Windows; não estão vinculados à janela de um jogo.
- Encerramento normal e falhas controladas tentam liberar o botão pressionado. Encerramento forçado do processo ou falha do sistema não oferece essa garantia.
- A liberação no canto de failsafe usa o backend interno do PyAutoGUI apenas para soltar o botão; validar novamente se atualizar essa biblioteca.

### Testes automatizados

```powershell
python -m unittest discover -s tests -v
python -m compileall -q main.py gui.py mouse_selector.py clicker.py config.py ui_constants.py
```

Os testes de mouse e interface usam simulações, sem emitir entradas reais.

### Teste manual no Windows (pendente)

1. Execute `python main.py`. Confirme que inicia desligado e restaura preferências.
2. Teste clique esquerdo/direito repetido nas três velocidades em uma área de teste.
3. Teste manter pressionado com cada botão. Confirme uma pressão contínua e liberação por F6 e F8.
4. Feche enquanto estiver pressionando; confirme que soltou. Teste alternâncias rápidas.
5. Confirme seletores bloqueados durante execução, velocidade desabilitada no modo pressionado e status coerente.
6. No Mu, selecione Direito/Manter pressionado, posicione o cursor e use F6. Verifique magia e parada antes de distribuir.

### Gerar o executável no Windows

Na pasta do projeto, com ambiente virtual ativado e dependências instaladas:

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller --clean --noconfirm AutoClick.spec
```

O resultado esperado é `dist/AutoClick.exe`. Teste também o executável e suas preferências antes de compartilhar. Não há atualização automática, QWE nem Release nesta etapa.

### Compatibilidade observada

André confirmou funcionamento no Roblox e no Mu após executar o aplicativo com elevação. Se o jogo roda como administrador e os atalhos não respondem nele, teste o aplicativo com o mesmo nível de permissão. Isso não exige desativar proteções do jogo. O teste anterior foi funcional; o novo seletor visual ainda precisa de validação no Windows.

Cliques repetidos agora mantêm o botão pressionado por 50 ms antes de soltar, além do intervalo selecionado entre cliques. É um ajuste de compatibilidade para aplicativos que não observam pressão/soltura instantâneas. Funcionamento dessa alteração no Mu ainda precisa de teste manual.

Acabamento visual: seletor de mouse suavizado com Pillow (dependência já utilizada pelo projeto), legenda externa e campos padronizados. Layout em grid preserva espaço para o botão inferior. Validação de escala/DPI e aparência completa no Windows permanece pendente.

### Arte Gamer LK

As imagens `assets/mouse_left.png` e `assets/mouse_right.png` representam as duas seleções e são incluídas pelo `AutoClick.spec`. O programa encontra os recursos tanto pelo código-fonte como no diretório temporário do PyInstaller. Artes geradas a partir do conceito visual aprovado por André; não são fotografias de hardware. Nenhuma alteração no motor dos cliques ou nos atalhos nesta etapa. A versão executável precisa ser reconstruída no Windows após validar o visual.

A interface usa ícone LK, título curto e status com o botão ativo. F6 alterna e F8 para; selecionar o mouse não ativa a execução.

### Interromper manualmente o modo pressionado

No Windows, um clique físico no mesmo botão selecionado interrompe apenas o modo **Manter pressionado**, e o status volta a desligado. F6 retoma. O outro botão permanece livre para uso manual. **Cliques repetidos não são alterados por cliques físicos.** O observador ignora eventos marcados pelo Windows como injetados e é removido ao encerrar. Essa integração requer teste manual na máquina Windows; testes automatizados simulam os eventos.

## Aplicativo unificado: Auto Click e LK Drop

O Auto Click usa **F6** para esquerdo e **F8** para direito. O Drop usa **F6**
para ligar/desligar. **F9** para tudo em qualquer aba. Trocar de aba interrompe a automação anterior e libera suas entradas.
O aplicativo inicia desligado; somente uma função pode executar por vez.
O Auto Click mantém o mouse LK, opções e comportamento anterior.

### LK Drop

1. Selecione a aba **LK Drop** e coloque o jogo em primeiro plano.
2. Posicione o cursor sobre a box no inventário e pressione **F2**.
3. Posicione o cursor no ponto do chão e pressione **F3**.
4. Use **F6** no jogo para iniciar; **F9** para parar.

O ciclo move até a box, clica, move até o chão, clica e, opcionalmente,
pressiona Espaço cinco vezes. O intervalo entre ações inicia em **50 ms**
(faixa permitida: 20–5000 ms). Cada clique permanece pressionado por **100 ms**;
Espaço permanece pressionado por **180 ms**, com **180 ms** entre pressões.
50 ms foi validado pelo usuário no programa separado; a integração precisa de
novo teste no Windows/MU. Intervalos menores podem falhar no jogo.

F2/F3 funcionam somente com Drop parado e uma janela externa em foco.
Marcar um ponto em outra janela limpa os pontos anteriores. Os pontos e a janela
alvo duram apenas a sessão; nunca são salvos. Intervalo e coleta são preferências
persistidas junto das configurações antigas. A posição é fixa na tela: marque
novamente se mover a janela ou o inventário. Ao perder o foco do jogo, o Drop
para e libera as entradas. Volte ao jogo e use F6 para retomar do início do ciclo.

Não há detecção de pilha vazia ou inventário cheio. Quando acabar a pilha, pare,
coloque outra no mesmo local e retome. As capturas aceitam uma janela externa;
o aplicativo não identifica automaticamente qual processo é o MU.

### Validação da integração

```powershell
python -m unittest discover -s tests -v
python -m compileall -q main.py gui.py drop.py drop_windows.py automation.py config.py
python -m PyInstaller --clean --noconfirm AutoClick.spec
```

Os novos módulos Python são incluídos automaticamente pelo PyInstaller; o
executável continua em `dist/AutoClick.exe`, contendo as duas funções e os assets
LK existentes. Testes simulados não precisam de Windows e não enviam entradas.

Antes de distribuir, teste no Windows: captura F2/F3 com jogo em foco, ciclo com e
sem coleta a 50 ms, F6/F9 nas duas abas, troca de aba enquanto mouse/Espaço estão
pressionados, perda de foco em cada etapa e fechamento durante execução. Confirme
que o ícone e a arte aparecem no novo executável. Esta integração não publica
Release nem instala atualização automática.


## LESK Tools — Auto Click + LK Drop + LK Combo (piloto da guild)

Branch de integracao: `feat/lesk-tools-combo-licencas`. Este trabalho ainda nao
esta integrado a `main` e nao deve ser distribuido sem testes no Windows/MU.

- Abas: Auto Click, LK Drop e LK Combo; F6 alterna Drop/Combo ou controla esquerdo no Auto Click; F8 controla direito no Auto Click; F9 para tudo.
- Auto Click: preservados modos repetido/pressionado, botao e velocidades.
- LK Drop: F2 marca a box, F3 marca o chao, coleta com cinco Espacos opcional.
- LK Combo DL/BK: tecla 1, 2, 3; toque 0–200 ms, intervalo 0–200 ms,
  espera apos magia 3 de 0–100 ms e recarga opcional de 0–15000 ms.
  Sem recarga: 1-2-3 continuo. Com recarga: 1-2-3-1, espera o saldo
  de recarga contado do fim da magia 3, e reinicia em 2-3-1.
  O clique direito permanece **manual**, como na versao separada.
- So uma automacao roda de cada vez. Sair da janela alvo interrompe
  o Drop/Combo. Selecionar outra aba para qualquer automacao em execucao.
- Apos configurar o Combo, use "Salvar ajustes", volte ao jogo e pressione F6.

### Licencas offline para a guild

O aplicativo valida uma licenca `.lesk` assinada com Ed25519 e vinculada
ao codigo resumido do computador. Sem uma licenca valida, a interface de
automacao nao e iniciada. O codigo exibido nao contem o MachineGuid bruto.

1. Usuario abre o EXE, clica em "Copiar codigo do PC" e manda ao admin.
2. Admin executa `gerar_licenca.py` com sua chave PRIVADA guardada fora do GitHub.
3. Admin envia apenas `licenca.lesk` ao usuario.
4. Usuario clica em "Importar arquivo de licenca" e escolhe o `.lesk`.
5. Licenca e salva em `%APPDATA%/LESKTools/license.lesk`.

A chave privada NAO e fornecida pelo repositório. A chave publica ja esta
embutida em `licensing.py`; licencas so podem ser geradas com a correspondente
chave privada do proprietario. Nunca inclua essa chave no EXE, em commits,
prints ou arquivos enviados a jogadores.

Limites: o sistema **nao possui servidor**, portanto revogacao imediata
remota nao existe; a vigencia opcional controla expiracao. Mudancas de
instalacao do Windows podem exigir nova emissao. Software desktop pode
ser modificado por engenharia reversa: nao existe protecao absoluta.

### Validacao e compilacao

No Windows, em ambiente de desenvolvimento:
```powershell
py -3 -m pip install -r requirements.txt
py -3 -m unittest discover -s tests -v
py -3 -m PyInstaller --clean --noconfirm AutoClick.spec
```

A branch possui fluxo GitHub Actions de build em Windows para testes, com
arquivo `LESK-Tools-Windows-prototipo` apos sucesso. O EXE nao foi
testado no cliente do MU por esse fluxo. Antes de entregar aos jogadores,
testar liberacao F8 com cada motor, as 3 teclas em diferentes servidores,
janela sem foco, 0 ms, ativacao, expiracao e reinstalacao. Respeitar as
regras de automacao de cada servidor de MU.
