# Travel Agent CLI (Gemini API)

Agente interativo de planejamento de viagens para terminal, desenvolvido em Python com o Google Gemini, Function Calling e um loop ReAct.

## Estrutura do projeto

- `agent.py`: controla a conversa, o loop do agente, as chamadas de ferramentas e os comandos `sair` e `exportar`.
- `tools.py`: implementa as ferramentas de clima, atrações e cálculo de orçamento.
- `requirements.txt`: lista as dependências do projeto.
- `plano_de_viagem.txt`: arquivo gerado pelo comando `exportar`.

## Pré-requisitos

- Python 3.9 ou superior
- Uma chave da API Gemini obtida no [Google AI Studio](https://aistudio.google.com/)

## Instalação

No PowerShell, execute:

```powershell
py -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
```

## Configuração da API

Configure a chave no mesmo terminal em que o agente será executado:

PowerShell:

```powershell
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

Bash ou Zsh:

```bash
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

A chave não deve ser colocada no código nem publicada no GitHub.

## Execução

Com o ambiente virtual ativado:

```powershell
python agent.py
```

Sem ativar o ambiente virtual:

```powershell
& ".\.venv\Scripts\python.exe" agent.py
```

O modelo padrão é `gemini-3.6-flash`. Para usar outro modelo:

```powershell
$env:GEMINI_MODEL="nome-do-modelo"
```

## Funcionalidades

- Cria roteiros de viagem com base no destino, duração e orçamento.
- Consulta a previsão do tempo pela API Open-Meteo.
- Sugere atrações cadastradas no projeto.
- Calcula os custos informados e verifica o orçamento.
- Mantém o histórico da conversa para permitir alterações no roteiro.
- Exporta a conversa para `plano_de_viagem.txt`.

As atrações turísticas atualmente são dados mockados para Rio de Janeiro, São Paulo e Niterói. A previsão do tempo é consultada online pela Open-Meteo.

## Comandos

| Comando | Ação |
| --- | --- |
| `exportar` | Salva o histórico em `plano_de_viagem.txt` e encerra. |
| `sair` | Encerra sem salvar o histórico. |

## Limitações

- O uso da API Gemini está sujeito aos limites de cota da conta.
- É necessária conexão com a internet para consultar o Gemini e a previsão do tempo.
- As atrações e seus preços são estimativas locais, não dados em tempo real.
