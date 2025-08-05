import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load .env file for local development (ignored in Streamlit Cloud)
load_dotenv()

# Safety check
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is missing. Check your .env or Streamlit secrets.")
    st.stop()

# ✅ Use from_env() to avoid ValidationError
llm = ChatOpenAI.from_env(model="gpt-4", temperature=0.7)

# Prompt definition
grant_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title", "project_description", "project_objectives",
        "funder_mission", "funder_focus_areas", "funder_requirements"
    ],
    template=(
        "Write a compelling grant proposal introduction for a project titled '{project_title}'. "
        "The project aims to {project_description}. Key objectives of the project include: {project_objectives}. "
        "The funder has the following mission: {funder_mission}, with focus areas in {funder_focus_areas}. "
        "Proposals must align with these requirements: {funder_requirements}. "
        "Ensure the introduction highlights how the project aligns with the funder's priorities and demonstrates measurable impacts."
    ),
)

# Streamlit UI
st.title("Grant Proposal Writing Assistant")
st.markdown("Fill in the details below to generate a grant proposal introduction.")

with st.form("grant_form"):
    project_title = st.text_input("Project Title", placeholder="e.g., Restoring Wetlands in Upstate NY")
    project_description = st.text_area("Project Description", placeholder="e.g., Restore 100 acres of wetlands...")
    project_objectives = st.text_area("Project Objectives (comma separated)", placeholder="e.g., Improve biodiversity, Reduce flood risk")
    funder_mission = st.text_area("Funder's Mission")
    funder_focus_areas = st.text_area("Funder's Focus Areas")
    funder_requirements = st.text_area("Funder's Requirements")
    
    submitted = st.form_submit_button("Generate Proposal")

if submitted:
    try:
        inputs = {
            "project_title": project_title,
            "project_description": project_description,
            "project_objectives": project_objectives,
            "funder_mission": funder_mission,
            "funder_focus_areas": funder_focus_areas,
            "funder_requirements": funder_requirements,
        }

        prompt = grant_proposal_prompt.format(**inputs)
        response = llm.invoke(prompt)

        st.subheader("Generated Grant Proposal Introduction:")
        st.write(response.content)

    except Exception as e:
        st.error(f"Error generating proposal: {e}")
