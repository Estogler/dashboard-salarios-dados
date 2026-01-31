import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide"
)

pio.renderers.default = "browser"

# ================= CARREGAMENTO DOS DADOS =================
URL = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
df = pd.read_csv(URL)

# ================= SIDEBAR =================
st.sidebar.header("🔍 Filtros")

anos = st.sidebar.multiselect(
    "Ano",
    sorted(df["ano"].unique()),
    default=sorted(df["ano"].unique())
)

senioridades = st.sidebar.multiselect(
    "Senioridade",
    sorted(df["senioridade"].unique()),
    default=sorted(df["senioridade"].unique())
)

contratos = st.sidebar.multiselect(
    "Tipo de Contrato",
    sorted(df["contrato"].unique()),
    default=sorted(df["contrato"].unique())
)

tamanhos = st.sidebar.multiselect(
    "Tamanho da Empresa",
    sorted(df["tamanho_empresa"].unique()),
    default=sorted(df["tamanho_empresa"].unique())
)

# ================= FILTRAGEM =================
df_filtrado = df[
    (df["ano"].isin(anos)) &
    (df["senioridade"].isin(senioridades)) &
    (df["contrato"].isin(contratos)) &
    (df["tamanho_empresa"].isin(tamanhos))
]

# ================= TÍTULO =================
st.title("📊 Dashboard de Salários na Área de Dados")
st.markdown(
    "Análise interativa de salários na área de dados. "
    "Use os filtros à esquerda para explorar os dados."
)

# ================= KPIs =================
st.subheader("Métricas gerais (USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_max = df_filtrado["usd"].max()
    total = len(df_filtrado)
    cargo_freq = df_filtrado["cargo"].mode()[0]
else:
    salario_medio = salario_max = total = 0
    cargo_freq = "—"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário médio", f"${salario_medio:,.0f}")
c2.metric("Salário máximo", f"${salario_max:,.0f}")
c3.metric("Registros", f"{total:,}")
c4.metric("Cargo mais frequente", cargo_freq)

st.markdown("---")

# ================= GRÁFICOS =================
st.subheader("Visualizações")

col1, col2 = st.columns(2)

# ---- Top cargos ----
with col1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado
            .groupby("cargo")["usd"]
            .mean()
            .nlargest(10)
            .sort_values()
            .reset_index()
        )

        fig = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 cargos por salário médio",
            labels={"usd": "Salário médio (USD)", "cargo": ""}
        )

        st.plotly_chart(fig, use_container_width=True)

# ---- Histograma ----
with col2:
    if not df_filtrado.empty:
        fig = px.histogram(
            df_filtrado,
            x="usd",
            nbins=30,
            title="Distribuição de salários",
            labels={"usd": "Salário anual (USD)"}
        )

        st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

# ---- Trabalho remoto ----
with col3:
    remoto = df_filtrado["remoto"].value_counts().reset_index()
    remoto.columns = ["tipo_trabalho", "quantidade"]

    fig = px.pie(
        remoto,
        names="tipo_trabalho",
        values="quantidade",
        title="Tipo de trabalho",
        hole=0.5
    )

    st.plotly_chart(fig, use_container_width=True)

# ---- MAPA (COLUNA CORRETA) ----
with col4:
    df_ds = df_filtrado[df_filtrado["cargo"] == "Data Scientist"]

    if not df_ds.empty:
        media_pais = (
            df_ds
            .groupby("residencia_iso3")["usd"]
            .mean()
            .reset_index()
        )

        fig = px.choropleth(
            media_pais,
            locations="residencia_iso3",
            locationmode="ISO-3",
            color="usd",
            color_continuous_scale="RdYlGn",
            title="Salário médio de Data Scientists por país",
            labels={"usd": "Salário médio (USD)"}
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de Data Scientist para o mapa.")

# ================= TABELA =================
st.subheader("Dados detalhados")
st.dataframe(df_filtrado)
