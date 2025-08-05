import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# -----------------------
# Load API Key from .env (for local testing)
# -----------------------
load_dotenv()  # Only needed if running locally with a .env file

# -----------------------
# Streamlit Page Config
# -----------------------
st.set_page_config(page_title="AI Grant Proposal Assistant", layout="centered")
st.title("📝 AI-Powered Grant Proposal Writing Assistant")
st.markdown("Fill in the details below to generate a professional proposal introduction:")

# -----------------------
# Grant Proposal Prompt Template
# -----------------------
grant_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title", "project_description", "project_objectives",
        "funder_mission", "funder_focus_areas", "funder_requirements"
    ],
    template=(
        "Write a compelling grant proposal introduction for a project titled '{project_title}'. "
        "The project aims to {project_description}. Key objectives include: {project_objectives}. "
        "The funder’s mission is: {funder_mission}, with focus areas in {funder_focus_areas}. "
        "Proposals must meet these requirements: {funder_requirements}. "
        "Ensure the introduction emphasizes alignment with the funder’s goals and demonstrates measurable impact."
    ),
)

# -----------------------
# Load LLM (from env or Streamlit secrets)
# -----------------------
try:
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7
    )
except Exception as e:
    st.error(f"Error initializing LLM: {e}")
    st.stop()

# -----------------------
# Streamlit Form
# -----------------------
with st.form("proposal_form"):
    project_title = st.text_input("Project Title")
    project_description = st.text_area("Brief Project Description")
    project_objectives = st.text_area("Key Objectives (comma-separated)")
    funder_mission = st.text_area("Funder’s Mission")
    funder_focus_areas = st.text_area("Funder’s Focus Areas")
    funder_requirements = st.text_area("Funder’s Requirements")
    submitted = st.form_submit_button("Generate Proposal")

# -----------------------
# On Submit
# -----------------------
if submitted:
    try:
        prompt = grant_proposal_prompt.format(
            project_title=project_title,
            project_description=project_description,
            project_objectives=project_objectives,
            funder_mission=funder_mission,
            funder_focus_areas=funder_focus_areas,
            funder_requirements=funder_requirements
        )

        response = llm.invoke(prompt)
        st.subheader("✅ Generated Proposal Introduction")
        st.success(response)

    except Exception as e:
        st.error(f"❌ Error generating proposal: {e}")
