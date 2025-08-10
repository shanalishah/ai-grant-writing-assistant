# writingassistant.py

import os
import re
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# -------------------------------
# Unified credentials (secrets first, then .env)
# -------------------------------
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

# -------------------------------
# LLM (less creative + simple init)
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.2,           # lower creativity, more faithful to inputs
    openai_api_key=api_key
)

# -------------------------------
# Strict prompt to prevent invention
# -------------------------------
grant_proposal_prompt = PromptTemplate(
    input_variables=[
        "project_title", "project_description", "project_objectives",
        "funder_mission", "funder_focus_areas", "funder_requirements"
    ],
    template=(
        "You are a precise grant-writer. Using ONLY the inputs below, write a concise "
        "grant proposal INTRODUCTION (150–220 words).\n\n"
        "RULES:\n"
        "- Do not invent any facts.\n"
        "- If any info is missing, write 'TBD' instead of guessing.\n"
        "- No greetings, no sign-offs, no placeholders like [Funder's Name].\n"
        "- Use neutral, professional tone.\n\n"
        "INPUTS:\n"
        "Project Title: {project_title}\n"
        "Project Description: {project_description}\n"
        "Key Objectives: {project_objectives}\n"
        "Funder Mission: {funder_mission}\n"
        "Funder Focus Areas: {funder_focus_areas}\n"
        "Funder Requirements: {funder_requirements}\n\n"
        "OUTPUT:\n"
        "A single paragraph introduction that clearly aligns the project with the funder’s mission/focus and mentions measurable impact criteria."
    ),
)

# -------------------------------
# Output validator
# -------------------------------
def validate_output(text: str, inputs: dict) -> list[str]:
    issues = []

    # 1) Greetings/sign-offs
    if re.search(r"\bDear\b", text, re.IGNORECASE):
        issues.append("Output contains a greeting (e.g., 'Dear').")
    if re.search(r"\bSincerely\b|\bBest regards\b|\bRegards\b", text, re.IGNORECASE):
        issues.append("Output contains a sign-off (e.g., 'Sincerely').")

    # 2) Placeholder brackets
    if "[" in text or "]" in text:
        issues.append("Output contains bracket placeholders like [Funder’s Name].")

    # 3) Word count range
    words = len(re.findall(r"\w+", text))
    if words < 140 or words > 260:
        issues.append(f"Output length is {words} words (expected ~150–220).")

    # 4) Too many TBDs -> inputs too sparse
    tbd_count = len(re.findall(r"\bTBD\b", text))
    if tbd_count >= 3:
        issues.append("Too many 'TBD' markers—fill in more fields or be more specific.")

    # 5) Title must appear
    title = inputs.get("project_title", "").strip()
    if title and title.lower() not in text.lower():
        issues.append("Project title was not clearly echoed in the output.")

    # 6) At least some input content referenced
    touched = 0
    for k in ("project_description", "project_objectives", "funder_mission",
              "funder_focus_areas", "funder_requirements"):
        v = inputs.get(k, "").strip()
        if v:
            tokens = [t for t in v.split() if len(t) > 3][:3]
            if any(tok.lower() in text.lower() for tok in tokens):
                touched += 1
    if touched == 0:
        issues.append("None of the provided details were explicitly referenced (output may be generic).")

    return issues

# -------------------------------
# Auto-sanitizer (fix common issues)
# -------------------------------
def sanitize_output(text: str) -> str:
    # Remove greetings at the start of a line (e.g., "Dear ...")
    text = re.sub(r"(?im)^\s*dear\b.*?$", "", text)

    # Remove sign-offs at the end (e.g., "Sincerely, ...")
    text = re.sub(r"(?is)\b(sincerely|best regards|regards)\b.*$", "", text)

    # Remove bracket placeholders like [Funder’s Name] / [Your Title]
    text = re.sub(r"\[.*?\]", "", text)

    # Collapse excessive whitespace/newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text

# -------------------------------
# UI
# -------------------------------
st.title("Grant Proposal Writing Assistant")
st.markdown("Fill in the details below to generate a grant proposal introduction.")

with st.form("grant_form"):
    project_title = st.text_input(
        "Project Title",
        placeholder="e.g., Restoring Wetlands in Upstate NY"
    )
    project_description = st.text_area(
        "Project Description",
        placeholder="e.g., Restore 100 acres of degraded wetlands to improve flood control and biodiversity."
    )
    project_objectives = st.text_area(
        "Project Objectives (comma separated)",
        placeholder="e.g., Increase native species richness by 20%, reduce peak runoff by 15% within 12 months"
    )
    funder_mission = st.text_area(
        "Funder's Mission",
        placeholder="e.g., Advance climate resilience and ecological restoration"
    )
    funder_focus_areas = st.text_area(
        "Funder's Focus Areas",
        placeholder="e.g., Water resources, biodiversity, resilient infrastructure"
    )
    funder_requirements = st.text_area(
        "Funder's Requirements",
        placeholder="e.g., Evidence-based outcomes; community engagement plan; budget justification"
    )
    submitted = st.form_submit_button("Generate Proposal")

if submitted:
    # Trim and validate
    fields = {
        "project_title": project_title.strip(),
        "project_description": project_description.strip(),
        "project_objectives": project_objectives.strip(),
        "funder_mission": funder_mission.strip(),
        "funder_focus_areas": funder_focus_areas.strip(),
        "funder_requirements": funder_requirements.strip(),
    }

    if not all(fields.values()):
        st.warning("Please fill out all the fields (no blanks).")
    else:
        try:
            with st.spinner("Generating proposal..."):
                prompt_text = grant_proposal_prompt.format(**fields)
                response = llm.invoke(prompt_text)
                raw_text = response.content

                # Validate + auto-sanitize
                issues = validate_output(raw_text, fields)
                cleaned = sanitize_output(raw_text)

            st.subheader("Generated Grant Proposal Introduction")
            if issues:
                for i in issues:
                    st.warning(i)
            st.write(cleaned)

        except Exception as e:
            st.error(f"Error generating proposal: {e}")
