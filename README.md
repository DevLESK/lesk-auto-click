# Auto Clicker

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
- Selecionar o desenho não liga a automação. Apenas um botão é automatizado por vez; F6 liga/desliga e F8 para.
- O seletor aceita foco por Tab e seleção pelas setas esquerda/direita.
- **F6** liga/desliga; **F8** interrompe e libera o botão. Os atalhos disparam ao pressionar a tecla, como na versão original; use toques curtos. Há também um botão Ligar / Desligar na janela.
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
