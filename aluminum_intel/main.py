"""Ponto de entrada para execução completa da inteligência de compras.

O script orquestra coleta de dados, cálculo de custos, análises estatísticas e
geração de insights. Toda a comunicação é feita em português e nenhuma
informação é inventada: quando dados não estão disponíveis, o relatório indica
as lacunas correspondentes.
"""

from __future__ import annotations

from typing import Dict

from aluminum_intel import analytics, cost_model, data_layer, inteligencia


DEFAULT_PARAMETROS = {
    "percentil_baixo": 0.3,
    "percentil_alto": 0.7,
    "estoque_alto": 500_000.0,
    "estoque_baixo": 250_000.0,
}



def executar_fluxo(parametros: Dict[str, float] | None = None) -> Dict[str, object]:
    """Executa o fluxo completo e devolve o relatório estruturado."""

    parametros = parametros or DEFAULT_PARAMETROS

    snapshot = data_layer.get_aluminum_market_snapshot()
    resumo_analytics = analytics.gerar_resumo_analytics(
        snapshot.get("history_usd_t"), snapshot.get("lme_3m_usd_t"), snapshot.get("lme_cash_usd_t")
    )

    custos = cost_model.calcular_custo_aluminio(
        lme_cash_usd_t=snapshot.get("lme_cash_usd_t"),
        lme_3m_usd_t=snapshot.get("lme_3m_usd_t"),
        premios_usd_t=None,
        frete_usd_t=None,
        outros_custos_usd_t=None,
    )

    insights = inteligencia.gerar_insights_compra(snapshot, resumo_analytics, parametros)

    return {
        "snapshot": snapshot,
        "analytics": resumo_analytics,
        "custos": custos,
        "insights": insights,
    }


def imprimir_relatorio(resultado: Dict[str, object]) -> None:
    """Imprime um relatório resumido em português para o terminal."""

    snapshot = resultado["snapshot"]
    analytics_resumo = resultado["analytics"]
    custos = resultado["custos"]
    insights = resultado["insights"]

    print("===== INTELIGÊNCIA DE COMPRAS - ALUMÍNIO 6061 =====")
    print(f"Data de atualização: {snapshot.get('data_atualizacao')}")
    print("\n--- Cotações ---")
    print(f"LME Cash (USD/t): {snapshot.get('lme_cash_usd_t')}")
    print(f"LME 3M (USD/t): {snapshot.get('lme_3m_usd_t')}")
    print(f"Estoque LME (t): {snapshot.get('lme_stock_t')}")
    print(f"FX PTAX BRL/USD: {snapshot.get('fx_spot_brl_usd')}")
    print(f"Spot Metals.Dev (USD/t): {snapshot.get('spot_metals_dev_usd_t')}")

    print("\n--- Custos ---")
    print(f"Referência LME utilizada (USD/t): {custos.get('lme_referencia_usd_t')}")
    print(f"Prêmios (USD/t): {custos.get('premios_usd_t')}")
    print(f"Frete (USD/t): {custos.get('frete_usd_t')}")
    print(f"Outros custos (USD/t): {custos.get('outros_custos_usd_t')}")
    print(f"Custo total estimado (USD/t): {custos.get('custo_total_usd_t')}")

    print("\n--- Analytics ---")
    print(f"Spread 3M - Cash (USD/t): {analytics_resumo.get('spread_3m_cash')}")
    print(f"Percentil LME: {analytics_resumo.get('percentil_lme')}")
    print(f"Estrutura da curva: {analytics_resumo.get('estrutura_curva')}")
    print(f"Volatilidade anualizada: {analytics_resumo.get('volatilidade')}")

    print("\n--- Insights ---")
    for insight in insights:
        print(f"- {insight}")

    if snapshot.get("warnings") or custos.get("warnings"):
        print("\n--- Avisos ---")
        for aviso in snapshot.get("warnings", []):
            print(f"[DADOS] {aviso}")
        for aviso in custos.get("warnings", []):
            print(f"[CUSTO] {aviso}")


if __name__ == "__main__":
    resultado = executar_fluxo()
    imprimir_relatorio(resultado)
