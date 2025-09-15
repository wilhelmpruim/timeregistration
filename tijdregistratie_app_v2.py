import streamlit as st
import pandas as pd
import datetime
import altair as alt

st.title("🏃 Tijdregistratie voetbaltraining - Versie 10.1")

# Invoer deelnemers
namen_input = st.text_area("Voer namen in (één per regel):", """Kind 1
Kind 2
Kind 3
Kind 4
Kind 5
Kind 6""")
namen = [naam.strip() for naam in namen_input.split("\n") if naam.strip()]

# Invoer aantal ronden
aantal_ronden = st.number_input("Aantal ronden", min_value=1, max_value=10, value=2, step=1)

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

    tijd_kolommen = [kol for kol in kolommen if kol != 'Naam']
    for kol in tijd_kolommen:
        df[kol + '_dt'] = df[kol].apply(parse_time)

    df['Looptijd_td'] = df.apply(lambda row: row['Eindtijd_dt'] - row['Starttijd_dt'] if row['Starttijd_dt'] and row['Eindtijd_dt'] else None, axis=1)
    df['Looptijd'] = df['Looptijd_td'].apply(lambda x: str(x).replace("0 days ", "") if pd.notna(x) else "")

    def bereken_rondes(row):
        tijden = [row['Starttijd_dt']]
        for i in range(1, aantal_ronden):
            tijden.append(row.get(f'Tussentijd {i}_dt'))
        tijden.append(row['Eindtijd_dt'])
        rondes = []
        for i in range(1, len(tijden)):
            if tijden[i] and tijden[i-1]:
                verschil = tijden[i] - tijden[i-1]
                rondes.append(str(verschil).replace("0 days ", ""))
            else:
                rondes.append("n.v.t.")
        return ", ".join(rondes)

    df['Rondetijden'] = df.apply(bereken_rondes, axis=1)

    df['Tussentijden'] = df[[kol for kol in kolommen if kol.startswith('Tussentijd')]].apply(
        lambda r: ", ".join([t for t in r if pd.notna(t)]), axis=1
    )

    resultaat_df = df[['Naam', 'Looptijd', 'Rondetijden', 'Starttijd', 'Eindtijd', 'Tussentijden', 'Looptijd_td']].copy()
    resultaat_df = resultaat_df.sort_values(by='Looptijd_td').reset_index(drop=True)
    resultaat_df.drop(columns=['Looptijd_td'], inplace=True)

    st.session_state.resultaat_df = resultaat_df

# Toon resultaten als ze beschikbaar zijn
if st.session_state.resultaat_df is not None:
    st.subheader("🏆 Resultaten op volgorde van looptijd")
    st.dataframe(st.session_state.resultaat_df)

    # 📥 CSV export
    csv = st.session_state.resultaat_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download resultaten als CSV", data=csv, file_name="resultaten_training.csv", mime="text/csv")

    # 📈 Altair-grafiek onder de resultaten
    st.subheader("📈 Voortgang per deelnemer")

    records = []
    for _, row in df.iterrows():
        tijden = [row['Starttijd_dt']]
        for i in range(1, aantal_ronden):
            tijden.append(row.get(f'Tussentijd {i}_dt'))
        tijden.append(row['Eindtijd_dt'])
        for i, tijd in enumerate(tijden):
            if tijd:
                records.append({
                    'Naam': row['Naam'],
                    'Ronde': f'Ronde {i+1}',
                    'Tijdstip': tijd
                })

    df_lijn = pd.DataFrame(records)

chart = alt.Chart(df_lijn).mark_line(point=True).encode(
    y='Tijdstip:T',
    x='Ronde:O',
    color='Naam:N'
).properties(
    title='Voortgang per deelnemer (tijd verticaal)',
    height=400
)

st.altair_chart(chart, use_container_width=True)

