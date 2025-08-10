# writingassistant.py

import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# ========= Credentials =========
api_key = None
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    except Exception:
        pass

if not api_key:
    st.error("OpenAI API key not found. Add it to Streamlit secrets or your local .env.")
    st.stop()

# ========= Model =========
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key=api_key,
)

# ========= Prompt (Email-style full proposal) =========
email_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title",
        "project_description",
        "project_objectives",
        "funder_mission",
        "funder_focus_areas",
        "funder_requirements",
        "target_audience"
    ],
    template=(
        "You are an experienced grant writer. Using ONLY the inputs below, draft a **full, email-style grant proposal** "
        "written as 3–6 cohesive paragraphs (no headings, no bullet lists). Do **not** include a greeting or a sign-off. "
        "If a detail is missing, write 'TBD' rather than inventing facts. Keep the tone professional, persuasive, and concise. "
        "Aim for 500–900 words. Avoid placeholders like [Funder Name] or [Your Title].\n\n"
        "Inputs:\n"
        "- Project Title: {project_title}\n"
        "- Project Description: {project_description}\n"
        "- Key Objectives: {project_objectives}\n"
        "- Funder Mission: {funder_mission}\n"
        "- Funder Focus Areas: {funder_focus_areas}\n"
        "- Funder Requirements: {funder_requirements}\n"
        "- Target Audience/Beneficiaries: {target_audience}\n\n"
        "Output:\n"
        "A polished, multi-paragraph email-style proposal body (no salutation, no signature), grounded only in the inputs."
    ),
)

# ========= UI =========
st.set_page_config(page_title="AI-Powered Grant Writing Assistant", layout="centered")

st.title("AI-Powered Grant Writing Assistant")
st.caption("Provide the essential details and the assistant will generate a proposal based on your inputs.")

with st.form("proposal_form"):
    project_title = st.text_input(
        "Project Title",
        placeholder="Restoring Wetlands in Upstate NY"
    )
    project_description = st.text_area(
        "Project Description",
        placeholder="Restore 100 acres of degraded wetlands to improve flood control and biodiversity."
    )
    project_objectives = st.text_area(
        "Key Objectives (comma-separated)",
        placeholder="Increase native species richness by 20%; Reduce peak runoff by 12% within 12 months"
    )
    funder_mission = st.text_area(
        "Funder Mission",
        placeholder="Advance climate resilience and ecological restoration."
    )
    funder_focus_areas = st.text_area(
        "Funder Focus Areas",
        placeholder="Water resources; biodiversity; resilient infrastructure"
    )
    funder_requirements = st.text_area(
        "Funder Requirements",
        placeholder="Evidence-based outcomes; community engagement; budget justification"
    )
    target_audience = st.text_area(
        "Target Audience / Beneficiaries (optional)",
        placeholder="Communities in flood-prone watersheds; local conservation partners"
    )

    submitted = st.form_submit_button("Generate Proposal")

fields = {
    "project_title": (project_title or "").strip(),
    "project_description": (project_description or "").strip(),
    "project_objectives": (project_objectives or "").strip(),
    "funder_mission": (funder_mission or "").strip(),
    "funder_focus_areas": (funder_focus_areas or "").strip(),
    "funder_requirements": (funder_requirements or "").strip(),
    "target_audience": (target_audience or "").strip(),
}

if submitted:
    try:
        with st.spinner("Generating proposal..."):
            prompt = email_proposal_prompt.format(**fields)
            resp = llm.invoke(prompt)
            body = resp.content.strip()

        st.subheader("Generated Proposal")
        st.markdown(body)

        st.download_button(
            label="⬇️ Download",
            data=body.encode("utf-8"),
            file_name=f"{(fields['project_title'] or 'proposal').replace(' ', '_')}.md",
            mime="text/markdown",
        )

    except Exception as e:
        st.error(f"Error generating proposal: {e}")
