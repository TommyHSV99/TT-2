import streamlit as st
import random
from collections import defaultdict

st.set_page_config(page_title="TT Training Pairing System", layout="wide")
st.title("TT Training Pairing System")

# --- Spieler-Datenbank (alphabetisch, groß) ---
spieler_db = sorted([
    {"name":"AIGA LIN","kategorie":"E"},
    {"name":"BENOIT","kategorie":"C"},
    {"name":"BJÖRN","kategorie":"E"},
    {"name":"BRUNO","kategorie":"D"},
    {"name":"DEAN","kategorie":"E"},
    {"name":"DANIEL","kategorie":"E"},
    {"name":"DANY","kategorie":"C"},
    {"name":"DIERK","kategorie":"C"},
    {"name":"DIDIER","kategorie":"C"},
    {"name":"DOMINIK","kategorie":"C"},
    {"name":"EMELY","kategorie":"E"},
    {"name":"ERIC","kategorie":"D"},
    {"name":"EYOB","kategorie":"E"},
    {"name":"FELIX","kategorie":"E"},
    {"name":"GABRIEL","kategorie":"E"},
    {"name":"GIADA","kategorie":"E"},
    {"name":"HENRI","kategorie":"D"},
    {"name":"JOCELYNE","kategorie":"E"},
    {"name":"JOCHEN","kategorie":"E"},
    {"name":"JAN","kategorie":"E"},
    {"name":"JULIAN","kategorie":"E"},
    {"name":"JULIEN RENERKEN","kategorie":"D"},
    {"name":"JULIEN RAXHON","kategorie":"E"},
    {"name":"KEVIN","kategorie":"C"},
    {"name":"LIAM","kategorie":"E"},
    {"name":"LEONARD","kategorie":"E"},
    {"name":"LENNY","kategorie":"C"},
    {"name":"LUCA FELDEISEN","kategorie":"C"},
    {"name":"LUCA BECKERS","kategorie":"E"},
    {"name":"MAURICE","kategorie":"E"},
    {"name":"MARC","kategorie":"E"},
    {"name":"MARCO","kategorie":"D"},
    {"name":"MARTIN","kategorie":"E"},
    {"name":"MATHIS","kategorie":"C"},
    {"name":"MARIJAN","kategorie":"E"},
    {"name":"MORITZ","kategorie":"C"},
    {"name":"NILS","kategorie":"C"},
    {"name":"NIKLAS","kategorie":"C"},
    {"name":"PAUL","kategorie":"D"},
    {"name":"PATRICK","kategorie":"D"},
    {"name":"SANJAY","kategorie":"D"},
    {"name":"SEMIR","kategorie":"E"},
    {"name":"STEPHAN","kategorie":"C"},
    {"name":"TIMO","kategorie":"D"},
    {"name":"TOM LENAERTS","kategorie":"C"},
    {"name":"TOM LAMBIET","kategorie":"C"},
    {"name":"WIDIYA","kategorie":"D"},
    {"name":"YOURI","kategorie":"C"},
    {"name":"YANIS","kategorie":"E"}
], key=lambda x: x["name"])

# --- Session State ---
if "runden_historie" not in st.session_state:
    st.session_state.runden_historie = []

# --- Sidebar: Spieler-Auswahl ---
st.sidebar.header("Spieler auswählen (max. 20)")

alle_spieler = [s["name"] for s in spieler_db]
auswahl = st.sidebar.multiselect(
    "Spieler auswählen",
    options=alle_spieler,
    default=[],
    max_selections=20
)

# Spieler-Liste für diese Session
spieler_liste = [s for s in spieler_db if s["name"] in auswahl]

# --- Ausgewählte Spieler nach Kategorie gruppiert anzeigen ---
st.subheader(f"Aktuell ausgewählte Spieler ({len(spieler_liste)})")
if spieler_liste:
    gruppiert = defaultdict(list)
    for s in spieler_liste:
        gruppiert[s["kategorie"]].append(s["name"])
    
    for kategorie in ["C","D","E"]:
        if gruppiert[kategorie]:
            st.markdown(f"**Kategorie {kategorie}:** " + ", ".join(sorted(gruppiert[kategorie])))
else:
    st.write("Noch keine Spieler ausgewählt.")

# --- Anzahl Runden ---
anzahl_runden = st.sidebar.number_input("Anzahl Runden", min_value=1, max_value=10, value=1)

# --- Paarungs-Regel ---
def erlaubt(s1, s2):
    return not ((s1["kategorie"]=="C" and s2["kategorie"]=="E") or (s1["kategorie"]=="E" and s2["kategorie"]=="C"))

# --- Runde generieren ---
def generate_round(players, history):
    noch = players.copy()
    random.shuffle(noch)
    runde_result = []

    letzte_runde = history[-1] if history else []
    letzte_paarungen = {frozenset([s1["name"],s2["name"]]) for s1,s2 in letzte_runde if s2["name"]!="Aussetzen"}

    while noch:
        s1 = noch.pop(0)
        moegliche_partner = [p for p in noch if erlaubt(s1,p) and frozenset([s1["name"],p["name"]]) not in letzte_paarungen]

        if moegliche_partner:
            partner = random.choice(moegliche_partner)
            noch.remove(partner)
            runde_result.append((s1, partner))
        else:
            runde_result.append((s1, {"name":"Aussetzen","kategorie":""}))
    return runde_result

# --- Button: Runden generieren ---
if st.button("Runden generieren"):
    if len(spieler_liste) < 2:
        st.warning("Mindestens 2 Spieler erforderlich")
    else:
        st.session_state.runden_historie = []
        for _ in range(anzahl_runden):
            runde = generate_round(spieler_liste, st.session_state.runden_historie)
            st.session_state.runden_historie.append(runde)
        st.success(f"{anzahl_runden} Runde(n) erstellt!")

# --- Alle Runden anzeigen ---
if st.session_state.runden_historie:
    st.subheader("Alle Paarungen")
    for r, runde in enumerate(st.session_state.runden_historie, start=1):
        st.markdown(f"### Runde {r}")
        for i, (s1,s2) in enumerate(runde, start=1):
            st.write(f"{i}. {s1['name']} – {s2['name']}")

