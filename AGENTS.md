# AGENTS.md – Regras e Instruções para o OpenAI Codex

## Objetivo do Projeto
Este repositório contém o desenvolvimento de uma ferramenta completa de INTELIGÊNCIA DE COMPRAS
para Alumínio Extrudado Liga 6061, composta por módulos de dados, custos, análise
histórica e geração de insights estratégicos. O foco é uso real em indústria
(Fundiferro / Consultoria Tinti).

O Codex deve:
- Criar e manter a arquitetura especificada abaixo.
- Nunca inventar valores de mercado.
- Trabalhar sempre com isolamento, boas práticas e modularidade limpa.

---

## Estrutura Final do Projeto

O Codex deve criar e manter a seguinte estrutura:

aluminum_intel/
data_layer.py
cost_model.py
analytics.py
inteligencia.py
main.py
README.md
AGENTS.md
requirements.txt

yaml
Copiar código

A pasta **aluminum_intel/** concentra toda a lógica Python do sistema.

---

## Regras Fundamentais

1. **Nunca inventar dados**  
   - Dados de mercado devem vir de:
     - WestMetall (scraping)
     - Metals.Dev (API)
     - yfinance (ALI=F)
     - PTAX (BCB)
   - Se qualquer fonte falhar: retornar None e registrar warnings.

2. **Não usar valores médios, típicos, estimados ou supostos.**

3. **Cumprir exatamente a arquitetura:**
   - data_layer.py → captura e consolida dados externos
   - cost_model.py → cálculo all-in do alumínio 6061
   - analytics.py → percentis, curva, volatilidade
   - inteligencia.py → heurísticas de apoio à decisão
   - main.py → execução e relatório

4. **Linguagem e documentação sempre em português.**

---

## Especificação dos Arquivos

### 1. data_layer.py
Funções obrigatórias:
- get_lme_from_westmetall()
- get_aluminum_from_metalsdev(symbols)
- get_ali_f_from_yfinance()
- get_ptax_brl_usd()
- get_aluminum_market_snapshot()

Snapshot deve conter:
{
"lme_cash_usd_t": float | None,
"lme_3m_usd_t": float | None,
"lme_stock_t": float | None,
"fx_spot_brl_usd": float | None,
"history_usd_t": pandas.Series | None,
"sources_used": dict,
"warnings": list[str]
}

yaml
Copiar código

### 2. cost_model.py
Função principal:
- calcular_custo_aluminio(...)

Regras confirmadas do setor:
- base = LME (3M ou Cash) + prêmios (inputs) + fretes (inputs)
- nada de valores fixos ou supostos.

### 3. analytics.py
Funções obrigatórias:
- calcular_percentil_preco()
- calcular_spread_3m_cash()
- classificar_estrutura_curva()
- calcular_volatilidade()

### 4. inteligencia.py
Função obrigatória:
- gerar_insights_compra(snapshot, analytics, parametros_regra)

Regras:
- preço barato = percentil baixo
- estoque alto = oferta confortável
- curva contango/backwardation = interpretação clássica
- Nada é “previsão”, apenas apoio à decisão.

### 5. main.py
Executa:
- captura de dados
- cálculo do custo
- cálculos estatísticos
- geração de insights
- impressão de relatório final em português

---

## Regras de Estilo e Boas Práticas

- Sempre modularizar.
- Nunca misturar scraping, lógica e interface.
- Sempre registrar warnings quando faltar informação.
- Terminal e prints sempre em português.
- Código limpo, comentado e fácil de testar.

---

## Comandos esperados do usuário
O Codex deve aceitar comandos como:

- “Criar todos os arquivos do sistema conforme AGENTS.md”
- “Atualizar data_layer.py mantendo regras do AGENTS.md”
- “Melhorar o main.py seguindo a arquitetura”
- “Criar testes unitários para analytics.py”

---

## IMPORTANTE
Este AGENTS.md substitui prompts extensos.  
O Codex deve **ler este arquivo automaticamente** e seguir **todos** os requisitos aqui definidos.
