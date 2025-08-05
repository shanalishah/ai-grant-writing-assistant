# writingassistant.py

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

# --- Unified Credential Loading ---
# This block will work for both local and deployed environments.

api_key = None
project_id = None

# First, try to load from Streamlit secrets (for deployed app)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    project_id = st.secrets["OPENAI_PROJECT_ID"]
# If that fails, load from .env file (for local development)
except (KeyError, FileNotFoundError):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        project_id = os.getenv("OPENAI_PROJECT_ID")
    except ImportError:
        # This handles the case where python-dotenv is not installed
        st.error("python-dotenv is not installed. Please run 'pip install python-dotenv' for local development.")
        st.stop()


# Final check to ensure credentials are loaded
if not api_key or not project_id:
    st.error("OpenAI API key or Project ID not found. Please set them in your Streamlit secrets or a local .env file.")
    st.stop()

# --- End of Credential Loading ---


# Set up LLM, passing the Project ID as a default header
try:
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        openai_api_key=api_key,
        # This is the correct way to pass the Project ID
        default_headers={
            "OpenAI-Project": project_id
        }
    )
except Exception as e:
    st.error(f"Failed to initialize the OpenAI model. Error: {e}")
    st.stop()

# Define Prompt
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
    if not all([project_title, project_description, project_objectives, funder_mission, funder_focus_areas, funder_requirements]):
        st.warning("Please fill out all the fields in the form.")
    else:
        try:
            with st.spinner("Generating proposal..."):
                inputs = {
                    "project_title": project_title,
                    "project_description": project_description,
                    "project_objectives": project_objectives,
                    "funder_mission": funder_mission,
                    "funder_focus_areas": funder_focus_areas,
                    "funder_requirements": funder_requirements,
                }

                prompt_text = grant_proposal_prompt.format(**inputs)
                response = llm.invoke(prompt_text)

                st.subheader("Generated Grant Proposal Introduction:")
                st.write(response.content)

        except Exception as e:
            st.error(f"Error generating proposal: {e}")
