import streamlit as st
import pandas as pd
import datetime

st.title("🏃 Tijdregistratie voetbaltraining - Versie 6")

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

# Knoppen in 2 kolommen
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

# Tabel met tijden
st.subheader("📋 Geregistreerde tijden")
st.dataframe(st.session_state.tijden_df)

# Afsluitknop
if st.button("🏁 Training afsluiten en resultaten tonen"):
    df = st.session_state.tijden_df.copy()

    def parse_time(t):
        try:
            return datetime.datetime.strptime(t, "%H:%M:%S") if pd.notna(t) else None
        except:
            return None

    df['Starttijd_dt'] = df['Starttijd'].apply(parse_time)
    df['Eindtijd_dt'] = df['Eindtijd'].apply(parse_time)
    df['Looptijd'] = df.apply(lambda row: row['Eindtijd_dt'] - row['Starttijd_dt'] if row['Starttijd_dt'] and row['Eindtijd_dt'] else None, axis=1)
    df['Looptijd_str'] = df['Looptijd'].apply(lambda x: str(x) if pd.notna(x) else "")

    # Voeg tussentijden toe als string
    df['Tussentijden'] = df[[kol for kol in kolommen if kol.startswith('Tussentijd')]].apply(
        lambda r: ", ".join([t for t in r if pd.notna(t)]), axis=1
    )

    # Maak resultaat dataframe
    resultaat_df = df[['Naam', 'Starttijd', 'Eindtijd', 'Tussentijden', 'Looptijd_str', 'Looptijd']].copy()
    resultaat_df = resultaat_df.sort_values(by='Looptijd').reset_index(drop=True)
    resultaat_df.rename(columns={'Looptijd_str': 'Looptijd'}, inplace=True)

    st.session_state.resultaat_df = resultaat_df

# Toon resultaten als ze beschikbaar zijn
if st.session_state.resultaat_df is not None:
    st.subheader("🏆 Resultaten op volgorde van looptijd")
    st.dataframe(st.session_state.resultaat_df[['Naam', 'Starttijd', 'Eindtijd', 'Tussentijden', 'Looptijd']])

    # Downloadknop
    csv = st.session_state.resultaat_df[['Naam', 'Starttijd', 'Eindtijd', 'Tussentijden', 'Looptijd']].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download resultaten als CSV", data=csv, file_name="resultaten_training.csv", mime="text/csv")
