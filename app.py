import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Configurazione Dashboard
st.set_page_config(page_title="GE-LU COCKPIT", layout="wide")
st.title("🛰️ GE-LU COCKPIT | Sniper 10-5-5")

# Parametri dai tuoi dati reali
P_REF_USA = 419.43  # Prezzo SP5C dal tuo Excel
P_REF_DIV = 52.83   # Prezzo TDIV dal tuo Excel
SOGLIA_MOLLA = 0.012
SOGLIA_RECONVERT = 0.025

# Download dati
@st.cache_data(ttl=300)
def get_data():
    # Usiamo IUSP.MI per LYSP (S&P 500) e TDIV.MI
    tickers = {'IUSP.MI': 'LYSP', 'TDIV.MI': 'TDIV'}
    df = yf.download(list(tickers.keys()), period="5d", interval="15m", progress=False)['Close']
    df.columns = [tickers[c] for c in df.columns]
    return df.dropna()

try:
    df = get_data()
    p_ora = df.iloc[-1]
    p_ieri = df.iloc[-2]

    # Logica GeLu
    spread_tdiv = (p_ora['TDIV']/p_ieri['TDIV']) - (p_ora['LYSP']/p_ieri['LYSP'])
    # Calcolo recupero basato sui tuoi prezzi di carico
    recupero = ((p_ora['LYSP']/P_REF_USA)-1) - ((p_ora['TDIV']/P_REF_DIV)-1)

    # Visualizzazione KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("Spread Oggi", f"{spread_tdiv:+.2%}")
    c2.metric("Recupero Reale", f"{recupero:+.2%}")
    c3.metric("Status", "🔥 SWITCH" if spread_tdiv >= 0.006 else "⚪ NEUTRO")

    if recupero >= SOGLIA_RECONVERT:
        st.success(f"🎯 TARGET RAGGIUNTO ({recupero:.2%})! Valuta Reconvert.")
    
    st.line_chart((df / df.iloc[0]) - 1)
    st.caption(f"Ultimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.error(f"Errore nel caricamento dati: {e}")
