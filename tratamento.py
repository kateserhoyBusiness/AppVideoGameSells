import pandas as pd

def carregar_dados(caminho="dados/vgsales.csv"):
    df = pd.read_csv(caminho)
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Global_Sales"].notna() & (df["Global_Sales"] > 0)]
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["AnoValido"] = df["Year"].notna()
    df["Soma_Regioes"] = df["NA_Sales"] + df["EU_Sales"] + df["JP_Sales"] + df["Other_Sales"]
    return df