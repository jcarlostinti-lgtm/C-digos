"""Heurísticas de apoio à decisão para compras de alumínio 6061.

O objetivo deste módulo é transformar métricas quantitativas em mensagens
objetivas em português. Nenhuma previsão é realizada; apenas interpretações
qualitativas com base nas regras descritas no AGENTS.md.
"""

from __future__ import annotations

from typing import Dict, List


INSIGHT_TEMPLATES = {
    "preco_baixo": "Preço LME em percentil baixo sugere janela de compra favorável.",
    "preco_alto": "Preço LME em percentil elevado requer cautela nas negociações.",
    "estoque_alto": "Estoque LME elevado indica oferta confortável no curto prazo.",
    "estoque_baixo": "Estoque LME reduzido pode pressionar prêmios e disponibilidade.",
    "contango": "Curva em contango indica conforto de oferta e custos financeiros maiores.",
    "backwardation": "Curva em backwardation sinaliza aperto de oferta no curto prazo.",
    "neutro": "Curva neutra não indica desequilíbrio relevante entre prazos.",
}



def gerar_insights_compra(snapshot: Dict[str, object], analytics: Dict[str, object], parametros_regra: Dict[str, float]) -> List[str]:
    """Gera lista de insights de compra conforme heurísticas predefinidas.

    Parameters
    ----------
    snapshot : dict
        Estrutura retornada por ``get_aluminum_market_snapshot`` contendo preços
        e estoques.
    analytics : dict
        Resultados consolidados de ``analytics.gerar_resumo_analytics``.
    parametros_regra : dict
        Limiares utilizados nas regras. Deve conter, por exemplo,
        ``percentil_baixo`` e ``percentil_alto``.

    Returns
    -------
    list[str]
        Mensagens em português destacando pontos de atenção e oportunidades.
    """

    insights: List[str] = []

    percentil = analytics.get("percentil_lme")
    estoque = snapshot.get("lme_stock_t")
    estrutura = analytics.get("estrutura_curva")

    percentil_baixo = parametros_regra.get("percentil_baixo", 0.3)
    percentil_alto = parametros_regra.get("percentil_alto", 0.7)
    estoque_alto = parametros_regra.get("estoque_alto", None)
    estoque_baixo = parametros_regra.get("estoque_baixo", None)

    if percentil is not None:
        if percentil <= percentil_baixo:
            insights.append(INSIGHT_TEMPLATES["preco_baixo"])
        elif percentil >= percentil_alto:
            insights.append(INSIGHT_TEMPLATES["preco_alto"])

    if estoque is not None:
        if estoque_alto is not None and estoque >= estoque_alto:
            insights.append(INSIGHT_TEMPLATES["estoque_alto"])
        if estoque_baixo is not None and estoque <= estoque_baixo:
            insights.append(INSIGHT_TEMPLATES["estoque_baixo"])

    if estrutura in {"contango", "backwardation", "neutro"}:
        insights.append(INSIGHT_TEMPLATES[estrutura])

    if not insights:
        insights.append("Sem insights específicos no momento; revisar dados e premissas.")

    return insights
