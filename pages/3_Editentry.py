import streamlit as st
import psycopg2

st.set_page_config(page_title="Edit Entry", page_icon="✏️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL2"])

st.title("✏️ Edit Entry")

conn = get_connection()
cur = conn.cursor()

cur.execute("""
SELECT ei.id, fe.id, fe.entry_date, l.name, fi.name, ei.quantity, fe.notes
FROM entry_items ei
JOIN food_entries fe ON ei.entry_id = fe.id
JOIN locations l ON fe.location_id = l.id
JOIN food_items fi ON ei.food_item_id = fi.id
ORDER BY fe.entry_date DESC;
""")

rows = cur.fetchall()

options = {
    f"{r[2]} | {r[3]} | {r[4]} | {r[5]}": r
    for r in rows
}

choice = st.selectbox("Select Entry", list(options.keys()))
record = options[choice]

entry_item_id = record[0]
entry_id = record[1]

# Dropdowns
cur.execute("SELECT id, name FROM locations;")
locations = {row[1]: row[0] for row in cur.fetchall()}

cur.execute("SELECT id, name FROM food_items;")
items = {row[1]: row[0] for row in cur.fetchall()}

conn.close()

with st.form("edit_form"):
    date = st.date_input("Date", value=record[2])
    location = st.selectbox("Location", list(locations.keys()), index=list(locations.keys()).index(record[3]))
    item = st.selectbox("Item", list(items.keys()), index=list(items.keys()).index(record[4]))
    quantity = st.number_input("Quantity", value=float(record[5]), min_value=0.1)
    notes = st.text_area("Notes", value=record[6] if record[6] else "")

    submit = st.form_submit_button("Update")

    if submit:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        UPDATE food_entries
        SET entry_date=%s, location_id=%s, notes=%s
        WHERE id=%s;
        """, (date, locations[location], notes, entry_id))

        cur.execute("""
        UPDATE entry_items
        SET food_item_id=%s, quantity=%s
        WHERE id=%s;
        """, (items[item], quantity, entry_item_id))

        conn.commit()
        conn.close()

        st.success("✅ Updated!")
