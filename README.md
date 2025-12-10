# Inteligência de Compras – Alumínio 6061  
Projeto desenvolvido para estruturar uma ferramenta profissional de cálculo de custo,
monitoramento de mercado, análise estatística e geração de insights estratégicos
para compras industriais de Alumínio Liga 6061, com uso real em Fundiferro e
Consultoria Tinti.

---

## 📦 Estrutura do Projeto

aluminum_intel/
data_layer.py # fontes de dados (WestMetall, Metals.Dev, yfinance, PTAX)
cost_model.py # cálculo all-in do alumínio
analytics.py # percentis, curva, volatilidade
inteligencia.py # apoio à decisão
main.py # execução
AGENTS.md # regras do Codex
requirements.txt # dependências

yaml
Copiar código

---

## 🧠 O que o sistema faz

- Coleta dados reais de mercado:
  - LME Aluminium (Cash, 3M, Estoques)
  - Metals.Dev (spot)
  - yfinance (ALI=F)
  - PTAX (Banco Central)

- Calcula custo **all-in** do alumínio:
  - LME + prêmios + fretes + custos locais

- Avalia condições de mercado:
  - Curva (contango/backwardation)
  - Percentil de preço histórico
  - Estoques LME
  - Volatilidade

- Gera insights:
  - “Janela favorável para antecipar compras”
  - “Mercado apertado – recomenda-se prudência”
  - (sempre como apoio à decisão, nunca como previsão)

---

## ▶ Como executar

Instale dependências:

pip install -r requirements.txt

makefile
Copiar código

Execute:

python aluminum_intel/main.py

yaml
Copiar código

---

## 🛠 Tecnologias utilizadas

- Python 3.10+
- requests
- pandas
- BeautifulSoup4
- yfinance

---

## 📄 Licença

Uso interno (Consultoria Tinti / Fundiferro).
