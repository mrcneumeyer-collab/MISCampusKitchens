import streamlit as st
import psycopg2

st.set_page_config(page_title="Delete Entry", page_icon="🗑️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🗑️ Delete Entry")

conn = get_connection()
cur = conn.cursor()

cur.execute("""
SELECT ei.id, fe.id, fe.entry_date, l.name, fi.name, ei.quantity
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

confirm = st.checkbox("Confirm deletion")

if st.button("Delete"):
    if confirm:
        cur.execute("DELETE FROM entry_items WHERE id=%s;", (entry_item_id,))

        cur.execute("SELECT COUNT(*) FROM entry_items WHERE entry_id=%s;", (entry_id,))
        if cur.fetchone()[0] == 0:
            cur.execute("DELETE FROM food_entries WHERE id=%s;", (entry_id,))

        conn.commit()
        conn.close()

        st.success("✅ Deleted!")
    else:
        st.error("Please confirm first.")