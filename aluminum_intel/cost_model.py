"""Modelo de custo all-in para alumínio 6061.

A função principal usa dados do snapshot e parâmetros explícitos de prêmios
ou fretes fornecidos pelo usuário. Nenhum valor é presumido: se faltar dado,
o cálculo registra warnings e retorna ``None`` nos campos afetados.
"""

from __future__ import annotations

from typing import Dict, Optional


def calcular_custo_aluminio(
    snapshot: Dict[str, object],
    premio_regional_usd_t: Optional[float] = None,
    premio_extrusao_usd_t: Optional[float] = None,
    frete_usd_t: Optional[float] = None,
    cambio_brl_usd: Optional[float] = None,
) -> Dict[str, object]:
    """Calcula o custo all-in do alumínio considerando insumos explícitos.

    Parameters
    ----------
    snapshot: dict
        Resultado de :func:`data_layer.get_aluminum_market_snapshot`.
    premio_regional_usd_t: float, optional
        Prêmio regional informado pelo usuário.
    premio_extrusao_usd_t: float, optional
        Prêmio específico para alumínio extrudado.
    frete_usd_t: float, optional
        Custo logístico por tonelada.
    cambio_brl_usd: float, optional
        Taxa de câmbio BRL/USD a ser usada. Se ``None``, utiliza o valor do
        snapshot, quando disponível.

    Returns
    -------
    dict
        Dicionário com componentes do custo e warnings se algo faltar.
    """

    warnings = list(snapshot.get("warnings", []))
    lme_base = snapshot.get("lme_3m_usd_t") or snapshot.get("lme_cash_usd_t")
    fx_spot = cambio_brl_usd or snapshot.get("fx_spot_brl_usd")

    if lme_base is None:
        warnings.append("Sem preço LME disponível para calcular o custo.")
    if fx_spot is None:
        warnings.append("Sem câmbio BRL/USD disponível para conversão.")

    premio_regional = premio_regional_usd_t if premio_regional_usd_t is not None else 0.0
    premio_extrusao = premio_extrusao_usd_t if premio_extrusao_usd_t is not None else 0.0
    frete = frete_usd_t if frete_usd_t is not None else 0.0

    custo_usd = None
    custo_brl = None
    if lme_base is not None:
        custo_usd = lme_base + premio_regional + premio_extrusao + frete
        if fx_spot is not None:
            custo_brl = custo_usd * fx_spot
        else:
            warnings.append("Custo em USD calculado, mas sem FX para converter em BRL.")

    return {
        "lme_base_usd_t": lme_base,
        "premio_regional_usd_t": premio_regional_usd_t,
        "premio_extrusao_usd_t": premio_extrusao_usd_t,
        "frete_usd_t": frete_usd_t,
        "custo_total_usd_t": custo_usd,
        "custo_total_brl_t": custo_brl,
        "fx_utilizado_brl_usd": fx_spot,
        "warnings": warnings,
    }
