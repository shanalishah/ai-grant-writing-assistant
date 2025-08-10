# writingassistant.py

import os
from io import BytesIO

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# For downloads
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# Session state init

def _init_once():
    defaults = {
        "proposal_body": "",
        "proposal_title": "proposal",
        "project_title": "",
        "project_description": "",
        "project_objectives": "",
        "funder_mission": "",
        "funder_focus_areas": "",
        "funder_requirements": "",
        "target_audience": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_once()


# Credentials

api_key = None
try:
    # Streamlit Cloud
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    # Local .env
    try:
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    except Exception:
        pass

if not api_key:
    st.error("OpenAI API key not found. Add it to Streamlit secrets or your local .env.")
    st.stop()


# Model

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key=api_key,
)


# Prompt

email_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title",
        "project_description",
        "project_objectives",
        "funder_mission",
        "funder_focus_areas",
        "funder_requirements",
        "target_audience",
    ],
    template=(
        "You are an experienced grant writer. Using ONLY the inputs below, draft a full, email-style grant proposal "
        "written as 3–6 cohesive paragraphs (no headings, no bullet lists). Do not include a greeting or a sign-off. "
        "If a detail is missing, write 'TBD' rather than inventing facts. Keep the tone professional, persuasive, and concise. "
        "Aim for 500–900 words.\n\n"
        "Inputs:\n"
        "- Project Title: {project_title}\n"
        "- Project Description: {project_description}\n"
        "- Key Objectives: {project_objectives}\n"
        "- Funder Mission: {funder_mission}\n"
        "- Funder Focus Areas: {funder_focus_areas}\n"
        "- Funder Requirements: {funder_requirements}\n"
        "- Target Audience/Beneficiaries: {target_audience}\n\n"
        "Output:\n"
        "A polished, multi-paragraph email-style proposal body (no salutation, no signature)."
    ),
)


# UI

st.set_page_config(page_title="AI-Powered Grant Writing Assistant", layout="centered")
st.title("AI-Powered Grant Writing Assistant")
st.caption("Provide the essential details and the assistant will generate a proposal based on your inputs.")

with st.form("proposal_form"):
    project_title = st.text_input(
        "Project Title",
        value=st.session_state.project_title,
        placeholder="Restoring Wetlands in Upstate NY",
    )
    project_description = st.text_area(
        "Project Description",
        value=st.session_state.project_description,
        placeholder="Restore 100 acres of degraded wetlands to improve flood control and biodiversity.",
    )
    project_objectives = st.text_area(
        "Key Objectives (comma-separated)",
        value=st.session_state.project_objectives,
        placeholder="Increase native species richness by 20%; Reduce peak runoff by 12% within 12 months",
    )
    funder_mission = st.text_area(
        "Funder Mission",
        value=st.session_state.funder_mission,
        placeholder="Advance climate resilience and ecological restoration.",
    )
    funder_focus_areas = st.text_area(
        "Funder Focus Areas",
        value=st.session_state.funder_focus_areas,
        placeholder="Water resources; biodiversity; resilient infrastructure",
    )
    funder_requirements = st.text_area(
        "Funder Requirements",
        value=st.session_state.funder_requirements,
        placeholder="Evidence-based outcomes; community engagement; budget justification",
    )
    target_audience = st.text_area(
        "Target Audience / Beneficiaries (optional)",
        value=st.session_state.target_audience,
        placeholder="Communities in flood-prone watersheds; local conservation partners",
    )

    submitted = st.form_submit_button("Generate Proposal")

if submitted:
    st.session_state.project_title = (project_title or "").strip()
    st.session_state.project_description = (project_description or "").strip()
    st.session_state.project_objectives = (project_objectives or "").strip()
    st.session_state.funder_mission = (funder_mission or "").strip()
    st.session_state.funder_focus_areas = (funder_focus_areas or "").strip()
    st.session_state.funder_requirements = (funder_requirements or "").strip()
    st.session_state.target_audience = (target_audience or "").strip()

    try:
        with st.spinner("Generating proposal..."):
            prompt = email_proposal_prompt.format(
                project_title=st.session_state.project_title,
                project_description=st.session_state.project_description,
                project_objectives=st.session_state.project_objectives,
                funder_mission=st.session_state.funder_mission,
                funder_focus_areas=st.session_state.funder_focus_areas,
                funder_requirements=st.session_state.funder_requirements,
                target_audience=st.session_state.target_audience,
            )
            resp = llm.invoke(prompt)
            st.session_state.proposal_body = (resp.content or "").strip()
            title = st.session_state.project_title or "proposal"
            st.session_state.proposal_title = "_".join(title.split())
        st.success("Proposal generated.")
    except Exception as e:
        st.error(f"Error generating proposal: {e}")

if st.session_state.proposal_body:
    st.subheader("Generated Proposal")
    st.markdown(st.session_state.proposal_body)

    # DOCX download
    docx_buffer = BytesIO()
    doc = Document()
    for para in st.session_state.proposal_body.split("\n\n"):
        doc.add_paragraph(para)
    doc.save(docx_buffer)
    docx_buffer.seek(0)
    st.download_button(
        "⬇️ Download as DOCX",
        data=docx_buffer,
        file_name=f"{st.session_state.proposal_title}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        key="dl_docx",
    )

    # PDF download
    pdf_buffer = BytesIO()
    pdf_doc = SimpleDocTemplate(pdf_buffer)
    styles = getSampleStyleSheet()
    flow = []
    for para in st.session_state.proposal_body.split("\n\n"):
        flow.append(Paragraph(para, styles["Normal"]))
        flow.append(Spacer(1, 12))
    pdf_doc.build(flow)
    pdf_buffer.seek(0)
    st.download_button(
        "⬇️ Download as PDF",
        data=pdf_buffer,
        file_name=f"{st.session_state.proposal_title}.pdf",
        mime="application/pdf",
        key="dl_pdf",
    )
