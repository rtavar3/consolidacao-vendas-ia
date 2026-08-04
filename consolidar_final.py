"""
Projeto de portfólio: Pipeline de Consolidação de Dados + Resumo via IA

Fluxo:
1. Lê múltiplos arquivos Excel/CSV de uma pasta
2. Limpa e padroniza os dados
3. Consolida tudo em um único DataFrame
4. Gera métricas/resumo (groupby)
5. Exporta o relatório final
6. (Fase 3) Envia um resumo dos dados para uma LLM gerar um texto explicativo
"""

import os
import glob
import pandas as pd
import requests

# ---------------------------------------------------------
# ETAPA 1: Leitura de múltiplos arquivos
# ---------------------------------------------------------
def ler_arquivos(pasta_entrada: str) -> list[pd.DataFrame]:
    """Lê todos os .xlsx e .csv de uma pasta e retorna uma lista de DataFrames."""
    caminhos = glob.glob(os.path.join(pasta_entrada, "*.xlsx")) + \
               glob.glob(os.path.join(pasta_entrada, "*.csv"))

    dataframes = []
    for caminho in caminhos:
        if caminho.endswith(".xlsx"):
            df = pd.read_excel(caminho)
        else:
            df = pd.read_csv(caminho)
        df["arquivo_origem"] = os.path.basename(caminho)  # rastreabilidade
        dataframes.append(df)

    return dataframes


# ---------------------------------------------------------
# ETAPA 2: Limpeza e padronização
# ---------------------------------------------------------
# Mapeamento: nomes alternativos de coluna -> nome padrão
MAPA_COLUNAS = {
    "vendedor_nome": "vendedor",
    "data_venda": "data",
    "valor_venda": "valor",
}

def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes de colunas, unifica formatos e trata nulos/duplicatas."""
    # 1. minúsculo + underscore (janeiro/marco já ficam certos: vendedor, data, valor, categoria)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # 2. aplica o mapeamento para os nomes alternativos (fevereiro: vendedor_nome -> vendedor etc.)
    df = df.rename(columns=MAPA_COLUNAS)

    # 3. unifica o formato de data (aceita tanto "2026-01-05" quanto "10/02/2026")
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    # 4. remove linhas sem vendedor ou sem valor (dados incompletos demais para usar)
    df = df.dropna(subset=["vendedor", "valor"])

    # 5. remove duplicatas exatas (ex: a linha repetida de Ana Silva em março)
    df = df.drop_duplicates(subset=["vendedor", "data", "produto", "valor"])

    return df


# ---------------------------------------------------------
# ETAPA 3: Consolidação
# ---------------------------------------------------------
def consolidar(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    """Junta todos os DataFrames em um único, após limpeza individual."""
    limpos = [limpar_dados(df) for df in dataframes]
    return pd.concat(limpos, ignore_index=True)


# ---------------------------------------------------------
# ETAPA 4: Métricas/resumo
# ---------------------------------------------------------
def gerar_resumo(df: pd.DataFrame) -> pd.DataFrame:
    """Soma o valor total vendido por categoria."""
    return df.groupby("categoria")["valor"].sum().reset_index()


# ---------------------------------------------------------
# ETAPA 5: Exportação
# ---------------------------------------------------------
def exportar(df: pd.DataFrame, caminho_saida: str):
    df.to_excel(caminho_saida, index=False)
    print(f"Relatório exportado para: {caminho_saida}")


# ---------------------------------------------------------
# ETAPA 6 (Fase 3): Resumo em linguagem natural via LLM
# ---------------------------------------------------------
def gerar_resumo_ia(resumo_df: pd.DataFrame, api_key: str) -> str:
    """Envia o resumo estatístico para a API da Anthropic e recebe um texto explicativo."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": f"Resuma esses dados em português, de forma objetiva, "
                            f"destacando os pontos mais relevantes:\n\n{resumo_df.to_string()}"
            }
        ],
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        dados = response.json()
        return dados["content"][0]["text"]
    elif response.status_code == 401:
        return "Erro: API key inválida ou ausente."
    elif response.status_code == 429:
        return "Erro: limite de requisições excedido. Tente novamente em instantes."
    else:
        return f"Erro inesperado ({response.status_code}): {response.text}"


# ---------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------------------------------------
if __name__ == "__main__":
    PASTA_ENTRADA = "dados_brutos"
    CAMINHO_SAIDA = "relatorio_final/relatorio_consolidado.xlsx"

    dfs = ler_arquivos(PASTA_ENTRADA)
    df_consolidado = consolidar(dfs)
    df_resumo = gerar_resumo(df_consolidado)
    exportar(df_resumo, CAMINHO_SAIDA)

    # Fase 3 — descomente quando estiver pronto para integrar IA
    # api_key = os.environ["ANTHROPIC_API_KEY"]
    # texto_ia = gerar_resumo_ia(df_resumo, api_key)
    # print("\nResumo gerado pela IA:\n", texto_ia)
