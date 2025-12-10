"""Heurísticas de apoio à decisão para compras de alumínio.

Nenhuma função faz previsão; apenas interpreta sinais com base em percentis,
estoques e estrutura de curva.
"""

from __future__ import annotations

from typing import Dict, List, Optional


def gerar_insights_compra(
    snapshot: Dict[str, object],
    analytics: Dict[str, object],
    parametros_regra: Optional[Dict[str, float]] = None,
) -> List[str]:
    """Gera insights qualitativos para apoio à decisão de compra.

    Parameters
    ----------
    snapshot: dict
        Estrutura de dados de mercado retornada pelo data_layer.
    analytics: dict
        Resultados de cálculos analíticos (percentil, spread, volatilidade).
    parametros_regra: dict, optional
        Parâmetros opcionais como limites de percentil ou estoque.

    Returns
    -------
    list[str]
        Lista de mensagens em português para orientar negociações.
    """

    insights: List[str] = []
    regras = parametros_regra or {}

    percentil = analytics.get("percentil_preco")
    estoque = snapshot.get("lme_stock_t")
    estrutura = analytics.get("estrutura_curva")
    volatilidade = analytics.get("volatilidade")

    limite_percentil_baixo = regras.get("limite_percentil_baixo", 30)
    limite_estoque_alto = regras.get("limite_estoque_alto", 100000)

    if percentil is not None:
        if percentil <= limite_percentil_baixo:
            insights.append("Preço atual em percentil baixo: oportunidade de compra.")
        else:
            insights.append("Preço não está em percentil baixo; avaliar timing de compra.")
    else:
        insights.append("Percentil de preço indisponível; revisar histórico e preço atual.")

    if estoque is not None:
        if estoque >= limite_estoque_alto:
            insights.append("Estoque LME elevado sugere oferta confortável.")
        else:
            insights.append("Estoque LME não está elevado; risco de aperto de oferta.")
    else:
        insights.append("Estoque LME indisponível; acompanhar boletins de estoque.")

    if estrutura is not None:
        if estrutura == "contango":
            insights.append("Curva em contango: mercado bem abastecido no curto prazo.")
        elif estrutura == "backwardation":
            insights.append("Curva em backwardation: prêmio para disponibilidade imediata.")
        else:
            insights.append("Curva neutra: sem sinal claro de escassez ou excesso.")
    else:
        insights.append("Estrutura de curva indisponível; verificar spreads.")

    if volatilidade is not None:
        insights.append(
            f"Volatilidade anualizada em {volatilidade:.2%}; avaliar hedge conforme política."
        )
    else:
        insights.append("Volatilidade não calculada; coletar histórico suficiente.")

    warnings = snapshot.get("warnings", [])
    warnings.extend(analytics.get("warnings", []))
    for aviso in warnings:
        insights.append(f"Aviso de dados: {aviso}")

    return insights
