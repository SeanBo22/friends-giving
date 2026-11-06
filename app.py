from pathlib import Path

import pandas as pd
import streamlit as st

CSV_PATH = Path(__file__).parent / "friendsgiving_signups.csv"
COLUMNS = ["name", "rsvp", "bringing"]
WORKSHEET = "Friendsgiving"
LOCATION = "Location shared after RSVP"

st.set_page_config(page_title="Friendsgiving RSVP", page_icon="🦃", layout="centered")


def use_gsheets():
    """Use Google Sheets when credentials are configured; otherwise fall back to a local CSV."""
    try:
        return "gsheets" in st.secrets.get("connections", {})
    except Exception:
        return False


def get_conn():
    from streamlit_gsheets import GSheetsConnection

    return st.connection("gsheets", type=GSheetsConnection)


def clean(df):
    df = df.copy()
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS].dropna(how="all")
    return df.fillna("").astype(str).reset_index(drop=True)


def load_data():
    if use_gsheets():
        df = get_conn().read(worksheet=WORKSHEET, ttl=0)
        return clean(df)
    if CSV_PATH.exists():
        try:
            return clean(pd.read_csv(CSV_PATH))
        except pd.errors.EmptyDataError:
            pass
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df = clean(df)
    if use_gsheets():
        get_conn().update(worksheet=WORKSHEET, data=df)
    else:
        df.to_csv(CSV_PATH, index=False)


st.title("🦃 Friendsgiving RSVP")
st.subheader("November 14 • 7:00 PM")

st.markdown(
    """
    Come celebrate with good food, cozy vibes, and a little holiday cheer.
    We can’t wait to gather together.
    """
)

st.markdown("---")

col1, col2 = st.columns(2)
col1.metric("Date", "Nov 14")
col2.metric("Time", "7:00 PM")

st.markdown("---")

st.info("Fill out the form below to RSVP and tell us what you're bringing.")

with st.form("rsvp_form"):
    name = st.text_input("Your name", placeholder="Jane Doe")
    rsvp = st.selectbox("RSVP", ["Attending", "Maybe", "Can't make it"])
    bringing = st.text_input("What are you bringing?", placeholder="e.g. stuffing, dessert, drinks")
    submit = st.form_submit_button("Save my RSVP")

if submit:
    cleaned_name = name.strip()
    cleaned_bringing = bringing.strip()

    if not cleaned_name:
        st.warning("Please enter your name before submitting.")
    else:
        df = load_data()

        if df.empty:
            df = pd.DataFrame(columns=["name", "rsvp", "bringing"])

        existing = df[df["name"].str.lower() == cleaned_name.lower()]

        if not existing.empty:
            df.loc[existing.index[0], ["name", "rsvp", "bringing"]] = [
                cleaned_name,
                rsvp,
                cleaned_bringing,
            ]
            st.success(f"Thanks, {cleaned_name}! Your RSVP was updated.")
        else:
            df = pd.concat(
                [df, pd.DataFrame([{"name": cleaned_name, "rsvp": rsvp, "bringing": cleaned_bringing}])],
                ignore_index=True,
            )
            st.success(f"Thanks, {cleaned_name}! Your RSVP has been saved.")

        save_data(df)

st.markdown("---")

st.subheader("Current signups")
df = load_data()

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
    attending_count = (df["rsvp"] == "Attending").sum()
    maybe_count = (df["rsvp"] == "Maybe").sum()
    st.caption(f"Attending: {attending_count} | Maybe: {maybe_count}")
else:
    st.caption("No one has RSVP’d yet. Be the first to join us!")

st.markdown("---")

st.subheader("Need to update or remove your RSVP?")
if not df.empty:
    names = df["name"].tolist()
    selected_name = st.selectbox("Choose your name", names)
    selected = df[df["name"] == selected_name].iloc[0]

    with st.form("edit_rsvp"):
        edit_name = st.text_input("Name", value=selected["name"])
        edit_rsvp = st.selectbox(
            "RSVP",
            ["Attending", "Maybe", "Can't make it"],
            index=(
                ["Attending", "Maybe", "Can't make it"].index(selected["rsvp"])
                if selected["rsvp"] in ["Attending", "Maybe", "Can't make it"]
                else 0
            ),
        )
        edit_bringing = st.text_input("What are you bringing?", value=selected["bringing"])

        col_update, col_remove = st.columns(2)
        with col_update:
            update_button = st.form_submit_button("Update")
        with col_remove:
            remove_button = st.form_submit_button("Remove")

    if update_button:
        df.loc[df["name"] == selected_name, ["name", "rsvp", "bringing"]] = [
            edit_name.strip(),
            edit_rsvp,
            edit_bringing.strip(),
        ]
        save_data(df)
        st.success("Your RSVP has been updated.")

    if remove_button:
        df = df[df["name"] != selected_name].reset_index(drop=True)
        save_data(df)
        st.success(f"{selected_name} was removed from the RSVP list.")
else:
    st.caption("There are no RSVPs to edit yet.")
