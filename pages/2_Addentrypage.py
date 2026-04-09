import streamlit as st
import psycopg2

st.set_page_config(page_title="Add Entry", page_icon="➕")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL2"])

st.title("➕ Add Food Entry")

conn = get_connection()
cur = conn.cursor()

# Dropdown data
cur.execute("SELECT id, name FROM locations ORDER BY name;")
locations = {row[1]: row[0] for row in cur.fetchall()}

cur.execute("SELECT id, name FROM food_items ORDER BY name;")
items = {row[1]: row[0] for row in cur.fetchall()}

conn.close()

with st.form("add_form"):
    date = st.date_input("Date")
    location = st.selectbox("Location", list(locations.keys()))
    item = st.selectbox("Item", list(items.keys()))
    quantity = st.number_input("Quantity", min_value=0.1, step=0.5)
    notes = st.text_area("Notes")

    submit = st.form_submit_button("Add Entry")

    if submit:
        conn = get_connection()
        cur = conn.cursor()

        # Insert parent
        cur.execute("""
            INSERT INTO food_entries (entry_date, location_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (date, locations[location], notes))

        entry_id = cur.fetchone()[0]

        # Insert child
        cur.execute("""
            INSERT INTO entry_items (entry_id, food_item_id, quantity)
            VALUES (%s, %s, %s);
        """, (entry_id, items[item], quantity))

        conn.commit()
        conn.close()

        st.success("✅ Entry added!")
