import os
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

_openai_key = os.getenv("OPENAI_API_KEY")
if _openai_key is None:
    raise EnvironmentError("OPENAI_API_KEY is not set")
_openai_secret = SecretStr(_openai_key)
print("Key length:", len(_openai_key))
print("Starts with:", _openai_key[:8])
print("Ends with:", _openai_key[-4:])
print(repr(_openai_key))

llm1 = ChatOpenAI(model="gpt-4", api_key=_openai_secret)
llm2 = ChatOpenAI(model="gpt-4", api_key=_openai_secret)

schema = """
Table: courses
title (VARCHAR(255)): Full name of the course
class_level (VARCHAR(255)): Course classification (e.g., Undergraduate)
course_id (VARCHAR(255), PRIMARY KEY): Unique course identifier (e.g., CS2305)
This gives list of all courses

Table: grades
prof_name (VARCHAR(255), NOT NULL): Professor's first name and last name concatenated (eg. Aaron Smith -> AaronSmith)
term (VARCHAR(255), NOT NULL): Academic term code (e.g., 24F)
Aplus to F, W (INT, NULLABLE): Grade distribution columns
course_id (VARCHAR(255), NOT NULL): Course identifier
Primary Key: (course_id, prof_name, term)
Foreign Keys:
(prof_name) → professors(name)
course_id → courses(course_id)
This table gives grades distribution of each professor for each course taught by them

Table: professors
professorId (VARCHAR(255)): Optional unique identifier
name (VARCHAR(255), NOT NULL): Professor's first name and last name concatenated (eg. Aaron Smith -> AaronSmith)
email (VARCHAR(255)): Email address
phone_number (VARCHAR(255)): Phone number
Primary Key: (name)
This gives list of all professors.

Table: professor_remarks
prof_name (VARCHAR(255), NOT NULL): Professor's first name and last name concatenated (eg. Aaron Smith -> AaronSmith)
avg_difficulty (DOUBLE): Average difficulty rating
avg_rating (DOUBLE): Average overall rating
department (VARCHAR(255)): Department name
total_rating (VARCHAR(255)): Total number of ratings (stored as text)
r1 to r5 (INT): Count of 1–5 star ratings
tags (VARCHAR(255)): Tags describing the professor
would_take_again (DOUBLE): % of students who would take them again
Primary Key: (prof_name)
Foreign Key: (prof_name) → professors(name)
This table gives remarks about the professors """


sql_system_prompt = f"You are a PostgreSQL query generator. You generate concise queries with DISTINCT keyword for the provided prompt, with out any code blocks or markdown formatting. \
                 Only give query, no other text. \
                 Also use full form of course titles. eg: NLP = Natural Language Processing \
                 Also always give SQL queries, no direct answers. \
                 If just the first name of professor is passed, eg. Dung in Dung Hyunh, search the pattern in name accordingly.\
                 Utilize keywords such as LIMIT for restricting size of result if asked to. \
                 Do not give any destructive queries such as DROP or DELETE. \
                 Use this schema for generating queries.\
                 schema: {schema}"
nl_system_prompt = "You generate natural language responses. You will be given a question and a result from a SQL query relating to the question.\
                    If the query result is too big, ask for followup questions to get more specific answers. \
                    DO NOT GIVE TOO BIG RESULTS, ALWAYS GIVE PARTIAL AND ASK QUESTION TO GET MORE SPECIFIC QUESTION. \
                    You need to convert the query result into natural language response and answer the question. If the result says 'Failed' or the it is empty\
                    reply saying that 'I cannot answer the question. Also answer as if taking to another person, don't mentioned implementation details. \
                    If the result has list of items or table of content, display it in html lists, tables and other tags accordingly." \
                    "Have the html tables with proper borders as well. Do not add unnecessary spacing and newlines."

checkpointer1 = InMemorySaver()
sql_generator = create_agent(model=llm1, tools=[], system_prompt=sql_system_prompt, checkpointer=checkpointer1)
config = {"configurable": {"thread_id": "1"}}
def get_sql_query(user_input: str):
    for event in sql_generator.stream({"messages": [{"role": "user", "content": user_input}]}, config=config, stream_mode="values"):
        if len(event["messages"][-1].response_metadata) != 0:
            return event["messages"][-1].content
        
checkpointer2 = InMemorySaver()
nl_generator = create_agent(model=llm2, tools=[], system_prompt=nl_system_prompt, checkpointer=checkpointer2)

def get_nl_response(question: str, sql_result):
    model_input = f"question: {question} SQL result: {sql_result}"
    for event in nl_generator.stream({"messages": [{"role": "user", "content": model_input}]}, config=config, stream_mode="values"):
        if len(event["messages"][-1].response_metadata) != 0:
            return event["messages"][-1].content
