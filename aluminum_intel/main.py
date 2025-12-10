"""Ponto de entrada para execução da inteligência de compras de alumínio."""

from __future__ import annotations

from pprint import pprint

from aluminum_intel import analytics, cost_model, data_layer, inteligencia


def executar_fluxo():
    """Executa coleta de dados, cálculos e gera um relatório em português."""

    snapshot = data_layer.get_aluminum_market_snapshot()

    analiticos = {
        "spread_3m_cash": analytics.calcular_spread_3m_cash(snapshot),
        "volatilidade": analytics.calcular_volatilidade(snapshot.get("history_usd_t")),
    }

    analiticos["percentil_preco"] = analytics.calcular_percentil_preco(
        snapshot.get("history_usd_t"), snapshot.get("lme_3m_usd_t") or snapshot.get("lme_cash_usd_t")
    )
    analiticos["estrutura_curva"] = analytics.classificar_estrutura_curva(analiticos["spread_3m_cash"])
    analiticos["warnings"] = []

    custos = cost_model.calcular_custo_aluminio(snapshot)

    insights = inteligencia.gerar_insights_compra(snapshot, analiticos)

    print("\n==== SNAPSHOT DE MERCADO ====")
    pprint(snapshot)

    print("\n==== CÁLCULO DE CUSTO ====")
    pprint(custos)

    print("\n==== ANÁLISE ESTATÍSTICA ====")
    pprint(analiticos)

    print("\n==== INSIGHTS ====")
    for item in insights:
        print(f"- {item}")


if __name__ == "__main__":
    executar_fluxo()
