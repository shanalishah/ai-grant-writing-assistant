import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load from .env for local development (has no effect on Streamlit Cloud)
load_dotenv()

# Streamlit UI
st.set_page_config(page_title="Grant Writing Assistant", layout="wide")
st.title("🤖 AI Grant Proposal Assistant")

st.markdown("This assistant helps generate grant proposal text from your inputs.")

# Input fields
objective = st.text_area("Project Objective", placeholder="Describe the core objective of the project")
audience = st.text_area("Target Audience", placeholder="Who will benefit from this project?")
outcomes = st.text_area("Expected Outcomes", placeholder="What results do you anticipate?")
budget = st.text_area("Budget Overview", placeholder="Brief overview of budget")
timeline = st.text_area("Project Timeline", placeholder="Milestones, duration, phases")

# Generate prompt
template = """
You are a grant writing assistant. Based on the following inputs, generate a well-written paragraph suitable for a grant proposal:

Objective: {objective}
Target Audience: {audience}
Expected Outcomes: {outcomes}
Budget: {budget}
Timeline: {timeline}

Write in a formal, clear, and persuasive tone.
"""

prompt = PromptTemplate(
    input_variables=["objective", "audience", "outcomes", "budget", "timeline"],
    template=template,
)

# Initialize ChatOpenAI (uses OPENAI_API_KEY from environment/secrets automatically)
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

if st.button("Generate Proposal Text"):
    if not all([objective, audience, outcomes, budget, timeline]):
        st.warning("Please fill in all fields before generating.")
    else:
        with st.spinner("Generating proposal..."):
            chain = prompt | llm
            response = chain.invoke({
                "objective": objective,
                "audience": audience,
                "outcomes": outcomes,
                "budget": budget,
                "timeline": timeline
            })
            st.success("Generated Proposal Text:")
            st.text_area("Proposal Output", value=response.content, height=300)
