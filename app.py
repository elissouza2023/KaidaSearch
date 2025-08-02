# app.py
import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações iniciais da página
st.set_page_config(page_title="Relatório ESG - TI", layout="wide")

# Logotipo e cabeçalho
logo = Image.open("logopq.png")
st.image(logo, width=200)
st.markdown("## Kaida Search — Análise de Conhecimento ESG em TI")

# Estilo customizado
st.markdown(
    """
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .reportview-container .markdown-text-container {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Introdução executiva
st.markdown("""
### 🌟 Objetivo da ferramenta
Este relatório interativo permite avaliar o conhecimento e a aceitação das práticas ESG entre colaboradores de TI da sua empresa. Os dados são obtidos por meio de um formulário padronizado e transformados automaticamente em um relatório executivo.
""")

st.title("📊 Relatório Executivo ESG na TI")
st.markdown("Este relatório resume, de forma estratégica, como o perfil dos colaboradores e o interesse pelo tema ESG se relacionam com o nível de conhecimento sobre o assunto.")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("📅 Envie o arquivo .CSV exportado do Google Forms", type="csv")

if not uploaded_file:
    st.info("Por favor, envie o arquivo CSV da pesquisa para visualizar o relatório.")

if uploaded_file:
    # Carregamento e pré-processamento
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ', regex=False)

    # Seleção e renomeação de colunas
    df_selected = df[[ 
        '1. Qual a sua faixa etária?',
        '2. Qual é o seu nível de formação?',
        '5. Você acha importante que profissionais de TI conheçam e apliquem princípios ESG no seu trabalho?',
        '7. Na sua opinião, qual área da TI pode mais contribuir com as práticas ESG?',
        '3. Você já ouviu falar sobre práticas ESG (Ambiental, Social e Governança)?',
        '4.Você saberia explicar o que são práticas ESG?',
        '6. Na empresa onde você trabalha (ou trabalhou mais recentemente), existe alguma política ou ação voltada às práticas ESG?'
    ]].dropna()

    df_selected.columns = [
        'Faixa Etária', 'Formação', 'Importância ESG', 'Área TI Contribui',
        'Conhece ESG', 'Sabe Explicar ESG', 'Conhece Política ESG'
    ]

    # Codificação para correlação
    df_encoded = df_selected.apply(lambda col: col.astype('category').cat.codes)
    X_cols = ['Faixa Etária', 'Formação', 'Importância ESG', 'Área TI Contribui']
    Y_cols = ['Conhece ESG', 'Sabe Explicar ESG', 'Conhece Política ESG']
    corr = df_encoded[X_cols + Y_cols].corr()
    corr_xy = corr.loc[X_cols, Y_cols]

    # Tradução para linguagem executiva
    colunas_legendas = {
        'Faixa Etária': 'a faixa etária',
        'Formação': 'a formação educacional',
        'Importância ESG': 'a percepção de importância do ESG',
        'Área TI Contribui': 'a área da TI apontada como mais relevante para ESG',
        'Conhece ESG': 'o conhecimento sobre ESG',
        'Sabe Explicar ESG': 'a capacidade de explicar ESG',
        'Conhece Política ESG': 'o conhecimento sobre políticas ESG da empresa'
    }

    corr_xy.index = [colunas_legendas[c] for c in corr_xy.index]
    corr_xy.columns = [colunas_legendas[c] for c in corr_xy.columns]

    # Geração dos insights
    def gerar_insights_executivos(corr_df):
        insights = []
        for x_var in corr_df.index:
            for y_var in corr_df.columns:
                valor_corr = corr_df.loc[x_var, y_var]

                if valor_corr >= 0.5:
                    frase = f"Colaboradores para os quais **{x_var}** é mais evidente tendem a demonstrar maior familiaridade com **{y_var}**."
                elif valor_corr >= 0.3:
                    frase = f"Existe uma tendência de que **{x_var}** esteja associada a maior familiaridade com **{y_var}**."
                elif valor_corr >= 0.1:
                    frase = f"Foi observada uma leve associação entre **{x_var}** e **{y_var}**, sugerindo uma possível influência sutil."
                elif valor_corr <= -0.3:
                    frase = f"Pessoas com **{x_var}** tendem a apresentar menor envolvimento com **{y_var}**, o que pode indicar barreiras que merecem atenção."
                elif valor_corr <= -0.1:
                    frase = f"Existe uma leve tendência de que **{x_var}** esteja associada a menor familiaridade com **{y_var}**."
                else:
                    continue

                insights.append("- " + frase)

        return "\n".join(insights)

    relatorio = gerar_insights_executivos(corr_xy)

    # Exibição do relatório
    st.subheader("📌 Recomendações Estratégicas com base nos dados:")
    st.markdown(relatorio)

    # Função para gerar o PDF
    def gerar_pdf(texto):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "RELATÓRIO EXECUTIVO - ESG NA TI\n", align='L')
        for linha in texto.split('\n'):
            pdf.multi_cell(0, 10, linha, align='L')
        return pdf.output(dest='S').encode('latin-1')

    # Geração e botão de download do PDF
    pdf_bytes = gerar_pdf(relatorio)
    st.download_button(
        label="📄 Baixar relatório em PDF",
        data=pdf_bytes,
        file_name="relatorio_esg_ti.pdf",
        mime="application/pdf"
    )

    # Heatmap de correlação
    st.subheader("🧽 Mapa de Correlação entre Perfil/Interesse e Conhecimento sobre ESG")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr_xy, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=0.5, cbar=True, ax=ax)
    ax.set_title("Correlação entre variáveis de perfil/interesse e conhecimento/aceitação ESG", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    st.pyplot(fig)
