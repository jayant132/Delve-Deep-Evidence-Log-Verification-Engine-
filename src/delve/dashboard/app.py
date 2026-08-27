import requests
import streamlit as st

API = "http://localhost:8000"

st.title("DELVE — Incident Dashboard")

with st.form("new_incident"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    if st.form_submit_button("Create Incident") and title and description:
        r = requests.post(f"{API}/incidents", json={"title": title, "description": description})
        st.json(r.json())

st.divider()
st.subheader("All Incidents")
incidents = requests.get(f"{API}/incidents").json()
for inc in incidents:
    with st.expander(f"{inc['title']} — {inc['status']}"):
        st.json(inc)
        if st.button("Investigate", key=f"inv_{inc['id']}"):
            r = requests.post(f"{API}/incidents/{inc['id']}/investigate")
            st.json(r.json())
        actions = requests.get(f"{API}/incidents/{inc['id']}/actions").json()
        for a in actions:
            col1, col2 = st.columns([4, 1])
            col1.write(f"[{a['risk_level'].upper()}] {a['description']} — {a['status']}")
            if a["status"] == "pending_approval" and col2.button("Approve", key=f"appr_{a['id']}"):
                requests.post(f"{API}/incidents/actions/{a['id']}/approve")
                st.rerun()
