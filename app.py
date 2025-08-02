# app.py
import streamlit as st
import pandas as pd
import io
from fpdf import FPDF

st.set_page_config(page_title="Relatório ESG - TI", layout="wide")

st.title("📊 Relatório Executivo ESG na TI")
st.markdown("Este relatório resume, de forma estratégica, como o perfil dos colaboradores e o interesse pelo tema ESG se relacionam com o nível de conhecimento sobre o assunto.")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("📥 Envie o arquivo .CSV exportado do Google Forms", type="csv")

if uploaded_file:
    # Carregamento e pré-processamento
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ', regex=False)

    # Seleção e renomeação
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

    # Renomeando para linguagem executiva
    colunas_legendas = {
        'Faixa Etária': 'a faixa etária',
        'Formação': 'a formação educacional',
        'Importância ESG': 'a percepção de importância do ESG',
        'Área TI Contribui': 'a área da TI apontada como mais relevante para ESG',
        'Conhece ESG': 'o conhecimento sobre ESG',
        'Sabe Explicar ESG': 'a capacidade de explicar ESG',
        'Conhece Política ESG': 'o conhecimento sobre políticas ESG da empresa'
    }

    corr.index = [colunas_legendas.get(c, c) for c in corr.index]
    corr.columns = [colunas_legendas.get(c, c) for c in corr.columns]
    corr_xy = corr.loc[list(colunas_legendas.values())[:4], list(colunas_legendas.values())[4:]]

    # Geração dos insights
    def gerar_insights_executivos(corr_df):
        insights = []
        for x_var in corr_df.index:
            for y_var in corr_df.columns:
                corr = corr_df.loc[x_var, y_var]

                if corr >= 0.5:
                    frase = f"Colaboradores para os quais **{x_var}** é mais evidente tendem a demonstrar maior familiaridade com **{y_var}**."
                elif corr >= 0.3:
                    frase = f"Existe uma tendência de que **{x_var}** esteja associada a maior familiaridade com **{y_var}**."
                elif corr >= 0.1:
                    frase = f"Foi observada uma leve associação entre **{x_var}** e **{y_var}**, sugerindo uma possível influência sutil."
                elif corr <= -0.3:
                    frase = f"Pessoas com **{x_var}** tendem a apresentar menor envolvimento com **{y_var}**, o que pode indicar barreiras que merecem atenção."
                elif corr <= -0.1:
                    frase = f"Existe uma leve tendência de que **{x_var}** esteja associada a menor familiaridade com **{y_var}**."
                else:
                    continue

                insights.append("- " + frase)

        return "\n".join(insights)

    relatorio = gerar_insights_executivos(corr_xy)

    # Exibição
    st.subheader("📌 Recomendações Estratégicas com base nos dados:")
    st.markdown(relatorio)

    # Exportar como PDF
    def gerar_pdf(texto):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for linha in texto.split('\n'):
            pdf.multi_cell(0, 10, linha)

        return pdf.output(dest='S').encode('latin-1')

    pdf_bytes = gerar_pdf("RELATÓRIO EXECUTIVO - ESG NA TI\n\n" + relatorio)

    st.download_button(
        label="📄 Baixar relatório em PDF",
        data=pdf_bytes,
        file_name="relatorio_esg_ti.pdf",
        mime="application/pdf"
    )
