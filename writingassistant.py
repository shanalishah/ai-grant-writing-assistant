import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# -------------------------
# Page config
st.set_page_config(page_title="AI-Powered Grant Proposal Assistant", page_icon="🌿")

# -------------------------
# Header
st.title("🌿 AI-Powered Grant Proposal Assistant")
st.write("Generate a compelling grant proposal introduction aligned with funder requirements.")

# -------------------------
# Load API Key from Streamlit secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# -------------------------
# Set up LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
)

# -------------------------
# Define prompt template
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

# -------------------------
# User input form
with st.form("grant_form"):
    project_title = st.text_input("Project Title")
    project_description = st.text_area("Brief Project Description")
    project_objectives = st.text_area("Key Objectives (comma-separated)")
    funder_mission = st.text_area("Funder Mission")
    funder_focus_areas = st.text_area("Funder Focus Areas")
    funder_requirements = st.text_area("Funder Proposal Requirements")

    submit = st.form_submit_button("Generate Proposal")

# -------------------------
# Handle form submission
if submit:
    with st.spinner("Generating proposal..."):
        try:
            inputs = {
                "project_title": project_title,
                "project_description": project_description,
                "project_objectives": project_objectives,
                "funder_mission": funder_mission,
                "funder_focus_areas": funder_focus_areas,
                "funder_requirements": funder_requirements
            }

            formatted_prompt = grant_proposal_prompt.format(**inputs)
            response = llm.invoke(formatted_prompt)

            st.subheader("📄 Generated Grant Proposal Introduction")
            st.write(response.content)

        except Exception as e:
            st.error(f"Error generating proposal: {e}")
