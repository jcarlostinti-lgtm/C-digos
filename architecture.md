# Arquitetura do Sistema – Alumínio 6061

```mermaid
flowchart LR
    A[WestMetall] --> D[data_layer.py]
    B[Metals.Dev] --> D
    C[yfinance ALI=F] --> D
    P[PTAX BCB] --> D

    D --> S[snapshot]
    S --> CM[cost_model.py]
    S --> AN[analytics.py]

    AN --> IN[inteligencia.py]
    CM --> IN

    IN --> M[main.py]
yaml
Copiar código

---

# 🔥 PRONTO PARA O USO

Agora você tem **os 5 componentes perfeitos** para:

- organizar o repositório  
- permitir que o Codex entenda tudo automaticamente  
- trabalhar com máxima qualidade  
- gerar código com a arquitetura definida  

---

# ❓ Quer que eu gere também:

### ✔ os 5 arquivos **já montados como PR para enviar ao GitHub**?  
### ✔ ou quer que eu **crie os arquivos automaticamente via Codex** usando seu ambiente?

Me diga **qual opção prefere**.






