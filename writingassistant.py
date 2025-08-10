# writingassistant.py

import os
import re
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# ==============================
# Credentials (secrets first, then .env)
# ==============================
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

# ==============================
# LLM (grounded & stable)
# ==============================
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,          # a bit more detail than 0.2, still grounded
    openai_api_key=api_key
)

# ==============================
# Full Proposal Prompt
# ==============================
full_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title", "project_description", "project_objectives",
        "funder_mission", "funder_focus_areas", "funder_requirements",
        "target_audience", "methods_workplan", "outcomes_metrics",
        "evaluation_plan", "budget_summary", "timeline_summary",
        "sustainability_plan", "org_overview", "risks_mitigation"
    ],
    template=(
        "You are an experienced grant writer. Using ONLY the inputs below, draft a **complete, professional grant proposal** "
        "formatted in Markdown with clear section headings and short paragraphs. If any detail is missing or unclear, write 'TBD' "
        "instead of inventing content. Do **not** include greetings or sign-offs.\n\n"

        "Required sections (use these exact headings):\n"
        "1. Executive Summary\n"
        "2. Needs Statement\n"
        "3. Project Description\n"
        "4. Objectives & Outcomes\n"
        "5. Methods & Work Plan\n"
        "6. Evaluation & Metrics\n"
        "7. Budget & Justification\n"
        "8. Timeline\n"
        "9. Sustainability\n"
        "10. Organizational Capacity\n"
        "11. Alignment with Funder Priorities\n"
        "12. Risks & Mitigation\n"
        "13. Conclusion\n\n"

        "Style/Constraints:\n"
        "- Write 600–1,000 words total.\n"
        "- Use concise, specific, non-repetitive language.\n"
        "- Tie claims to the provided inputs; do not add external facts.\n"
        "- Where relevant, echo measurable targets and how they’ll be tracked.\n"
        "- No placeholders like [Funder Name] or [Your Title].\n\n"

        "INPUTS\n"
        "Project Title: {project_title}\n"
        "Project Description: {project_description}\n"
        "Key Objectives: {project_objectives}\n"
        "Funder Mission: {funder_mission}\n"
        "Funder Focus Areas: {funder_focus_areas}\n"
        "Funder Requirements: {funder_requirements}\n"
        "Target Audience/Beneficiaries: {target_audience}\n"
        "Methods & Work Plan (how you’ll execute): {methods_workplan}\n"
        "Outcomes & Metrics (what success looks like): {outcomes_metrics}\n"
        "Evaluation Plan (how you’ll measure): {evaluation_plan}\n"
        "Budget Summary (major cost categories): {budget_summary}\n"
        "Timeline Summary (key milestones): {timeline_summary}\n"
        "Sustainability Plan (after funding): {sustainability_plan}\n"
        "Organizational Overview (capacity): {org_overview}\n"
        "Risks & Mitigation: {risks_mitigation}\n\n"

        "OUTPUT:\n"
        "A complete Markdown proposal with the required headings, grounded only in the inputs above."
    ),
)

# ==============================
# Output checks
# ==============================
REQUIRED_HEADINGS = [
    "Executive Summary",
    "Needs Statement",
    "Project Description",
    "Objectives & Outcomes",
    "Methods & Work Plan",
    "Evaluation & Metrics",
    "Budget & Justification",
    "Timeline",
    "Sustainability",
    "Organizational Capacity",
    "Alignment with Funder Priorities",
    "Risks & Mitigation",
    "Conclusion",
]

def validate_output_md(text: str, inputs: dict) -> list[str]:
    issues = []

    # ban greetings/sign-offs
    if re.search(r"(?im)^\s*dear\b", text):
        issues.append("Contains a greeting (e.g., 'Dear').")
    if re.search(r"(?im)\b(sincerely|best regards|regards)\b", text):
        issues.append("Contains a sign-off (e.g., 'Sincerely').")

    # no bracket placeholders
    if "[" in text or "]" in text:
        issues.append("Contains square-bracket placeholders (e.g., [Funder Name]).")

    # headings present
    missing = [h for h in REQUIRED_HEADINGS if not re.search(rf"(?im)^#{1,3}\s*{re.escape(h)}\s*$|(?im)^\s*{re.escape(h)}\s*$", text)]
    if missing:
        issues.append(f"Missing required section(s): {', '.join(missing)}.")

    # rough word count
    wc = len(re.findall(r"\w+", text))
    if wc < 550:
        issues.append(f"Proposal seems short ({wc} words). Aim for 600–1,000 words.")
    if wc > 1200:
        issues.append(f"Proposal seems long ({wc} words). Aim for 600–1,000 words.")

    # echo project title
    title = (inputs.get("project_title") or "").strip()
    if title and title.lower() not in text.lower():
        issues.append("Project title was not clearly echoed.")

    return issues

def sanitize_output(text: str) -> str:
    # strip greetings/sign-offs lines
    text = re.sub(r"(?im)^\s*dear\b.*?$", "", text)
    text = re.sub(r"(?is)\b(sincerely|best regards|regards)\b.*$", "", text)
    # remove bracket placeholders
    text = re.sub(r"\[.*?\]", "", text)
    # collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

# ==============================
# UI
# ==============================
st.title("AI-Powered Grant Proposal Generator")
st.markdown("Provide what you know. The tool will keep it factual and use **TBD** when something’s missing.")

with st.form("proposal_form"):
    st.subheader("Core")
    project_title = st.text_input("Project Title", placeholder="Restoring Wetlands in Upstate NY")
    project_description = st.text_area("Project Description", placeholder="Restore 100 acres of degraded wetlands to improve flood control and biodiversity.")
    project_objectives = st.text_area("Key Objectives (comma-separated)", placeholder="Increase native species richness by 20%; Reduce peak runoff by 12% within 12 months")

    st.subheader("Funder & Alignment")
    funder_mission = st.text_area("Funder Mission", placeholder="Advance climate resilience and ecological restoration.")
    funder_focus_areas = st.text_area("Funder Focus Areas", placeholder="Water resources; biodiversity; resilient infrastructure")
    funder_requirements = st.text_area("Funder Requirements", placeholder="Evidence-based outcomes; community engagement; budget justification")

    st.subheader("Execution")
    target_audience = st.text_area("Target Audience / Beneficiaries", placeholder="Communities in flood-prone watersheds; local conservation partners")
    methods_workplan = st.text_area("Methods & Work Plan", placeholder="Site assessment, native planting, hydrology restoration, community volunteer days")
    outcomes_metrics = st.text_area("Outcomes & Metrics", placeholder="Species richness change; water retention; reduced peak flow; volunteer hours")
    evaluation_plan = st.text_area("Evaluation Plan", placeholder="Before/after biodiversity surveys; hydrological monitoring; quarterly progress reviews")

    st.subheader("Resourcing")
    budget_summary = st.text_area("Budget Summary", placeholder="Plants & materials; equipment rental; monitoring; community engagement; project management")
    timeline_summary = st.text_area("Timeline Summary", placeholder="Phase 1 (Q1–Q2): site prep; Phase 2 (Q3): planting; Phase 3 (Q4): monitoring")
    sustainability_plan = st.text_area("Sustainability Plan", placeholder="Stewardship agreements; municipal maintenance; citizen science monitoring")
    org_overview = st.text_area("Organizational Overview", placeholder="Track record in habitat restoration; staff expertise; partnerships")
    risks_mitigation = st.text_area("Risks & Mitigation", placeholder="Drought risk (install cisterns); invasive species (ongoing removal); community buy-in (early engagement)")

    submitted = st.form_submit_button("Generate Full Proposal")

# Build inputs (allow blanks; prompt will use TBD)
fields = {
    "project_title": (project_title or "").strip(),
    "project_description": (project_description or "").strip(),
    "project_objectives": (project_objectives or "").strip(),
    "funder_mission": (funder_mission or "").strip(),
    "funder_focus_areas": (funder_focus_areas or "").strip(),
    "funder_requirements": (funder_requirements or "").strip(),
    "target_audience": (target_audience or "").strip(),
    "methods_workplan": (methods_workplan or "").strip(),
    "outcomes_metrics": (outcomes_metrics or "").strip(),
    "evaluation_plan": (evaluation_plan or "").strip(),
    "budget_summary": (budget_summary or "").strip(),
    "timeline_summary": (timeline_summary or "").strip(),
    "sustainability_plan": (sustainability_plan or "").strip(),
    "org_overview": (org_overview or "").strip(),
    "risks_mitigation": (risks_mitigation or "").strip(),
}

if submitted:
    try:
        with st.spinner("Drafting full proposal..."):
            prompt = full_proposal_prompt.format(**fields)
            resp = llm.invoke(prompt)
            raw_md = resp.content

        issues = validate_output_md(raw_md, fields)
        cleaned_md = sanitize_output(raw_md)

        st.subheader("Generated Proposal")
        if issues:
            for i in issues:
                st.warning(i)
        st.markdown(cleaned_md)

        st.download_button(
            label="⬇️ Download as Markdown",
            data=cleaned_md.encode("utf-8"),
            file_name=f"{(fields['project_title'] or 'proposal').replace(' ', '_')}.md",
            mime="text/markdown",
        )

    except Exception as e:
        st.error(f"Error generating proposal: {e}")
