# writingassistant.py

import os
import re
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# ========== Credentials ==========
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

# ========== Model ==========
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key=api_key,
)

# ========== Prompt (Full proposal, minimal inputs) ==========
full_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title",
        "project_description",
        "project_objectives",
        "funder_mission",
        "funder_focus_areas",
        "funder_requirements",
        "target_audience",  # optional; can be blank
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
        "- Write ~700–1,000 words total.\n"
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
        "Target Audience/Beneficiaries: {target_audience}\n\n"

        "OUTPUT:\n"
        "A complete Markdown proposal with the required headings, grounded only in the inputs above."
    ),
)

# ========== Validators / Sanitizers (fixed regex flags) ==========
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

    # greetings / sign-offs
    if re.search(r"^\s*dear\b", text, flags=re.IGNORECASE | re.MULTILINE):
        issues.append("Contains a greeting (e.g., 'Dear').")
    if re.search(r"\b(sincerely|best regards|regards)\b", text, flags=re.IGNORECASE):
        issues.append("Contains a sign-off (e.g., 'Sincerely').")

    # bracket placeholders
    if "[" in text or "]" in text:
        issues.append("Contains square-bracket placeholders (e.g., [Funder Name]).")

    # required headings present (compile once with flags)
    heading_regexes = [
        re.compile(rf"^#{1,3}\s*{re.escape(h)}\s*$|^\s*{re.escape(h)}\s*$",
                   flags=re.IGNORECASE | re.MULTILINE)
        for h in REQUIRED_HEADINGS
    ]
    missing = [h for h, rx in zip(REQUIRED_HEADINGS, heading_regexes) if not rx.search(text)]
    if missing:
        issues.append(f"Missing required section(s): {', '.join(missing)}.")

    # rough word count
    wc = len(re.findall(r"\w+", text))
    if wc < 600:
        issues.append(f"Proposal seems short ({wc} words). Aim for 700–1,000 words.")
    if wc > 1200:
        issues.append(f"Proposal seems long ({wc} words). Aim for 700–1,000 words.")

    # echo project title
    title = (inputs.get("project_title") or "").strip()
    if title and title.lower() not in text.lower():
        issues.append("Project title was not clearly echoed.")

    return issues

def sanitize_output(text: str) -> str:
    # strip greetings/sign-offs lines
    text = re.sub(r"^\s*dear\b.*?$", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"\b(sincerely|best regards|regards)\b.*$", "", text, flags=re.IGNORECASE | re.DOTALL)
    # remove bracket placeholders
    text = re.sub(r"\[.*?\]", "", text)
    # collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

# ========== UI (minimal inputs, consistent placeholders) ==========
st.title("AI-Powered Grant Proposal Generator")
st.markdown("Provide the essentials. The tool will keep it factual and use **TBD** where info is missing.")

with st.form("proposal_form"):
    project_title = st.text_input("Project Title", placeholder="Restoring Wetlands in Upstate NY")
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

    submitted = st.form_submit_button("Generate Full Proposal")

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
