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
# LLM (less creative + no extra headers)
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

    # 1) No greetings/sign-offs
    if re.search(r"\bDear\b", text, re.IGNORECASE):
        issues.append("Output contains a greeting (e.g., 'Dear').")
    if re.search(r"\bSincerely\b|\bBest regards\b", text, re.IGNORECASE):
        issues.append("Output contains a sign-off (e.g., 'Sincerely').")

    # 2) No bracket placeholders
    if "[" in text or "]" in text:
        issues.append("Output contains bracket placeholders like [Funder’s Name].")

    # 3) Word count range
    words = len(re.findall(r"\w+", text))
    if words < 140 or words > 260:
        issues.append(f"Output length is {words} words (expected ~150–220).")

    # 4) Too much TBD implies weak inputs
    tbd_count = len(re.findall(r"\bTBD\b", text))
    if tbd_count >= 3:
        issues.append("Too many 'TBD' markers—fill in more fields or be more specific.")

    # 5) Must echo the title
    title = inputs.get("project_title", "").strip()
    if title and title.lower() not in text.lower():
        issues.append("Project title was not clearly echoed in the output.")

    # 6) At least some input content referenced
    touched = 0
    for k in ("project_description", "project_objectives", "funder_mission",
              "funder_focus_areas", "funder_requirements"):
        v = inputs.get(k, "").strip()
        if v:
            # crude echo check – looks for any early token in the output
            tokens = [t for t in v.split() if len(t) > 3][:3]
            if any(tok.lower() in text.lower() for tok in tokens):
                touched += 1
    if touched == 0:
        issues.append("None of the provided details were explicitly referenced (output may be generic).")

    return issues

# -------------------------------
# UI
# -------------------------------
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
                output_text = response.content

                # Validate before showing
                issues = validate_output(output_text, fields)
                st.subheader("Generated Grant Proposal Introduction")
                if issues:
                    for i in issues:
                        st.warning(i)

                st.write(output_text)

        except Exception as e:
            st.error(f"Error generating proposal: {e}")
