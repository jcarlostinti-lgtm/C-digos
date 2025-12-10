"""Módulo de análises estatísticas sobre preços de alumínio.

As funções aqui implementadas não produzem previsões; apenas oferecem métricas
historicamente utilizadas para contextualizar decisões de compra. Nenhum valor
é inventado e todas as saídas refletem cálculos diretos sobre os dados
fornecidos.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd


def calcular_percentil_preco(serie_precos: pd.Series, valor_atual: float) -> Optional[float]:
    """Calcula o percentil do valor atual dentro da série histórica.

    Retorna ``None`` quando a série estiver vazia ou quando o valor não for
    numérico. O percentil é calculado de forma empírica usando a função
    ``quantile`` do pandas.
    """

    if serie_precos is None or serie_precos.empty:
        return None
    try:
        percentil = (serie_precos < valor_atual).sum() / len(serie_precos)
        return float(percentil)
    except Exception:
        return None


def calcular_spread_3m_cash(lme_3m_usd_t: Optional[float], lme_cash_usd_t: Optional[float]) -> Optional[float]:
    """Calcula o spread entre LME 3M e Cash.

    Retorna ``None`` quando um dos valores estiver ausente.
    """

    if lme_3m_usd_t is None or lme_cash_usd_t is None:
        return None
    return lme_3m_usd_t - lme_cash_usd_t


def classificar_estrutura_curva(spread_3m_cash: Optional[float], tolerancia: float = 1e-6) -> str:
    """Classifica a estrutura da curva futuro x à vista.

    Parameters
    ----------
    spread_3m_cash : float | None
        Diferença entre LME 3M e LME Cash.
    tolerancia : float
        Margem de tolerância para considerar a curva como neutra.

    Returns
    -------
    str
        ``"contango"`` quando o spread for positivo, ``"backwardation"`` quando
        negativo e ``"neutro"`` quando estiver dentro da tolerância definida.
    """

    if spread_3m_cash is None:
        return "desconhecida"
    if spread_3m_cash > tolerancia:
        return "contango"
    if spread_3m_cash < -tolerancia:
        return "backwardation"
    return "neutro"


def calcular_volatilidade(serie_precos: pd.Series, dias_ano: int = 252) -> Optional[float]:
    """Calcula a volatilidade anualizada a partir de retornos logarítmicos.

    Quando a série possuir menos de dois pontos, retorna ``None``. O cálculo usa
    desvio padrão dos log-retornos multiplicado pela raiz do número de dias
    úteis por ano.
    """

    if serie_precos is None or len(serie_precos) < 2:
        return None

    retornos = np.log(serie_precos / serie_precos.shift(1)).dropna()
    if retornos.empty:
        return None

    volatilidade = retornos.std() * np.sqrt(dias_ano)
    return float(volatilidade)


def gerar_resumo_analytics(
    serie_precos: Optional[pd.Series],
    lme_3m_usd_t: Optional[float],
    lme_cash_usd_t: Optional[float],
) -> Dict[str, Optional[float]]:
    """Aplica todos os cálculos analíticos e devolve um dicionário consolidado."""

    spread = calcular_spread_3m_cash(lme_3m_usd_t, lme_cash_usd_t)
    percentil = calcular_percentil_preco(serie_precos, lme_3m_usd_t or lme_cash_usd_t or 0.0)
    volatilidade = calcular_volatilidade(serie_precos)
    estrutura = classificar_estrutura_curva(spread)

    return {
        "spread_3m_cash": spread,
        "percentil_lme": percentil,
        "estrutura_curva": estrutura,
        "volatilidade": volatilidade,
    }
