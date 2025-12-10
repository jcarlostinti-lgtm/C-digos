"""Rotinas analíticas para o mercado de alumínio.

Todas as funções retornam resultados numéricos baseados em séries históricas ou
preços do snapshot, sem qualquer extrapolação ou previsão.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd


def calcular_percentil_preco(series: Optional[pd.Series], valor_atual: Optional[float]) -> Optional[float]:
    """Calcula o percentil do preço atual em relação ao histórico fornecido.

    Parameters
    ----------
    series: pandas.Series | None
        Histórico de preços em USD/tonelada.
    valor_atual: float | None
        Preço atual a ser posicionado no histórico.

    Returns
    -------
    float | None
        Percentil (0-100) ou ``None`` se não houver dados suficientes.
    """

    if series is None or valor_atual is None:
        return None
    serie_limpa = series.dropna()
    if serie_limpa.empty:
        return None
    posicao = (serie_limpa <= valor_atual).sum() / len(serie_limpa)
    return float(posicao * 100)


def calcular_spread_3m_cash(snapshot: Dict[str, object]) -> Optional[float]:
    """Calcula o spread entre LME 3M e cash.

    Parameters
    ----------
    snapshot: dict
        Estrutura retornada pelo data_layer com campos ``lme_3m_usd_t`` e
        ``lme_cash_usd_t``.

    Returns
    -------
    float | None
        Valor do spread (USD/tonelada) ou ``None`` se faltarem componentes.
    """

    lme_3m = snapshot.get("lme_3m_usd_t")
    lme_cash = snapshot.get("lme_cash_usd_t")
    if lme_3m is None or lme_cash is None:
        return None
    return float(lme_3m - lme_cash)


def classificar_estrutura_curva(spread: Optional[float]) -> Optional[str]:
    """Classifica a estrutura de curva com base no spread 3M - Cash.

    Parameters
    ----------
    spread: float | None
        Spread calculado entre o contrato de 3 meses e o preço cash.

    Returns
    -------
    str | None
        "contango" quando o spread for positivo, "backwardation" se negativo
        e "neutra" quando zero. Retorna ``None`` quando não há spread.
    """

    if spread is None:
        return None
    if spread > 0:
        return "contango"
    if spread < 0:
        return "backwardation"
    return "neutra"


def calcular_volatilidade(series: Optional[pd.Series], janela: int = 30) -> Optional[float]:
    """Calcula a volatilidade histórica anualizada.

    Parameters
    ----------
    series: pandas.Series | None
        Série de preços diários em USD/tonelada.
    janela: int, default 30
        Número de dias úteis para a janela de volatilidade.

    Returns
    -------
    float | None
        Volatilidade anualizada (desvio padrão) ou ``None`` se não houver
        dados suficientes.
    """

    if series is None:
        return None
    retornos = series.dropna().pct_change().dropna()
    if retornos.empty or len(retornos) < janela:
        return None
    vol_diaria = retornos.rolling(window=janela).std().iloc[-1]
    if np.isnan(vol_diaria):
        return None
    return float(vol_diaria * np.sqrt(252))
