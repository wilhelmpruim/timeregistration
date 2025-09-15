
import streamlit as st
import pandas as pd
import datetime

st.title("🏃 Tijdregistratie voetbaltraining - Versie 2")

# Flexibele invoer van deelnemers
namen_input = st.text_area("Voer namen in (één per regel):", """Kind 1
Kind 2
Kind 3
Kind 4
Kind 5
Kind 6""")
namen = [naam.strip() for naam in namen_input.split("\n") if naam.strip()]

# Initialiseer session state
if 'tijden_df' not in st.session_state or st.session_state.get('namen') != namen:
    st.session_state.tijden_df = pd.DataFrame({
        'Naam': namen,
        'Starttijd': [None]*len(namen),
        'Tussentijd': [None]*len(namen),
        'Eindtijd': [None]*len(namen)
    })
    st.session_state.namen = namen

# Centrale startknop
if st.button("🚦 Start training voor iedereen"):
    nu = datetime.datetime.now().strftime("%H:%M:%S")
    for i in range(len(st.session_state.tijden_df)):
        st.session_state.tijden_df.at[i, 'Starttijd'] = nu

# Functie om individuele tijden te registreren
def registreer_tijd(naam):
    nu = datetime.datetime.now().strftime("%H:%M:%S")
    rij = st.session_state.tijden_df[st.session_state.tijden_df['Naam'] == naam].index[0]
    if pd.isna(st.session_state.tijden_df.at[rij, 'Tussentijd']):
        st.session_state.tijden_df.at[rij, 'Tussentijd'] = nu
    elif pd.isna(st.session_state.tijden_df.at[rij, 'Eindtijd']):
        st.session_state.tijden_df.at[rij, 'Eindtijd'] = nu

# Toon knoppen per deelnemer in 2 kolommen
st.subheader("👤 Deelnemers")
kol1, kol2 = st.columns(2)
for i, naam in enumerate(namen):
    if i % 2 == 0:
        with kol1:
            if st.button(f"Registreer voor {naam}"):
                registreer_tijd(naam)
    else:
        with kol2:
            if st.button(f"Registreer voor {naam}"):
                registreer_tijd(naam)

# Toon tabel met tijden
st.subheader("📋 Geregistreerde tijden")
st.dataframe(st.session_state.tijden_df)

# Download als CSV
csv = st.session_state.tijden_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download als CSV", data=csv, file_name="tijdregistratie_training_v2.csv", mime="text/csv")
