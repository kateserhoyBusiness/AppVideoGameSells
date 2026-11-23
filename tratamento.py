
from pathlib import Path
import pandas as pd


def carregar_dados(caminho="dados/vgsales.csv"):
    # Localiza o CSV a partir da pasta do projeto.
    pasta = Path(__file__).resolve().parent
    arquivo = pasta / caminho

    # 1. Leitura dos dados
    df = pd.read_csv(arquivo)
    df.columns = [coluna.strip() for coluna in df.columns]

    # 2. Padronização das colunas de texto
    colunas_texto = ["Name", "Platform", "Genre", "Publisher"]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # 3. Tratamento de valores ausentes
    # Nome, plataforma e gênero são essenciais para a análise.
    df = df.dropna(
        subset=["Name", "Platform", "Genre"]
    ).copy()

    # Mantemos jogos sem editora identificada.
    df["Publisher"] = df["Publisher"].fillna(
        "Nao informado"
    )

    # 4. Correção dos tipos de dados
    ano = pd.to_numeric(df["Year"], errors="coerce")

    # Impede que anos fracionários sejam considerados válidos.
    ano = ano.where(
        ano.isna() | ano.mod(1).eq(0)
    )

    df["Year"] = ano.astype("Int64")

    df["Rank"] = pd.to_numeric(
        df["Rank"], errors="coerce"
    ).astype("Int64")

    # 5. Tratamento das colunas de vendas
    # Os valores representam milhões de unidades.
    colunas_vendas = [
        "NA_Sales",
        "EU_Sales",
        "JP_Sales",
        "Other_Sales",
        "Global_Sales"
    ]

    for coluna in colunas_vendas:
        df[coluna] = pd.to_numeric(
            df[coluna], errors="coerce"
        )

    # Remove registros com vendas ausentes ou negativas.
    vendas_invalidas = (
        df[colunas_vendas].isna().any(axis=1)
        | df[colunas_vendas].lt(0).any(axis=1)
    )

    df = df.loc[~vendas_invalidas].copy()

    # 6. Remoção de duplicatas completas
    # Jogos iguais em plataformas diferentes são preservados.
    df = df.drop_duplicates().copy()

    # 7. Criação de colunas auxiliares
    # Indica se o ano de lançamento é conhecido.
    df["AnoValido"] = df["Year"].notna()

    # Permite análises agrupadas por década.
    df["Decada"] = (
        df["Year"] // 10 * 10
    ).astype("Int64")

    # Soma das vendas registradas nas quatro regiões.
    df["Soma_Regioes"] = (
        df["NA_Sales"]
        + df["EU_Sales"]
        + df["JP_Sales"]
        + df["Other_Sales"]
    )

    # 8. Organização final
    df = df.reset_index(drop=True)

    return df
