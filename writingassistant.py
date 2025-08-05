import streamlit as st
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# ----------------------------
# Load API key securely from secrets.toml
# ----------------------------
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ----------------------------
# Streamlit App UI
# ----------------------------
st.set_page_config(page_title="Grant Writing Assistant", layout="centered")
st.title("🌿 AI-Powered Grant Proposal Assistant")
st.write("Generate a compelling grant proposal introduction aligned with funder requirements.")

# ----------------------------
# Collect User Inputs
# ----------------------------
project_title = st.text_input("Project Title")
project_description = st.text_area("Brief Project Description")
project_objectives = st.text_area("Key Objectives (comma-separated)")
funder_mission = st.text_area("Funder Mission")
funder_focus_areas = st.text_area("Funder Focus Areas")
funder_requirements = st.text_area("Funder Proposal Requirements")

# ----------------------------
# LangChain Prompt Template
# ----------------------------
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

# ----------------------------
# Generate Proposal on Button Click
# ----------------------------
if st.button("Generate Proposal"):
    try:
        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4",
            temperature=0.7
        )

        prompt = grant_proposal_prompt.format(
            project_title=project_title,
            project_description=project_description,
            project_objectives=project_objectives,
            funder_mission=funder_mission,
            funder_focus_areas=funder_focus_areas,
            funder_requirements=funder_requirements,
        )

        response = llm.predict(prompt)

        st.subheader("Generated Proposal Introduction:")
        st.success(response)

    except Exception as e:
        st.error(f"Error generating proposal: {str(e)}")
