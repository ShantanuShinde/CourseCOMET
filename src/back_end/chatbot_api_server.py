from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from llm_querier import get_sql_query, get_nl_response
from sql_manager import get_query_results

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post('/api/ask')
async def answer_question(request: Request):
    data = await request.json()
    question = data.get("question")
    query = get_sql_query(question)
    result = get_query_results(query)
    response = get_nl_response(question, result)
    print(response)
    return {"response" : response}
