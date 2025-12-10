"""Modelo de cálculo de custo all-in do alumínio 6061.

Nenhum valor fixo deve ser assumido. O cálculo segue a fórmula consagrada no
setor: base LME (Cash ou 3M) somada aos prêmios e fretes fornecidos como
entrada. Sempre que um componente estiver ausente, um aviso é registrado para
alertar o usuário sobre lacunas de informação.
"""

from __future__ import annotations

from typing import Dict, List, Optional


def calcular_custo_aluminio(
    lme_cash_usd_t: Optional[float],
    lme_3m_usd_t: Optional[float],
    premios_usd_t: Optional[float] = None,
    frete_usd_t: Optional[float] = None,
    outros_custos_usd_t: Optional[float] = None,
    usar_preco_preferencial: str = "3m",
) -> Dict[str, object]:
    """Calcula o custo all-in a partir das referências fornecidas.

    Parameters
    ----------
    lme_cash_usd_t : float | None
        Cotação LME Cash em USD/t.
    lme_3m_usd_t : float | None
        Cotação LME 3M em USD/t.
    premios_usd_t : float | None, optional
        Soma de prêmios regionais, billet e prêmio extrusão informados pelo
        usuário. Quando não informado, o valor será tratado como zero porém um
        aviso explicará a ausência.
    frete_usd_t : float | None, optional
        Custos de frete logístico em USD/t.
    outros_custos_usd_t : float | None, optional
        Qualquer custo adicional repassado pelo cliente (ex.: seguro). Nenhum
        valor padrão é assumido.
    usar_preco_preferencial : {"3m", "cash"}
        Define qual referência LME é priorizada. Caso a referência escolhida
        esteja indisponível, o método tentará a alternativa restante.

    Returns
    -------
    dict
        Estrutura com componentes de custo, referência LME utilizada e lista de
        avisos registrados durante o cálculo.
    """

    warnings: List[str] = []

    if usar_preco_preferencial not in {"3m", "cash"}:
        warnings.append("Parâmetro 'usar_preco_preferencial' inválido; usando 3M como padrão.")
        usar_preco_preferencial = "3m"

    lme_escolhida: Optional[float] = None
    if usar_preco_preferencial == "3m" and lme_3m_usd_t is not None:
        lme_escolhida = lme_3m_usd_t
    elif usar_preco_preferencial == "cash" and lme_cash_usd_t is not None:
        lme_escolhida = lme_cash_usd_t
    elif lme_3m_usd_t is not None:
        warnings.append("Cotação preferencial ausente; utilizando LME 3M disponível.")
        lme_escolhida = lme_3m_usd_t
    elif lme_cash_usd_t is not None:
        warnings.append("Cotação preferencial ausente; utilizando LME Cash disponível.")
        lme_escolhida = lme_cash_usd_t
    else:
        warnings.append("Nenhuma referência LME disponível para cálculo de custo.")

    premio_total = premios_usd_t if premios_usd_t is not None else 0.0
    frete_total = frete_usd_t if frete_usd_t is not None else 0.0
    outros_total = outros_custos_usd_t if outros_custos_usd_t is not None else 0.0

    if premios_usd_t is None:
        warnings.append("Prêmios não informados; componente considerado zero.")
    if frete_usd_t is None:
        warnings.append("Frete não informado; componente considerado zero.")
    if outros_custos_usd_t is None:
        warnings.append("Outros custos não informados; componente considerado zero.")

    if lme_escolhida is None:
        custo_total = None
    else:
        custo_total = lme_escolhida + premio_total + frete_total + outros_total

    return {
        "lme_referencia_usd_t": lme_escolhida,
        "premios_usd_t": premio_total,
        "frete_usd_t": frete_total,
        "outros_custos_usd_t": outros_total,
        "custo_total_usd_t": custo_total,
        "warnings": warnings,
    }
