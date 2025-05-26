import streamlit as st
import json
from typing import List, Dict

# Initialzustand definieren, falls keine Sessiondaten vorhanden sind
def initialisiere_session():
    if 'spieler' not in st.session_state:
        st.session_state.spieler = []
    if 'spielverlauf' not in st.session_state:
        st.session_state.spielverlauf = []
    if 'aktuelles_spiel' not in st.session_state:
        st.session_state.aktuelles_spiel = None

# Punkte aktualisieren basierend auf Platzierung
def spiel_abschliessen():
    spiel = st.session_state.aktuelles_spiel
    if not spiel:
        return

    faktor = len(st.session_state.spieler)
    platz_map = {p['name']: p['platz'] for p in spiel['platzierung']}

    for s in st.session_state.spieler:
        einsatz = next((e['einsatz'] for e in spiel['einsaetze'] if e['name'] == s['name']), 1)
        platz = platz_map.get(s['name'], faktor)
        differenz = round((faktor - platz) * einsatz)
        s['punkte'] += differenz

    verlauf_eintrag = {
        'spiel': spiel['name'],
        'einsatz': {e['name']: e['einsatz'] for e in spiel['einsaetze']},
        'platzierung': spiel['platzierung']
    }

    st.session_state.spielverlauf.append(verlauf_eintrag)
    st.session_state.aktuelles_spiel = None

# App Start
st.title("Vatertagsspiele Punkteverwaltung")
initialisiere_session()

if not st.session_state.spieler:
    st.subheader("Spieler hinzufügen")
    name = st.text_input("Name", key="neuer_spieler")
    if st.button("Hinzufügen"):
        if name and name not in [s['name'] for s in st.session_state.spieler]:
            st.session_state.spieler.append({'name': name, 'punkte': 20, 'einsatz': 1})
            st.experimental_rerun()
    for s in st.session_state.spieler:
        st.write(s['name'])
    if st.button("Spiel starten"):
        for s in st.session_state.spieler:
            s['punkte'] = 20
            s['einsatz'] = 1
        st.experimental_rerun()
else:
    st.subheader("Spieler und Punkte")
    for s in st.session_state.spieler:
        st.write(f"{s['name']}: {s['punkte']} Punkte")

    st.subheader("Neues Spiel vorbereiten")
    spielname = st.text_input("Spielname", key="spielname")
    einsaetze = {}
    for s in st.session_state.spieler:
        einsaetze[s['name']] = st.number_input(f"{s['name']} setzt", min_value=1, max_value=3, value=s['einsatz'], key=f"einsatz_{s['name']}")

    if st.button("Spiel vorbereiten") and spielname:
        st.session_state.aktuelles_spiel = {
            'name': spielname,
            'einsaetze': [{'name': n, 'einsatz': e} for n, e in einsaetze.items()],
            'platzierung': []
        }
        st.experimental_rerun()

    if st.session_state.aktuelles_spiel:
        st.subheader(f"Platzierung: {st.session_state.aktuelles_spiel['name']}")
        platzierungen = []
        for s in st.session_state.spieler:
            platz = st.number_input(f"Platz für {s['name']}", min_value=1, max_value=len(st.session_state.spieler), key=f"platz_{s['name']}")
            platzierungen.append({'name': s['name'], 'platz': platz})
        if st.button("Spiel abschließen"):
            st.session_state.aktuelles_spiel['platzierung'] = platzierungen
            spiel_abschliessen()
            st.experimental_rerun()

    st.subheader("Spielverlauf")
    if st.session_state.spielverlauf:
        st.table([
            {
                "Spiel": e['spiel'],
                "Einsatz": ', '.join([f"{n} ({v})" for n, v in e['einsatz'].items()]),
                "Platzierung": ', '.join([f"{p['name']} ({p['platz']})" for p in e['platzierung']])
            }
            for e in st.session_state.spielverlauf
        ])

    if st.button("Zurücksetzen"):
        for key in ['spieler', 'spielverlauf', 'aktuelles_spiel']:
            st.session_state.pop(key, None)
        st.experimental_rerun()
