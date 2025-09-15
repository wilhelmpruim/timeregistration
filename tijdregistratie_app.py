
import streamlit as st
import pandas as pd
import datetime

st.title("🏃 Tijdregistratie voetbaltraining")

# Flexibele invoer van deelnemers
namen_input = st.text_area("Voer namen in (één per regel):", """Kind 1
Kind 2
Kind 3""")
namen = [naam.strip() for naam in namen_input.split("
") if naam.strip()]

# Initialiseer session state
if 'tijden_df' not in st.session_state or st.session_state.get('namen') != namen:
    st.session_state.tijden_df = pd.DataFrame({
        'Naam': namen,
        'Starttijd': [None]*len(namen),
        'Tussentijd': [None]*len(namen),
        'Eindtijd': [None]*len(namen)
    })
    st.session_state.namen = namen

# Functie om tijd te registreren
def registreer_tijd(naam):
    nu = datetime.datetime.now().strftime("%H:%M:%S")
    rij = st.session_state.tijden_df[st.session_state.tijden_df['Naam'] == naam].index[0]
    if pd.isna(st.session_state.tijden_df.at[rij, 'Starttijd']):
        st.session_state.tijden_df.at[rij, 'Starttijd'] = nu
    elif pd.isna(st.session_state.tijden_df.at[rij, 'Tussentijd']):
        st.session_state.tijden_df.at[rij, 'Tussentijd'] = nu
    elif pd.isna(st.session_state.tijden_df.at[rij, 'Eindtijd']):
        st.session_state.tijden_df.at[rij, 'Eindtijd'] = nu

# Toon knoppen per deelnemer
st.subheader("👤 Deelnemers")
for naam in namen:
    if st.button(naam):
        registreer_tijd(naam)

# Toon tabel met tijden
st.subheader("📋 Geregistreerde tijden")
st.dataframe(st.session_state.tijden_df)

# Download als CSV
csv = st.session_state.tijden_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download als CSV", data=csv, file_name="tijdregistratie_training.csv", mime="text/csv")
