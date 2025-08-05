import streamlit as st
from openai import OpenAI
import os

# Setup client using OpenAI v1+ SDK (secure, cloud-ready)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.set_page_config(page_title="Grant Proposal Assistant", layout="centered")
st.title("🎯 AI Grant Proposal Assistant")

# Input fields
objective = st.text_input("🎯 Project Objective")
audience = st.text_input("👥 Target Audience")
outcomes = st.text_area("📈 Expected Outcomes")
budget = st.text_area("💵 Budget Details")
timeline = st.text_area("⏳ Project Timeline")

if st.button("Generate Proposal Text"):
    if not all([objective, audience, outcomes, budget, timeline]):
        st.warning("Please fill in all fields.")
    else:
        with st.spinner("Generating proposal..."):
            prompt = f"""
You are a grant proposal writing assistant. Given the following details, draft a concise and persuasive grant proposal:

Objective: {objective}
Target Audience: {audience}
Expected Outcomes: {outcomes}
Budget: {budget}
Timeline: {timeline}

Write in a professional and persuasive tone.
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                proposal = response.choices[0].message.content
                st.subheader("📝 Generated Grant Proposal")
                st.write(proposal)

            except Exception as e:
                st.error(f"An error occurred: {e}")
