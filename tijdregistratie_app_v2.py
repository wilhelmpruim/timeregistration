import streamlit as st
import pandas as pd
import datetime
st.title("🏃 Tijdregistratie voetbaltraining - Versie 3 (met afsluitknop)")

# Invoer deelnemers
namen_input = st.text_area("Voer namen in (één per regel):", """Kind 1
Kind 2
Kind 3
Kind 4
Kind 5
Kind 6""")
namen = [naam.strip() for naam in namen_input.split("\n") if naam.strip()]

# Invoer aantal ronden
aantal_ronden = st.number_input("Aantal ronden", min_value=1, max_value=10, value=1, step=1)

# Kolomnamen op basis van aantal ronden
kolommen = ['Naam', 'Starttijd']
for i in range(1, aantal_ronden):
    kolommen.append(f'Tussentijd {i}')
kolommen.append('Eindtijd')

# Initialiseer session state
if 'tijden_df' not in st.session_state or st.session_state.get('namen') != namen or st.session_state.get('ronden') != aantal_ronden:
    data = {kol: [None]*len(namen) for kol in kolommen}
    data['Naam'] = namen
    st.session_state.tijden_df = pd.DataFrame(data)
    st.session_state.namen = namen
    st.session_state.ronden = aantal_ronden
    st.session_state.resultaat_df = None

# Centrale startknop
if st.button("🚦 Start training voor iedereen"):
    nu = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.tijden_df['Starttijd'] = [nu]*len(namen)

# Functie om tijd te registreren
def registreer_tijd(naam):
    nu = datetime.datetime.now().strftime("%H:%M:%S")
    rij = st.session_state.tijden_df[st.session_state.tijden_df['Naam'] == naam].index[0]
    for kol in kolommen[1:]:  # sla 'Naam' over
        if pd.isna(st.session_state.tijden_df.at[rij, kol]):
            st.session_state.tijden_df.at[rij, kol] = nu
            break
