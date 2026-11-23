
from pathlib import Path
import pandas as pd


def carregar_dados(caminho="dados/vgsales.csv"):
    pasta = Path(__file__).resolve().parent
    arquivo = pasta / caminho

    df = pd.read_csv(arquivo)
    df.columns = [coluna.strip() for coluna in df.columns]

    colunas_texto = ["Name", "Platform", "Genre", "Publisher"]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    df = df.dropna(
        subset=["Name", "Platform", "Genre"]
    ).copy()

    df["Publisher"] = df["Publisher"].fillna(
        "Nao informado"
    )

    ano = pd.to_numeric(df["Year"], errors="coerce")

    ano = ano.where(
        ano.isna() | ano.mod(1).eq(0)
    )

    df["Year"] = ano.astype("Int64")

    df["Rank"] = pd.to_numeric(
        df["Rank"], errors="coerce"
    ).astype("Int64")

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

    vendas_invalidas = (
        df[colunas_vendas].isna().any(axis=1)
        | df[colunas_vendas].lt(0).any(axis=1)
    )

    df = df.loc[~vendas_invalidas].copy()

    df = df.drop_duplicates().copy()

    df["AnoValido"] = df["Year"].notna()

    df["Decada"] = (
        df["Year"] // 10 * 10
    ).astype("Int64")

    df["Soma_Regioes"] = (
        df["NA_Sales"]
        + df["EU_Sales"]
        + df["JP_Sales"]
        + df["Other_Sales"]
    )

    df = df.reset_index(drop=True)

    return df
