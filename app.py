import pandas as pd
import plotly.express as px
import streamlit as st

from tratamento import carregar_dados

st.set_page_config(page_title="Vendas de Videogames", layout="wide")

df = carregar_dados()

st.title("Vendas de Videogames pelo Mundo")
st.markdown(
    """
    **Tema:** análise das vendas globais de videogames.
    **Objetivo:** identificar gêneros, plataformas e jogos de maior destaque comercial,
    como as vendas variaram ao longo dos anos e as diferenças entre América do Norte,
    Europa, Japão e outras regiões.
    **Fonte:** Video Game Sales (Kaggle / VGChartz). Vendas em milhões de unidades.
    """
)

st.subheader("Indicadores gerais")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jogos", len(df))
c2.metric("Vendas globais (mi)", round(df["Global_Sales"].sum(), 1))
c3.metric("Plataformas", df["Platform"].nunique())
c4.metric("Gêneros", df["Genre"].nunique())

st.sidebar.header("Filtros")
generos = sorted(df["Genre"].dropna().unique())
plataformas = sorted(df["Platform"].dropna().unique())
generos_sel = st.sidebar.multiselect("Gêneros", generos, default=generos)
plataformas_sel = st.sidebar.multiselect("Plataformas", plataformas, default=plataformas)
ano_min = int(df["Year"].min())
ano_max = int(df["Year"].max())
ano_sel = st.sidebar.slider("Período", ano_min, ano_max, (ano_min, ano_max))
regiao = st.sidebar.selectbox(
    "Região em destaque",
    ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"],
    format_func=lambda x: {
        "NA_Sales": "América do Norte",
        "EU_Sales": "Europa",
        "JP_Sales": "Japão",
        "Other_Sales": "Outras regiões",
    }[x],
)
nome_regiao = {
    "NA_Sales": "América do Norte",
    "EU_Sales": "Europa",
    "JP_Sales": "Japão",
    "Other_Sales": "Outras regiões",
}[regiao]

df_f = df[
    df["Genre"].isin(generos_sel)
    & df["Platform"].isin(plataformas_sel)
    & df["Year"].between(ano_sel[0], ano_sel[1])
].copy()

if df_f.empty:
    st.warning("Nenhum registro com os filtros selecionados.")
    st.stop()

st.caption(f"Registros filtrados: {len(df_f)} | Vendas: {round(df_f['Global_Sales'].sum(), 1)} mi")

st.header("1. Vendas por gênero")
g = df_f.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False).reset_index()
fig = px.bar(g, x="Genre", y="Global_Sales", text_auto=".2f",
             labels={"Genre": "Gênero", "Global_Sales": "Vendas globais (mi)"},
             title="Vendas globais por gênero")
fig.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig, use_container_width=True)
st.write("Ação lidera em vendas totais, seguida por Esportes e Tiro. Estratégia e Aventura vendem menos no total.")

st.header("2. Vendas por plataforma")
p = df_f.groupby("Platform")["Global_Sales"].sum().sort_values(ascending=False).head(15).reset_index()
fig = px.bar(p, x="Platform", y="Global_Sales", text_auto=".1f",
             labels={"Platform": "Plataforma", "Global_Sales": "Vendas globais (mi)"},
             title="Top 15 plataformas")
st.plotly_chart(fig, use_container_width=True)
st.write("PS2 é a plataforma mais vendida, seguida por X360, PS3, Wii e DS.")

st.header("3. Jogos mais vendidos")
j = df_f.groupby("Name")["Global_Sales"].sum().sort_values(ascending=False).head(10).reset_index()
fig = px.bar(j, x="Global_Sales", y="Name", orientation="h", text_auto=".1f",
             labels={"Name": "Jogo", "Global_Sales": "Vendas globais (mi)"},
             title="Top 10 jogos")
fig.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig, use_container_width=True)
st.write("Wii Sports é o mais vendido, com folga. Quatro dos cinco primeiros são da Nintendo.")

st.header("4. Vendas ao longo dos anos")
a = df_f[df_f["AnoValido"]].groupby("Year")["Global_Sales"].sum().reset_index()
fig = px.line(a, x="Year", y="Global_Sales", markers=True,
              labels={"Year": "Ano", "Global_Sales": "Vendas globais (mi)"},
              title="Vendas globais por ano")
st.plotly_chart(fig, use_container_width=True)
st.write("As vendas crescem até o pico em 2008 e depois caem. O dado de 2016 é parcial.")

st.header("5. Diferenças entre regiões")
regioes = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
nomes = ["América do Norte", "Europa", "Japão", "Outras"]
totais = [df_f[r].sum() for r in regioes]
fig = px.pie(values=totais, names=nomes, hole=0.4,
             title="Participação regional nas vendas")
st.plotly_chart(fig, use_container_width=True)

gr = df_f.groupby("Genre")[regiao].sum().sort_values(ascending=False).head(10).reset_index()
fig = px.bar(gr, x="Genre", y=regiao, text_auto=".1f",
             labels={"Genre": "Gênero", regiao: f"Vendas em {nome_regiao} (mi)"},
             title=f"Top 10 gêneros em {nome_regiao}")
fig.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig, use_container_width=True)
st.write(f"Em {nome_regiao}, o ranking de gêneros pode diferir do global. No Japão, RPG tem peso muito maior.")

st.header("6. Distribuição das vendas")
ca, cb = st.columns(2)
with ca:
    lim = df_f["Global_Sales"].quantile(0.95)
    fig = px.histogram(df_f[df_f["Global_Sales"] <= lim], x="Global_Sales", nbins=40,
                       labels={"Global_Sales": "Vendas globais (mi)"},
                       title="Histograma até o percentil 95")
    st.plotly_chart(fig, use_container_width=True)
with cb:
    fig = px.box(df_f, y="Global_Sales", log_y=True,
                 labels={"Global_Sales": "Vendas globais (mi, log)"},
                 title="Boxplot em escala log")
    st.plotly_chart(fig, use_container_width=True)
st.write("As vendas são muito assimétricas: a maioria vende pouco e poucos jogos concentram grande parte do total.")

st.header("7. Relação entre regiões")
corr = df_f[regioes].corr()
fig = px.imshow(corr, text_auto=".2f", x=nomes, y=nomes,
                color_continuous_scale="Blues",
                title="Correlação entre vendas regionais")
st.plotly_chart(fig, use_container_width=True)
st.write("América do Norte e Europa têm correlação alta; com o Japão a correlação é menor.")

st.divider()
st.caption("Projeto acadêmico — Análise de Dados e Desenvolvimento de Dashboard Interativo. Fonte: Video Game Sales (Kaggle / VGChartz).")