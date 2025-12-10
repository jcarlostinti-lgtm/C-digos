"""Camada de dados para captura de informações do mercado de alumínio.

As funções deste módulo se concentram em obter preços, estoques e histórico
sem nunca inventar valores. Sempre que uma fonte falhar, a função registra um
warning e retorna ``None`` para o dado indisponível.
"""

from __future__ import annotations

import datetime as _dt
import logging
from typing import Dict, List, Optional

import pandas as pd
import requests
import yfinance as yf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _safe_request_json(url: str, params: Optional[Dict[str, str]] = None) -> Optional[dict]:
    """Executa uma requisição HTTP GET e retorna o JSON quando possível.

    Parameters
    ----------
    url: str
        URL do endpoint a ser consultado.
    params: dict, optional
        Parâmetros de query string.

    Returns
    -------
    dict | None
        Dicionário com a resposta JSON ou ``None`` se houver erro.
    """

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001 - capturar qualquer falha de rede
        logger.warning("Falha ao requisitar %s: %s", url, exc)
        return None


def get_lme_from_westmetall() -> Dict[str, Optional[float]]:
    """Obtém preços e estoque de alumínio da WestMetall.

    Returns
    -------
    dict
        Dicionário com chaves ``cash``, ``three_month`` e ``stock``. Valores
        ausentes são representados por ``None``.
    """

    url = "https://www.westmetall.com/en/markdaten.php"
    params = {"aid": 150, "lang": "en"}
    warnings: List[str] = []
    cash: Optional[float] = None
    three_month: Optional[float] = None
    stock: Optional[float] = None

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        df_list = pd.read_html(response.text)
        if df_list:
            tabela = df_list[0]
            tabela.columns = [col.lower() for col in tabela.columns]
            if "cash" in tabela.columns:
                cash = float(tabela.loc[0, "cash"])
            if "3 months" in tabela.columns:
                three_month = float(tabela.loc[0, "3 months"])
            if "stocks" in tabela.columns:
                stock = float(tabela.loc[0, "stocks"])
        else:
            warnings.append("Tabela não encontrada na página da WestMetall.")
    except Exception as exc:  # noqa: BLE001 - scraping depende de HTML
        warnings.append(f"Erro ao ler dados da WestMetall: {exc}")
        logger.warning(warnings[-1])

    return {
        "cash": cash,
        "three_month": three_month,
        "stock": stock,
        "warnings": warnings,
    }


def get_aluminum_from_metalsdev(symbols: List[str]) -> Dict[str, Optional[float]]:
    """Busca preços via API Metals.Dev para os símbolos informados.

    Parameters
    ----------
    symbols: list[str]
        Lista de símbolos disponíveis na API.

    Returns
    -------
    dict
        Mapeia símbolo para preço em USD/tonelada quando disponível.
    """

    api_key = requests.utils.os.environ.get("METALS_DEV_API_KEY")
    base_url = "https://api.metals.dev/v1/latest"
    resultados: Dict[str, Optional[float]] = {}

    if not api_key:
        logger.warning("Chave METALS_DEV_API_KEY não configurada.")
        for simbolo in symbols:
            resultados[simbolo] = None
        return resultados

    for simbolo in symbols:
        params = {"symbol": simbolo, "api_key": api_key}
        payload = _safe_request_json(base_url, params=params)
        if payload and "data" in payload and payload["data"]:
            valor = payload["data"].get("price")
            resultados[simbolo] = float(valor) if valor is not None else None
        else:
            resultados[simbolo] = None
    return resultados


def get_ali_f_from_yfinance(periodo: str = "1y") -> Optional[pd.Series]:
    """Obtém histórico do futuro de alumínio ALI=F via yfinance.

    Parameters
    ----------
    periodo: str, default "1y"
        Período a ser solicitado à API do Yahoo Finance.

    Returns
    -------
    pandas.Series | None
        Série com os preços de fechamento diário em USD/tonelada, se
        disponível.
    """

    try:
        ticker = yf.Ticker("ALI=F")
        history = ticker.history(period=periodo)
        if history.empty:
            logger.warning("Histórico vazio retornado pelo yfinance para ALI=F.")
            return None
        return history["Close"].rename("ALI=F")
    except Exception as exc:  # noqa: BLE001 - chamada externa pode falhar
        logger.warning("Erro ao obter dados do yfinance: %s", exc)
        return None


def get_ptax_brl_usd(data_referencia: Optional[_dt.date] = None) -> Optional[float]:
    """Consulta a taxa PTAX BRL/USD no serviço do Banco Central.

    Parameters
    ----------
    data_referencia: datetime.date, optional
        Data de referência. Por padrão usa a data atual.

    Returns
    -------
    float | None
        Valor do câmbio de compra (taxaPTAX) ou ``None`` em caso de falha.
    """

    data = data_referencia or _dt.date.today()
    data_formatada = data.strftime("%m-%d-%Y")
    url = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        "CotacaoDolarDia(dataCotacao='{}')".format(data_formatada)
    )

    payload = _safe_request_json(url)
    if not payload or "value" not in payload or not payload["value"]:
        logger.warning("PTAX indisponível para a data informada: %s", data_formatada)
        return None

    cotacao = payload["value"][0].get("cotacaoCompra")
    return float(cotacao) if cotacao is not None else None


def get_aluminum_market_snapshot() -> Dict[str, object]:
    """Monta um snapshot consolidado do mercado de alumínio.

    Returns
    -------
    dict
        Estrutura completa conforme especificação do projeto com preços,
        estoque, câmbio, histórico e metadados de fontes utilizadas.
    """

    warnings: List[str] = []
    sources_used: Dict[str, bool] = {
        "westmetall": False,
        "metals_dev": False,
        "yfinance": False,
        "ptax": False,
    }

    dados_westmetall = get_lme_from_westmetall()
    sources_used["westmetall"] = True
    warnings.extend(dados_westmetall.get("warnings", []))

    lme_cash = dados_westmetall.get("cash")
    lme_three_month = dados_westmetall.get("three_month")
    lme_stock = dados_westmetall.get("stock")

    metals_dev_precos = get_aluminum_from_metalsdev(["LME-ALU-3M"])
    sources_used["metals_dev"] = True
    if metals_dev_precos.get("LME-ALU-3M") is None:
        warnings.append("Preço via Metals.Dev indisponível.")

    history = get_ali_f_from_yfinance()
    sources_used["yfinance"] = True
    if history is None:
        warnings.append("Histórico ALI=F indisponível via yfinance.")

    fx_spot = get_ptax_brl_usd()
    sources_used["ptax"] = True
    if fx_spot is None:
        warnings.append("PTAX BRL/USD não retornou valor.")

    snapshot = {
        "lme_cash_usd_t": lme_cash or metals_dev_precos.get("LME-ALU-3M"),
        "lme_3m_usd_t": lme_three_month or metals_dev_precos.get("LME-ALU-3M"),
        "lme_stock_t": lme_stock,
        "fx_spot_brl_usd": fx_spot,
        "history_usd_t": history,
        "sources_used": sources_used,
        "warnings": warnings,
    }

    return snapshot
