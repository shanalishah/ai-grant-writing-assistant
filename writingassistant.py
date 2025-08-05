# Gen AI Apps for Business - Shan Ali Shah Sayed

# -------------------------

# Environmental Conservation: Grant Writing Assistant

# -------------------------

# !pip install langchain openai python-dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os


# -------------------------

# Loading API key which is saved in a file named .env saved in the same folder as this jupyter file. 

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# -------------------------

llm = ChatOpenAI(model="gpt-4", temperature=0.7)


# -------------------------

# Defining Prompt Template for Grant Proposal Writing as per the assignment topic chosen: Environmental Conservation

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

def collect_inputs():
    print("Welcome to the Grant Proposal Writing Assistant!")
    print("Please provide details about your project and the funder to create a tailored grant proposal introduction.\n")

    project_title = input("Enter the project title: ")
    project_description = input("Provide a brief description of the project: ")
    project_objectives = input("List the key objectives of the project (separate by commas): ")
    funder_mission = input("What is the mission of the funder? ")
    funder_focus_areas = input("What are the focus areas of the funder? ")
    funder_requirements = input("What are the requirements of the funder? ")

    return {
        "project_title": project_title,
        "project_description": project_description,
        "project_objectives": project_objectives,
        "funder_mission": funder_mission,
        "funder_focus_areas": funder_focus_areas,
        "funder_requirements": funder_requirements,
    }
    

# -------------------------

user_inputs = collect_inputs()
formatted_prompt = grant_proposal_prompt.format(**user_inputs)
conversation = ConversationChain(llm=llm)
response = conversation.run(formatted_prompt)
print("\n--- Grant Proposal Introduction ---\n")
print(response)


# -------------------------

# --
