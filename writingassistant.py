import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

# -----------------------
# Load API Key from Secrets (Streamlit Cloud) or .env (local)
# -----------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found. Please set it in your environment or Streamlit Secrets.")
    st.stop()

# Initialize LLM
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4", temperature=0.7)

# -----------------------
# Prompt Template
# -----------------------

prompt_template = PromptTemplate(
    input_variables=[
        "project_title", "project_description", "project_objectives",
        "funder_mission", "funder_focus_areas", "funder_requirements"
    ],
    template="""
Write a compelling grant proposal introduction for a project titled "{project_title}". 
The project aims to {project_description}. Key objectives include: {project_objectives}. 
The funder’s mission is: {funder_mission}, with focus areas in {funder_focus_areas}. 
Proposals must meet these requirements: {funder_requirements}. 
Emphasize alignment with the funder’s goals and demonstrate measurable impact.
"""
)

# -----------------------
# Streamlit App
# -----------------------

st.set_page_config(page_title="AI Grant Writing Assistant", layout="centered")
st.title("🎯 AI Grant Proposal Assistant")
st.write("Fill out the details to generate a grant proposal introduction:")

with st.form("grant_form"):
    project_title = st.text_input("Project Title")
    project_description = st.text_area("Project Description")
    project_objectives = st.text_area("Key Objectives (comma-separated)")
    funder_mission = st.text_area("Funder’s Mission")
    funder_focus_areas = st.text_area("Funder’s Focus Areas")
    funder_requirements = st.text_area("Funder’s Requirements")

    submitted = st.form_submit_button("Generate Proposal")

if submitted:
    try:
        filled_prompt = prompt_template.format(
            project_title=project_title,
            project_description=project_description,
            project_objectives=project_objectives,
            funder_mission=funder_mission,
            funder_focus_areas=funder_focus_areas,
            funder_requirements=funder_requirements
        )

        result = llm.invoke(filled_prompt)
        st.subheader("✨ Generated Proposal")
        st.success(result)

    except Exception as e:
        st.error(f"❌ Error generating proposal: {e}")
