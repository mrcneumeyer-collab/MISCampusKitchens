import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(
    page_title="Food Entry Database App",
    page_icon="🍽️",
    layout="wide"
)

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL2"])

st.title("🍽️ Food Entry Database App")
st.write("Welcome! Use the sidebar to view, add, edit, or delete food entries.")

st.markdown("---")
st.subheader("📊 Current Data Summary")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM food_entries;")
    total_entries = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM locations;")
    total_locations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM food_items;")
    total_items = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM entry_items;")
    total_quantity = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Entries", total_entries)
    col2.metric("Locations", total_locations)
    col3.metric("Unique Items", total_items)
    col4.metric("Total Quantity", total_quantity)

    st.markdown("---")
    st.subheader("🔍 Filter Food Entries")

    # Filters
    cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM entry_date)::INT FROM food_entries ORDER BY 1;")
    years = ["All"] + [str(row[0]) for row in cur.fetchall()]

    cur.execute("SELECT name FROM locations ORDER BY name;")
    locations = ["All"] + [row[0] for row in cur.fetchall()]

    col1, col2 = st.columns(2)
    selected_year = col1.selectbox("Filter by Year", years)
    selected_location = col2.selectbox("Filter by Location", locations)

    query = """
        SELECT fe.id, fe.entry_date, l.name, fi.name, ei.quantity, fe.notes
        FROM food_entries fe
        JOIN locations l ON fe.location_id = l.id
        JOIN entry_items ei ON fe.id = ei.entry_id
        JOIN food_items fi ON ei.food_item_id = fi.id
        WHERE 1=1
    """
    params = []

    if selected_year != "All":
        query += " AND EXTRACT(YEAR FROM fe.entry_date) = %s"
        params.append(int(selected_year))

    if selected_location != "All":
        query += " AND l.name = %s"
        params.append(selected_location)

    query += " ORDER BY fe.entry_date DESC;"

    df = pd.read_sql(query, conn, params=params)

    st.markdown("---")
    st.subheader("📈 Filtered Data Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Entries", df["id"].nunique() if not df.empty else 0)
    col2.metric("Unique Items", df["name"].nunique() if not df.empty else 0)
    col3.metric("Total Quantity", df["quantity"].sum() if not df.empty else 0)

    st.markdown("---")
    st.subheader("📋 Records")

    if df.empty:
        st.info("No records found.")
    else:
        st.dataframe(df, use_container_width=True)

    conn.close()

except Exception as e:
    st.error(f"Error: {e}")
