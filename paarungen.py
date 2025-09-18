import streamlit as st
import random

st.set_page_config(page_title="TT Training Pairing System", layout="wide")
st.title("TT Training Pairing System")

# --- State initialisieren ---
if "spieler_liste" not in st.session_state:
    st.session_state.spieler_liste = []

if "runden_historie" not in st.session_state:
    st.session_state.runden_historie = []

# --- Sidebar: Spieler hinzufügen ---
st.sidebar.header("Spieler hinzufügen / bearbeiten")
name = st.sidebar.text_input("Spielername eingeben")
kategorie = st.sidebar.selectbox("Kategorie wählen", ["C", "D", "E"])
if st.sidebar.button("Spieler hinzufügen") and name:
    st.session_state.spieler_liste.append({"name": name, "kategorie": kategorie})
    st.sidebar.success(f"Spieler {name} ({kategorie}) hinzugefügt")

# --- Beispielspieler hinzufügen ---
if st.sidebar.button("Beispielspieler erstellen"):
    beispielspieler = [
        {"name":"Tom","kategorie":"C"},
        {"name":"Mathis","kategorie":"C"},
        {"name":"Youri","kategorie":"C"},
        {"name":"Paul","kategorie":"D"},
        {"name":"Samir","kategorie":"E"},
        {"name":"Björn","kategorie":"E"},
        {"name":"Sanjay","kategorie":"D"}
    ]
    st.session_state.spieler_liste.extend(beispielspieler)
    st.sidebar.success("Beispielspieler hinzugefügt")

# --- Main: Spielerliste bearbeiten/löschen ---
st.subheader("Aktuelle Spieler")
if st.session_state.spieler_liste:
    for i, s in enumerate(st.session_state.spieler_liste):
        cols = st.columns([3,1,1])
        cols[0].write(f"{s['name']} ({s['kategorie']})")
        if cols[1].button("Bearbeiten", key=f"edit_{i}"):
            st.session_state.spieler_liste[i]["name"] = st.text_input(f"Neuer Name {i}", value=s["name"])
            st.session_state.spieler_liste[i]["kategorie"] = st.selectbox(f"Neue Kategorie {i}", ["C","D","E"], index=["C","D","E"].index(s["kategorie"]))
        if cols[2].button("Löschen", key=f"del_{i}"):
            st.session_state.spieler_liste.pop(i)
            st.experimental_rerun()
else:
    st.write("Keine Spieler hinzugefügt")

# --- Sidebar: Kategorie-Verteilung ---
st.sidebar.subheader("Kategorie-Verteilung")
verteilung = {"C":0,"D":0,"E":0}
for s in st.session_state.spieler_liste:
    verteilung[s["kategorie"]] +=1
for k,v in verteilung.items():
    st.sidebar.write(f"{k}: {v}")
st.sidebar.write(f"Gesamt: {len(st.session_state.spieler_liste)} Spieler")

# --- Paarungs Regeln ---
def erlaubt(s1, s2):
    return (s1["kategorie"], s2["kategorie"]) not in [("C","E"),("E","C")]

# --- Runde generieren ---
def generate_round(players, history):
    noch = players.copy()
    random.shuffle(noch)
    runde_result = []

    letzte_runde = history[-1] if history else []

    # Spieler, die letzte Runde ausgesetzt haben
    ausgesetzt_last = {s1["name"] for s1, s2 in letzte_runde if s2["name"]=="Aussetzen"}

    # Paare, die letzte Runde gespielt haben
    letzte_paarungen = {frozenset([s1["name"], s2["name"]]) for s1, s2 in letzte_runde if s2["name"]!="Aussetzen"}

    gerade = len(noch) % 2 == 0

    while noch:
        s1 = noch.pop(0)

        # Alle möglichen Partner noch nicht in dieser Runde
        moegliche_partner = [p for p in noch if erlaubt(s1,p)]
        # Partner nicht die letzte Runde zusammen gespielt haben
        moegliche_partner = [p for p in moegliche_partner if frozenset([s1["name"], p["name"]]) not in letzte_paarungen]

        partner = None
        if moegliche_partner:
            partner = random.choice(moegliche_partner)
        else:
            # Kein Partner ohne Wiederholung → erlaube Wiederholung nur bei gerade Zahl
            if gerade:
                fallback = [p for p in noch if erlaubt(s1,p)]
                fallback = [p for p in fallback if frozenset([s1["name"],p["name"]]) not in letzte_paarungen]
                if fallback:
                    partner = random.choice(fallback)
                elif noch:
                    partner = random.choice(noch)

        if partner:
            noch.remove(partner)
            runde_result.append((s1, partner))
        else:
            # Ungerade Spielerzahl: nur aussetzen, wenn letzte Runde nicht schon Aussetzer
            if not gerade:
                if s1["name"] in ausgesetzt_last:
                    noch.append(s1)
                    random.shuffle(noch)
                    continue
                runde_result.append((s1, {"name":"Aussetzen","kategorie":""}))

    return runde_result

# --- Anzahl Runden eingeben ---
st.subheader("Automatische Runden erstellen")
anzahl_runden = st.number_input("Anzahl Runden", min_value=1, step=1, value=1)
if st.button("Alle Runden generieren"):
    if len(st.session_state.spieler_liste)<2:
        st.warning("Mindestens 2 Spieler erforderlich")
    else:
        for _ in range(anzahl_runden):
            runde = generate_round(st.session_state.spieler_liste, st.session_state.runden_historie)
            st.session_state.runden_historie.append(runde)
        st.success(f"{anzahl_runden} Runde(n) erstellt!")

# --- Aktuelle Paarungen ---
st.subheader("Aktuelle Paarungen")
if st.session_state.runden_historie:
    for s1,s2 in st.session_state.runden_historie[-1]:
        st.write(f"{s1['name']} ({s1['kategorie']})  vs  {s2['name']} ({s2['kategorie']})")
else:
    st.write("Noch keine Runde gestartet")

# --- Paarungs-Historie ---
st.subheader("Paarungs-Historie")
if st.session_state.runden_historie:
    for i,runde in enumerate(st.session_state.runden_historie,start=1):
        st.write(f"Runde {i}")
        for s1,s2 in runde:
            st.write(f"{s1['name']} ({s1['kategorie']})  vs  {s2['name']} ({s2['kategorie']})")
else:
    st.write("Noch keine Runden gespielt")

# --- Statistiken ---
st.subheader("Statistiken")
gespielt = len(st.session_state.runden_historie)
wiederholungen = 0
ungueltige = 0
historie_sets = []

for runde in st.session_state.runden_historie:
    for s1,s2 in runde:
        if s2["name"]=="Aussetzen":
            continue
        pair = frozenset([s1["name"],s2["name"]])
        if pair in historie_sets:
            wiederholungen+=1
        historie_sets.append(pair)
        if (s1["kategorie"],s2["kategorie"]) in [("C","E"),("E","C")]:
            ungueltige+=1

st.write(f"Gespielte Runden: {gespielt}")
st.write(f"Wiederholungen: {wiederholungen}")
st.write(f"Ungültige Paarungen: {ungueltige}")
erfolg = 100 if gespielt==0 else max(0,100-int(ungueltige/gespielt*100))
st.write(f"Erfolgsquote: {erfolg}%")

