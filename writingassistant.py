import os
import streamlit as st
import openai
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Get the OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Streamlit UI
st.set_page_config(page_title="Grant Writing Assistant", layout="wide")
st.title("AI Grant Proposal Writing Assistant")

st.markdown("Fill in the fields below and click **Generate Proposal Text** to get started.")

objective = st.text_area("Project Objective", help="Describe the primary goal of the grant project.")
audience = st.text_area("Target Audience", help="Who will benefit from this project?")
outcomes = st.text_area("Expected Outcomes", help="What are the intended outcomes or impact?")
budget = st.text_area("Budget Overview", help="Summarize the funding needs and allocations.")
timeline = st.text_area("Timeline", help="Provide a rough timeline or project phases.")

if st.button("Generate Proposal Text"):
    if not all([objective, audience, outcomes, budget, timeline]):
        st.warning("Please fill in all fields before generating proposal text.")
    else:
        with st.spinner("Generating proposal..."):
            prompt = f"""
You are an expert grant writer. Write a compelling grant proposal based on the following details:

Project Objective: {objective}
Target Audience: {audience}
Expected Outcomes: {outcomes}
Budget Overview: {budget}
Timeline: {timeline}

Please write in a professional and clear tone suitable for funding agencies.
"""

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                proposal_text = response.choices[0].message["content"]
                st.success("Proposal generated successfully!")
                st.text_area("Generated Proposal", proposal_text, height=400)
            except Exception as e:
                st.error(f"An error occurred: {e}")
