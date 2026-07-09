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

o3_mini = ChatOpenAI(model="o3-mini", api_key=_openai_secret)
gpt4o_mini = ChatOpenAI(model="gpt-4o-mini", api_key=_openai_secret)

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


sql_system_prompt = f"You are an expert PostgreSQL engineer.\
                    Rules:\
                    - Use ONLY the tables and columns provided.\
                    - Do NOT invent columns or tables.\
                    - Use PostgreSQL syntax only.\
                    - If a join is required, infer it from the foreign keys.\
                    - Return ONLY the SQL query.\
                    - Do not return any explanation or text.\
                    - Do not return destructive queries (e.g., DROP, DELETE, UPDATE).\
                    schema: {schema}\
                    Here are few examples of how to write SQL queries based on the schema:\
                    1. Get professors that teach NLP course:\
                        SELECT DISTINCT p.name FROM professors p JOIN grades g ON p.name = g.prof_name JOIN courses c ON g.course_id = c.course_id WHERE c.title = 'Natural Language Processing';\
                    2. Give me information and ratings about professor Aaron Smith:\
                        SELECT * FROM professors p JOIN professor_remarks r ON p.name = r.prof_name WHERE p.name = 'AaronSmith';\
                    3. Get the average rating of professor Aaron Smith:\
                        SELECT r.avg_rating FROM professors p JOIN professor_remarks r ON p.name = r.prof_name WHERE p.name = 'AaronSmith';"

nl_system_prompt = "You generate natural language responses. You will be given a question and a result from a SQL query relating to the question.\
                    If the query result is too big, ask for followup questions to get more specific answers. \
                    DO NOT GIVE TOO BIG RESULTS, ALWAYS GIVE PARTIAL AND ASK QUESTION TO GET MORE SPECIFIC QUESTION. \
                    You need to convert the query result into natural language response and answer the question. If the result says 'Failed' or the it is empty\
                    reply saying that 'I cannot answer the question. Also answer as if taking to another person, don't mentioned implementation details. \
                    If the result has table of content, display it in html tables and other tags accordingly. \
                    For lists use bullet points. \
                    Have the html tables with proper borders as well. Do not add unnecessary spacing and newlines."

checkpointer1 = InMemorySaver()
sql_generator = create_agent(model=o3_mini, tools=[], system_prompt=sql_system_prompt, checkpointer=checkpointer1)
config = {"configurable": {"thread_id": "1"}}
def get_sql_query(user_input: str):
    for event in sql_generator.stream({"messages": [{"role": "user", "content": user_input}]}, config=config, stream_mode="values"):
        if len(event["messages"][-1].response_metadata) != 0:
            return event["messages"][-1].content
        
checkpointer2 = InMemorySaver()
nl_generator = create_agent(model=gpt4o_mini, tools=[], system_prompt=nl_system_prompt, checkpointer=checkpointer2)

def get_nl_response(question: str, sql_result):
    model_input = f"question: {question} SQL result: {sql_result}"
    for event in nl_generator.stream({"messages": [{"role": "user", "content": model_input}]}, config=config, stream_mode="values"):
        if len(event["messages"][-1].response_metadata) != 0:
            return event["messages"][-1].content
