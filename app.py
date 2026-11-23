
import pandas as pd
import plotly.express as px
import streamlit as st

from tratamento import carregar_dados


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Vendas de Videogames",
    layout="wide"
)

# CARREGAMENTO DOS DADOS
df = carregar_dados()

COR_PRINCIPAL = "#FF4B4B"

# APRESENTAÇÃO DO PROJETO
st.title("Vendas de Videogames pelo Mundo")

st.markdown(
    """
    **Integrantes:** Nikole Maio e Kaio Kleinkauf

    **Tema:** análise das vendas globais de videogames.

    **Objetivo:** identificar gêneros, plataformas e jogos de maior
    destaque comercial, como as vendas variaram ao longo dos anos
    e as diferenças entre América do Norte, Europa, Japão
    e outras regiões.

    **Conjunto de dados:** Video Game Sales, disponibilizado no
    Kaggle e baseado em informações do VGChartz.

    **Fonte:** [Kaggle - Video Game Sales](https://www.kaggle.com/datasets/gregorut/videogamesales)

    **Unidade de medida:** milhões de unidades vendidas.
    """
)

# FILTROS INTERATIVOS
st.sidebar.header("Filtros (Clique para filtrar)")

generos = sorted(df["Genre"].dropna().unique())
plataformas = sorted(df["Platform"].dropna().unique())

generos_sel = st.sidebar.multiselect(
    "Gêneros",
    generos,
    default=[],
    placeholder="Todos os gêneros"
)

plataformas_sel = st.sidebar.multiselect(
    "Plataformas",
    plataformas,
    default=[],
    placeholder="Todas as plataformas"
)

ano_min = int(df["Year"].min())
ano_max = int(df["Year"].max())

ano_sel = st.sidebar.slider(
    "Período",
    ano_min,
    ano_max,
    (ano_min, ano_max)
)

nomes_regioes = {
    "NA_Sales": "América do Norte",
    "EU_Sales": "Europa",
    "JP_Sales": "Japão",
    "Other_Sales": "Outras regiões"
}

regiao = st.sidebar.selectbox(
    "Região em destaque",
    list(nomes_regioes.keys()),
    format_func=lambda x: nomes_regioes[x]
)

nome_regiao = nomes_regioes[regiao]

# APLICAÇÃO DOS FILTROS
df_f = df.copy()

if generos_sel:
    df_f = df_f[
        df_f["Genre"].isin(generos_sel)
    ]

if plataformas_sel:
    df_f = df_f[
        df_f["Platform"].isin(plataformas_sel)
    ]

# O período selecionado filtra os registros com ano conhecido.
df_f = df_f[
    df_f["Year"].between(ano_sel[0], ano_sel[1])
].copy()

if df_f.empty:
    st.warning(
        "Nenhum registro encontrado com os filtros selecionados. "
        "Ajuste os filtros para continuar."
    )
    st.stop()

# INDICADORES ATUALIZADOS
st.subheader("Indicadores dos Dados Selecionados")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Registros", len(df_f))

c2.metric(
    "Vendas globais (mi)",
    round(df_f["Global_Sales"].sum(), 1)
)

c3.metric(
    "Plataformas",
    df_f["Platform"].nunique()
)

c4.metric(
    "Gêneros",
    df_f["Genre"].nunique()
)

st.caption(
    f"Período selecionado: {ano_sel[0]} a {ano_sel[1]} | "
    f"Registros analisados: {len(df_f)} | "
    f"Vendas globais: {df_f['Global_Sales'].sum():.2f} milhões"
)

anos_ausentes = int(df["Year"].isna().sum())

st.info(
    f"A base tratada possui {len(df)} registros. "
    f"Desses, {anos_ausentes} não possuem ano de lançamento "
    "identificado e não participam das análises filtradas "
    "por período. Os valores representam vendas registradas "
    "no conjunto de dados, não vendas atuais."
)

# ETAPA 3 - ANÁLISE EXPLORATÓRIA
st.subheader("Etapa 3 — Análise Exploratória e Gráficos")

# GRÁFICO 1 - VENDAS POR GÊNERO
st.header("1. Vendas por gênero")

g = (
    df_f.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig = px.bar(
    g,
    x="Genre",
    y="Global_Sales",
    text_auto=".2f",
    labels={
        "Genre": "Gênero",
        "Global_Sales": "Vendas globais (mi)"
    },
    title="Vendas globais por gênero",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig.update_layout(xaxis_tickangle=-35)

st.plotly_chart(fig, use_container_width=True)

genero_lider = g.iloc[0]

st.write(
    f"Entre os registros selecionados, o gênero "
    f"**{genero_lider['Genre']}** apresenta o maior volume "
    f"de vendas, com **{genero_lider['Global_Sales']:.2f} "
    f"milhões de unidades**."
)

# GRÁFICO 2 - VENDAS POR PLATAFORMA
st.header("2. Vendas por plataforma")

p = (
    df_f.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

fig = px.bar(
    p,
    x="Platform",
    y="Global_Sales",
    text_auto=".1f",
    labels={
        "Platform": "Plataforma",
        "Global_Sales": "Vendas globais (mi)"
    },
    title="Top 15 plataformas",
    color_discrete_sequence=[COR_PRINCIPAL]
)

st.plotly_chart(fig, use_container_width=True)

plataforma_lider = p.iloc[0]

st.write(
    f"A plataforma **{plataforma_lider['Platform']}** "
    f"lidera as vendas no conjunto selecionado, "
    f"com **{plataforma_lider['Global_Sales']:.2f} "
    f"milhões de unidades**."
)

# GRÁFICO 3 - JOGOS MAIS VENDIDOS
st.header("3. Jogos mais vendidos")

j = (
    df_f.groupby("Name")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    j,
    x="Global_Sales",
    y="Name",
    orientation="h",
    text_auto=".1f",
    labels={
        "Name": "Jogo",
        "Global_Sales": "Vendas globais (mi)"
    },
    title="Top 10 jogos por vendas acumuladas",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig.update_layout(
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig, use_container_width=True)

jogo_lider = j.iloc[0]

st.write(
    f"O jogo **{jogo_lider['Name']}** possui o maior "
    f"volume acumulado de vendas na seleção, com "
    f"**{jogo_lider['Global_Sales']:.2f} milhões "
    f"de unidades**."
)

st.caption(
    "Quando um mesmo jogo aparece em diferentes plataformas, "
    "suas vendas são somadas para esta comparação."
)

# GRÁFICO 4 - VENDAS AO LONGO DOS ANOS
st.header("4. Vendas ao longo dos anos")

a = (
    df_f[df_f["AnoValido"]]
    .groupby("Year")["Global_Sales"]
    .sum()
    .reset_index()
    .sort_values("Year")
)

fig = px.line(
    a,
    x="Year",
    y="Global_Sales",
    markers=True,
    labels={
        "Year": "Ano",
        "Global_Sales": "Vendas globais (mi)"
    },
    title="Vendas globais por ano",
    color_discrete_sequence=[COR_PRINCIPAL]
)

st.plotly_chart(fig, use_container_width=True)

if not a.empty:
    ano_pico = a.loc[a["Global_Sales"].idxmax()]

    st.write(
        f"O maior volume de vendas registrado no período "
        f"selecionado ocorreu em **{int(ano_pico['Year'])}**, "
        f"com **{ano_pico['Global_Sales']:.2f} milhões "
        f"de unidades**."
    )

st.caption(
    "A série representa os registros disponíveis no dataset. "
    "Os anos mais recentes podem apresentar cobertura incompleta, "
    "portanto uma queda não significa necessariamente redução "
    "real das vendas de todo o mercado."
)

# GRÁFICO 5 - DIFERENÇAS ENTRE REGIÕES
st.header("5. Diferenças entre regiões")

regioes = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales"
]

nomes = [
    "América do Norte",
    "Europa",
    "Japão",
    "Outras"
]

totais = [df_f[r].sum() for r in regioes]

fig = px.pie(
    values=totais,
    names=nomes,
    hole=0.4,
    title="Participação regional nas vendas",
    color_discrete_sequence=px.colors.sequential.Reds_r
)

st.plotly_chart(fig, use_container_width=True)

vendas_regioes = pd.Series(
    totais,
    index=nomes
)

maior_regiao = vendas_regioes.idxmax()

participacao = (
    vendas_regioes.max() / vendas_regioes.sum()
) * 100

st.write(
    f"A região com maior participação nas vendas "
    f"selecionadas é **{maior_regiao}**, representando "
    f"aproximadamente **{participacao:.1f}%** "
    f"do total regional registrado."
)

# GRÁFICO 6 - GÊNEROS POR REGIÃO
st.header("6. Gêneros em destaque por região")

gr = (
    df_f.groupby("Genre")[regiao]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    gr,
    x="Genre",
    y=regiao,
    text_auto=".1f",
    labels={
        "Genre": "Gênero",
        regiao: f"Vendas em {nome_regiao} (mi)"
    },
    title=f"Top 10 gêneros em {nome_regiao}",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig.update_layout(xaxis_tickangle=-35)

st.plotly_chart(fig, use_container_width=True)

genero_regional = gr.iloc[0]

st.write(
    f"Na região **{nome_regiao}**, o gênero com "
    f"maior volume de vendas na seleção é "
    f"**{genero_regional['Genre']}**, com "
    f"**{genero_regional[regiao]:.2f} milhões "
    f"de unidades**."
)

# ETAPA 4 - ANÁLISES COMPLEMENTARES
st.subheader("Etapa 4 — Análises Complementares")

# GRÁFICO 7 - DISTRIBUIÇÃO DAS VENDAS
st.header("7. Distribuição das vendas")

lim = df_f["Global_Sales"].quantile(0.95)

dados_histograma = df_f[
    df_f["Global_Sales"] <= lim
]

fig = px.histogram(
    dados_histograma,
    x="Global_Sales",
    nbins=40,
    labels={
        "Global_Sales": "Vendas globais (mi)"
    },
    title="Histograma de vendas (até o percentil 95)",
    color_discrete_sequence=[COR_PRINCIPAL]
)

st.plotly_chart(fig, use_container_width=True)

mediana = df_f["Global_Sales"].median()
media = df_f["Global_Sales"].mean()

st.write(
    f"Na seleção, a média de vendas por registro é "
    f"**{media:.2f} milhões**, enquanto a mediana "
    f"é **{mediana:.2f} milhões**."
)

if media > mediana:
    st.write(
        "A média superior à mediana sugere que "
        "registros com vendas elevadas influenciam "
        "o resultado geral."
    )
elif media < mediana:
    st.write(
        "A mediana é superior à média nesta seleção, "
        "indicando uma distribuição diferente da "
        "observada na base completa."
    )
else:
    st.write(
        "A média e a mediana apresentam valores iguais "
        "quando arredondadas nesta seleção."
    )

st.caption(
    "O histograma mostra registros até o percentil 95 "
    "para facilitar a visualização. Os 5% superiores "
    "não aparecem no gráfico, mas continuam incluídos "
    "nas métricas e nas demais análises."
)

# GRÁFICO 8 - CORRELAÇÃO ENTRE REGIÕES
st.header("8. Relação entre regiões")

corr = df_f[regioes].corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    x=nomes,
    y=nomes,
    color_continuous_scale="Reds",
    zmin=-1,
    zmax=1,
    title="Correlação entre vendas regionais"
)

st.plotly_chart(fig, use_container_width=True)

correlacao_na_eu = corr.loc[
    "NA_Sales", "EU_Sales"
]

if pd.notna(correlacao_na_eu):
    st.write(
        f"A correlação entre as vendas na América "
        f"do Norte e na Europa é de "
        f"**{correlacao_na_eu:.2f}** na seleção atual."
    )
else:
    st.write(
        "Não há variação suficiente nos dados "
        "selecionados para calcular essa correlação."
    )

st.caption(
    "A correlação varia de -1 a 1. Valores próximos "
    "de 1 indicam uma relação positiva forte; "
    "próximos de -1 indicam uma relação negativa forte; "
    "e próximos de zero indicam pouca relação linear. "
    "Correlação não significa causalidade."
)

# CONSIDERAÇÕES FINAIS
st.header("Considerações finais")

st.write(
    "O dashboard permite comparar as vendas de videogames "
    "por gênero, plataforma, jogo, período e região. "
    "Os filtros ajudam a identificar diferenças entre "
    "grupos e períodos específicos, transformando "
    "os registros do dataset em informações para análise."
)

st.caption(
    "Fonte: Video Game Sales (Kaggle / VGChartz). "
    "As conclusões se referem aos dados disponíveis "
    "no conjunto analisado."
)
