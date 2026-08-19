import json
import urllib.request
import urllib.error

def buscar_clima(cidade: str, latitude: float, longitude: float) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&"
        f"timezone=auto&forecast_days=3"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                return {"erro": f"Open-Meteo respondeu {response.status}"}
            
            data = json.loads(response.read().decode("utf-8"))
            daily = data.get("daily", {})
            times = daily.get("time", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            chance_chuva = daily.get("precipitation_probability_max", [])

            previsao = [
                {
                    "data": data_,
                    "temp_max": temp_max[i],
                    "temp_min": temp_min[i],
                    "chance_chuva": chance_chuva[i],
                }
                for i, data_ in enumerate(times)
            ]

            return {"cidade": cidade, "previsao": previsao}
    except Exception as err:
        return {"erro": f"Falha ao buscar clima: {str(err)}"}


ATRACOES_MOCK = {
    "rio de janeiro": [
        {"nome": "Cristo Redentor", "categoria": "ponto turístico", "custo_estimado": 90},
        {"nome": "Pão de Açúcar", "categoria": "ponto turístico", "custo_estimado": 150},
        {"nome": "Praia de Ipanema", "categoria": "praia", "custo_estimado": 0},
    ],
    "são paulo": [
        {"nome": "MASP", "categoria": "museu", "custo_estimado": 50},
        {"nome": "Parque Ibirapuera", "categoria": "parque", "custo_estimado": 0},
        {"nome": "Mercado Municipal", "categoria": "gastronomia", "custo_estimado": 40},
    ],
    "niterói": [
        {"nome": "MAC Niterói", "categoria": "museu", "custo_estimado": 20},
        {"nome": "Praia de Icaraí", "categoria": "praia", "custo_estimado": 0},
        {"nome": "Caminho Niemeyer", "categoria": "arquitetura", "custo_estimado": 0},
    ],
}


def buscar_atracoes(cidade: str) -> dict:
    chave = cidade.strip().lower()
    resultado = ATRACOES_MOCK.get(chave)
    if not resultado:
        return {
            "aviso": f'Sem dados mockados para "{cidade}". Em produção isso chamaria uma API real (ex: Google Places).',
            "atracoes": [],
        }
    return {"cidade": cidade, "atracoes": resultado}


def calcular_orcamento(itens: list, orcamento_total: float) -> dict:
    soma = sum(item.get("custo", 0) for item in itens)
    restante = orcamento_total - soma

    return {
        "total_gasto": soma,
        "orcamento_total": orcamento_total,
        "restante": restante,
        "dentro_do_orcamento": restante >= 0,
        "detalhe": itens,
    }


GEMINI_TOOL_DECLARATIONS = [
    {
        "name": "buscar_clima",
        "description": "Busca a previsão do tempo de 3 dias para uma cidade, dado seu nome e coordenadas geográficas (latitude/longitude).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "cidade": {"type": "STRING", "description": "Nome da cidade"},
                "latitude": {"type": "NUMBER", "description": "Latitude da cidade"},
                "longitude": {"type": "NUMBER", "description": "Longitude da cidade"},
            },
            "required": ["cidade", "latitude", "longitude"],
        },
    },
    {
        "name": "buscar_atracoes",
        "description": "Retorna uma lista de atrações turísticas e seus custos estimados em reais para uma cidade.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "cidade": {"type": "STRING", "description": "Nome da cidade"},
            },
            "required": ["cidade"],
        },
    },
    {
        "name": "calcular_orcamento",
        "description": "Soma o custo de uma lista de itens (atrações, hospedagem, etc.) e compara com o orçamento total disponível.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "itens": {
                    "type": "ARRAY",
                    "description": "Lista de itens com nome e custo",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "nome": {"type": "STRING"},
                            "custo": {"type": "NUMBER"},
                        },
                        "required": ["nome", "custo"],
                    },
                },
                "orcamento_total": {"type": "NUMBER", "description": "Orçamento disponível em reais"},
            },
            "required": ["itens", "orcamento_total"],
        },
    },
]

TOOL_IMPLEMENTATIONS = {
    "buscar_clima": buscar_clima,
    "buscar_atracoes": buscar_atracoes,
    "calcular_orcamento": calcular_orcamento,
}