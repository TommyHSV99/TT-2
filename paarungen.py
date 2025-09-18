import streamlit as st
import random
from collections import defaultdict

st.set_page_config(page_title="TTC ASTORIA KELMIS", layout="wide")
st.title("TTC ASTORIA KELMIS")
st.markdown("### AUSWAHL PAARUNGEN TRAINING")

# --- Spieler-Datenbank im Cache ---
@st.cache_data
def get_spieler_db():
    return sorted([
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
        {"name":"SAMIR","kategorie":"E"},
        {"name":"SEMIR","kategorie":"E"},
        {"name":"STEPHAN","kategorie":"C"},
        {"name":"TIMO","kategorie":"D"},
        {"name":"TOM LENAERTS","kategorie":"C"},
        {"name":"TOM LAMBIET","kategorie":"C"},
        {"name":"WIDIYA","kategorie":"D"},
        {"name":"YOURI","kategorie":"C"},
        {"name":"YANIS","kategorie":"E"}
    ], key=lambda x: x["name"])

spieler_db = get_spieler_db()

# --- Session State ---
if "runden_historie" not in st.session_state:
    st.session_state.runden_historie = []
if "aussetzen_counter" not in st.session_state:
    st.session_state.aussetzen_counter = defaultdict(int)
if "runde_index" not in st.session_state:
    st.session_state.runde_index = 0  # Start bei 0

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
def generate_round(players, history, aussetzen_counter):
    noch = players.copy()
    random.shuffle(noch)
    runde_result = []

    letzte_runde = history[-1] if history else []
    letzte_paarungen = {frozenset([s1["name"], s2["name"]]) for s1, s2 in letzte_runde if s2["name"] != "Aussetzen"}

    while noch:
        s1 = noch.pop(0)
        moegliche_partner = [p for p in noch if p["kategorie"] == s1["kategorie"] 
                             and erlaubt(s1, p) 
                             and frozenset([s1["name"], p["name"]]) not in letzte_paarungen]
        if not moegliche_partner:
            moegliche_partner = [p for p in noch if erlaubt(s1, p) 
                                 and frozenset([s1["name"], p["name"]]) not in letzte_paarungen]
        if moegliche_partner:
            partner = random.choice(moegliche_partner)
            noch.remove(partner)
            runde_result.append((s1, partner))
        else:
            if aussetzen_counter[s1["name"]] < 1:
                runde_result.append((s1, {"name": "Aussetzen", "kategorie": ""}))
                aussetzen_counter[s1["name"]] += 1
            else:
                runde_result.append((s1, {"name": "Keine Paarung möglich", "kategorie": ""}))
    return runde_result

# --- ALLE Runden generieren im Cache ---
@st.cache_data
def generate_all_rounds(spieler_liste, anzahl_runden):
    history = []
    aussetzen_counter = defaultdict(int)
    for _ in range(anzahl_runden):
        runde = generate_round(spieler_liste, history, aussetzen_counter)
        history.append(runde)
    return history

# --- Button: Runden generieren ---
if st.button("Runden generieren"):
    if len(spieler_liste) < 2:
        st.warning("Mindestens 2 Spieler erforderlich")
    else:
        st.session_state.runden_historie = generate_all_rounds(spieler_liste, anzahl_runden)
        st.session_state.runde_index = 0
        st.success(f"{anzahl_runden} Runde(n) erstellt!")

# --- Anzeige mit Pfeil-Navigation ---
if st.session_state.runden_historie:
    max_runden = len(st.session_state.runden_historie)

    col1, col2, col3 = st.columns([1,3,1])
    with col1:
        if st.button("⬅️", disabled=st.session_state.runde_index == 0):
            st.session_state.runde_index = max(0, st.session_state.runde_index - 1)
    with col3:
        if st.button("➡️", disabled=st.session_state.runde_index == max_runden-1):
            st.session_state.runde_index = min(max_runden-1, st.session_state.runde_index + 1)

    runde = st.session_state.runden_historie[st.session_state.runde_index]
    st.subheader(f"Runde {st.session_state.runde_index + 1} von {max_runden}")
    for i, (s1, s2) in enumerate(runde, start=1):
        st.write(f"{i}. {s1['name']} – {s2['name']}")
