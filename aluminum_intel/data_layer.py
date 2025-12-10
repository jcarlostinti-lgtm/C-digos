"""Camada de dados para captura e consolidação de informações de mercado.

Este módulo centraliza o acesso a múltiplas fontes abertas utilizadas na
formação de preço do alumínio extrudado liga 6061. Nenhum dado fixo ou
suposto é considerado; quando uma fonte não responde ou o parsing não é
possível, o retorno deve ser ``None`` e um aviso é registrado.
"""

from __future__ import annotations

import logging
import os
from datetime import date
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

WESTMETALL_URL = "https://www.westmetall.com/en/markdaten.php?aid=15&lieferant_id=8&lang=en"
METALS_DEV_SPOT_URL = "https://api.metals.dev/v1/market/spot"
BCB_PTAX_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/5?formato=json"


def _append_warning(warnings: List[str], message: str) -> None:
    """Adiciona um aviso à lista e registra no logger.

    A função centraliza o padrão de registro para manter consistência entre
    diferentes pontos de coleta de dados.
    """

    warnings.append(message)
    logger.warning(message)


def get_lme_from_westmetall() -> Dict[str, Optional[float]]:
    """Captura cotações de alumínio LME (Cash e 3M) e estoques do WestMetall.

    Returns
    -------
    dict
        Dicionário com as chaves ``cash_usd_t``, ``three_month_usd_t`` e
        ``stock_t``. Cada valor pode ser ``None`` quando não for possível
        extrair a informação sem suposições.
    """

    warnings: List[str] = []
    cash_value = three_month_value = stock_value = None

    try:
        response = requests.get(WESTMETALL_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "markdata"}) or soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
                if not cells:
                    continue
                header_text = " ".join(cells).lower()
                if "aluminium" in header_text and "cash" in header_text and len(cells) >= 2:
                    try:
                        cash_value = float(cells[-1].replace(",", ""))
                    except ValueError:
                        _append_warning(warnings, "Falha ao converter Cash LME a partir do WestMetall.")
                if "aluminium" in header_text and "3 months" in header_text and len(cells) >= 2:
                    try:
                        three_month_value = float(cells[-1].replace(",", ""))
                    except ValueError:
                        _append_warning(warnings, "Falha ao converter 3M LME a partir do WestMetall.")
                if "stocks" in header_text and len(cells) >= 2:
                    try:
                        stock_value = float(cells[-1].replace(",", ""))
                    except ValueError:
                        _append_warning(warnings, "Falha ao converter estoque LME a partir do WestMetall.")
        else:
            _append_warning(warnings, "Tabela principal não encontrada no WestMetall.")
    except requests.RequestException as exc:
        _append_warning(warnings, f"Erro na requisição ao WestMetall: {exc}")

    return {
        "cash_usd_t": cash_value,
        "three_month_usd_t": three_month_value,
        "stock_t": stock_value,
        "warnings": warnings,
    }


def get_aluminum_from_metalsdev(symbols: Iterable[str]) -> Dict[str, Optional[float]]:
    """Consulta preços spot na API Metals.Dev para os símbolos fornecidos.

    Parameters
    ----------
    symbols : Iterable[str]
        Lista de símbolos conforme documentação da Metals.Dev, por exemplo
        ``["ALUMINUM"]``.

    Returns
    -------
    dict
        Mapeamento símbolo → preço float ou ``None``. Quando a API key não
        estiver configurada, nenhum valor é retornado e um aviso é gerado.
    """

    api_key = os.getenv("METALS_DEV_API_KEY")
    results: Dict[str, Optional[float]] = {symbol: None for symbol in symbols}
    warnings: List[str] = []

    if not api_key:
        _append_warning(warnings, "Variável de ambiente METALS_DEV_API_KEY não informada.")
        return {"values": results, "warnings": warnings}

    for symbol in symbols:
        try:
            response = requests.get(
                METALS_DEV_SPOT_URL,
                params={"metal": symbol.lower()},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            price = payload.get("price") or payload.get("data", {}).get("price")
            if price is not None:
                try:
                    results[symbol] = float(price)
                except (TypeError, ValueError):
                    _append_warning(warnings, f"Preço inválido retornado pela Metals.Dev para {symbol}.")
            else:
                _append_warning(warnings, f"Preço não disponível na Metals.Dev para {symbol}.")
        except requests.RequestException as exc:
            _append_warning(warnings, f"Erro na Metals.Dev para {symbol}: {exc}")

    return {"values": results, "warnings": warnings}


def get_ali_f_from_yfinance() -> Dict[str, Optional[pd.Series]]:
    """Baixa a série histórica do contrato ALI=F via yfinance.

    Returns
    -------
    dict
        Contém ``series`` com ``pandas.Series`` de fechamento diário e
        ``warnings`` com problemas encontrados. Em caso de falha, ``series`` é
        ``None`` e uma mensagem informativa é adicionada.
    """

    warnings: List[str] = []
    history_series: Optional[pd.Series] = None

    try:
        ticker = yf.Ticker("ALI=F")
        history = ticker.history(period="6mo", interval="1d")
        if not history.empty:
            history_series = history["Close"].dropna()
        else:
            _append_warning(warnings, "Série ALI=F vazia retornada pelo yfinance.")
    except Exception as exc:  # noqa: BLE001 - capturar qualquer erro da biblioteca externa
        _append_warning(warnings, f"Erro ao acessar yfinance para ALI=F: {exc}")

    return {"series": history_series, "warnings": warnings}


def get_ptax_brl_usd() -> Dict[str, Optional[float]]:
    """Obtém o câmbio PTAX BRL/USD mais recente via API do Banco Central.

    Returns
    -------
    dict
        Dicionário com ``fx`` contendo o valor float quando disponível e
        ``warnings`` em caso de falhas. Nenhum valor padrão é assumido.
    """

    warnings: List[str] = []
    fx_value: Optional[float] = None

    try:
        response = requests.get(BCB_PTAX_URL, timeout=10)
        response.raise_for_status()
        payload = response.json()
        if payload:
            latest_entry = payload[-1]
            valor = latest_entry.get("valor") or latest_entry.get("value")
            try:
                fx_value = float(str(valor).replace(",", "."))
            except (TypeError, ValueError):
                _append_warning(warnings, "Valor PTAX inválido retornado pela API do BCB.")
        else:
            _append_warning(warnings, "Nenhum dado retornado pela API PTAX.")
    except requests.RequestException as exc:
        _append_warning(warnings, f"Erro na requisição PTAX: {exc}")

    return {"fx": fx_value, "warnings": warnings}


def get_aluminum_market_snapshot() -> Dict[str, object]:
    """Compila um snapshot consolidado das principais referências de mercado.

    O snapshot reúne cotações LME, câmbio PTAX, histórico ALI=F e indica quais
    fontes foram utilizadas. Quando alguma informação estiver ausente, o valor
    correspondente será ``None`` e a lista de ``warnings`` detalhará o motivo.
    """

    warnings: List[str] = []
    sources_used: Dict[str, bool] = {
        "westmetall": False,
        "metals_dev": False,
        "yfinance": False,
        "ptax": False,
    }

    westmetall_data = get_lme_from_westmetall()
    warnings.extend(westmetall_data.pop("warnings", []))
    sources_used["westmetall"] = any(
        value is not None for key, value in westmetall_data.items() if key != "warnings"
    )

    metals_dev_data = get_aluminum_from_metalsdev(["ALUMINUM"])
    warnings.extend(metals_dev_data.get("warnings", []))
    sources_used["metals_dev"] = any(value is not None for value in metals_dev_data.get("values", {}).values())

    yfinance_data = get_ali_f_from_yfinance()
    warnings.extend(yfinance_data.get("warnings", []))
    sources_used["yfinance"] = yfinance_data.get("series") is not None

    ptax_data = get_ptax_brl_usd()
    warnings.extend(ptax_data.get("warnings", []))
    sources_used["ptax"] = ptax_data.get("fx") is not None

    snapshot = {
        "lme_cash_usd_t": westmetall_data.get("cash_usd_t"),
        "lme_3m_usd_t": westmetall_data.get("three_month_usd_t"),
        "lme_stock_t": westmetall_data.get("stock_t"),
        "fx_spot_brl_usd": ptax_data.get("fx"),
        "history_usd_t": yfinance_data.get("series"),
        "sources_used": sources_used,
        "warnings": warnings,
    }

    if metals_dev_data.get("values", {}).get("ALUMINUM") is not None:
        snapshot["spot_metals_dev_usd_t"] = metals_dev_data["values"]["ALUMINUM"]
    else:
        snapshot["spot_metals_dev_usd_t"] = None

    snapshot["data_atualizacao"] = date.today().isoformat()

    return snapshot
