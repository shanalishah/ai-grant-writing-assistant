import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables (local only)
load_dotenv()

# Get OpenAI key from environment (or Streamlit Cloud secrets)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ✅ Initialize ChatOpenAI the correct way (NO client param)
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

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
            You are an expert grant writer. Based on the details provided below, write a compelling grant proposal draft.

            Project Objective: {objective}
            Target Audience: {audience}
            Expected Outcomes: {outcomes}
            Budget Overview: {budget}
            Timeline: {timeline}

            Please write a professional, clear, and concise grant proposal draft.
            """
            try:
                response = llm.invoke(prompt)
                st.success("Proposal generated successfully!")
                st.text_area("Generated Proposal", response.content, height=400)
            except Exception as e:
                st.error(f"An error occurred: {e}")
