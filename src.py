import streamlit as st
import pandas as pd
import re
from typing import *

st.set_page_config(page_title="Wordle Solver", page_icon="assets/osaker.png", layout="centered")

# Costum CSS to make it better
st.markdown("""
    <style>
    /* Make inputs look like Wordle tiles */
    div[data-testid="stTextInput"] input {
        background-color: #787c7e; /* Wordle inactive grey */
        color: white;             /* White text */
        text-align: center;
        font-weight: 800;
        font-size: 24px;
        text-transform: uppercase;
        border-radius: 5px;
        border: 2px solid #d3d6da;
    }
    
    /* Highlighting the active box */
    div[data-testid="stTextInput"] input:focus {
        border-color: #878a8c;
        background-color: #555;
    }

    /* Center columns*/
    div[data-testid="column"] {
        text-align: center;
    }
                     
    /* Custom Header for alignment purposes*/
    .green-header { color: #6aaa64; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .yellow-header { color: #c9b458; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .grey-header { color: #787c7e; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_words(loadtype: Literal["all", "common"]):
    '''
    This does what the name suggests, lol.

    Perhaps i'll add more dictionaries later on.
    '''
    try:
        filename = "dict/5_ALL.csv" if loadtype == "All Words" else "dict/5_common.csv"
        df = pd.read_csv(filename, header=None)
        return [str(x).lower() for x in df.iloc[:, 0].tolist()]
    except Exception as e:
        return []

def clear_form():
   '''
   Clears all input boxes
   '''
   keys = ["g0", "g1", "g2", "g3", "g4", "yellow", "grey"]
   for k in keys:
       if k in st.session_state:
           st.session_state[k] = ""

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Dictionary", ["Common Words", "All Words"])    # If changed will reload the word list
    st.caption("**Note:** These dictionaries are strictly limited to 5-letter words.")
    st.divider()
    st.button("Reset", type="primary", on_click=clear_form)

word_list = load_words(mode)


st.title("🫃 Wordle solver")
st.markdown("helps you find possible words based on your past guesses. (Imagine cheating, duh. Pathetic.)")

# Correct pos
st.markdown('<p class="green-header">🟩 Correct</p>', unsafe_allow_html=True)

cols = st.columns(5)
green_inputs = []

for i, col in enumerate(cols):
    with col:
        val = st.text_input(
            "_", 
            max_chars=1, 
            key=f"g{i}", 
            label_visibility="collapsed"
        ).lower()
        green_inputs.append(val if val else ".")

# Filters for yellow and grey inputs
st.write("")
col_y, col_b = st.columns(2)

# Yellow
with col_y:
    st.markdown('<p class="yellow-header">🟨 Correct but wrong spot</p>', unsafe_allow_html=True)
    possible_input = st.text_input(
        "Yellow Label", 
        key="yellow",
        label_visibility="collapsed",
        placeholder="Included letters"
    ).lower()

# Grey
with col_b:
    st.markdown('<p class="grey-header">⬛ Excluded</p>', unsafe_allow_html=True)
    blacklisted_input = st.text_input(
        "Grey Label", 
        key="grey",
        label_visibility="collapsed",
        placeholder="Excluded letters"
    ).lower()


# If only one word is found, show victory popup
@st.dialog("CONGRATS YOU FOUND IT!")
def show_victory_popup(answer):
    '''
    Sata andagii!
    '''
    # Show answer
    st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 18px; margin-bottom: 5px;">The answer is indeed:</p>
            <div style="
                background-color: #6aaa64; 
                color: white; 
                padding: 15px; 
                border-radius: 10px; 
                font-size: 40px; 
                font-weight: 800; 
                letter-spacing: 2px;
                margin-bottom: 15px;
                text-transform: uppercase;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            ">
                {answer}
            </div>
            <p style="font-style: italic; color: #555;">Sata Andagi!</p>
    </div>
    ''', unsafe_allow_html=True)
    
    try:
        st.video("assets/osaker.mp4", autoplay=True)
    except Exception:
        st.error("Could not find osaker.mp4, no sata andagi for you :(")

    st.write("") # Spacing
    # Play Again Button
    if st.button("Play Again", type="primary", use_container_width=True):
        clear_form()
        st.rerun()

# Main Logic
if word_list:
    # Filter the word list based on inputs
    # Green Filter
    search_pattern = "".join(green_inputs)
    regex_pattern = f"^{search_pattern}$"
    filtered = [w for w in word_list if re.match(regex_pattern, w)]

    # Grey Filter
    if blacklisted_input:
        filtered = [w for w in filtered if not any(c in w for c in blacklisted_input)]

    # Yellow Filter
    if possible_input:
        filtered = [w for w in filtered if all(c in w for c in possible_input)]

    # Display Results 
    st.divider()
    count = len(filtered)
    
    if count == 0:
        st.error("No words found.")
    elif count == 1:
        # st.success(f"Solution: **{filtered[0].upper()}**")
        show_victory_popup(filtered[0].upper())
    else:
        st.subheader(f"Possible Words: {count}")
        if count <= 60:
            st.markdown(" ".join([f"`{w.upper()}`" for w in filtered]))
        else:
            df_res = pd.DataFrame(filtered, columns=["Matches"])
            df_res["Matches"] = df_res["Matches"].str.upper()
            st.dataframe(df_res, use_container_width=True, height=300, hide_index=True)