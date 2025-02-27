from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from utils.llm_handler import LLMHandler
from utils.sql_parser import SQLParser

# Create FastAPI app instance first
app = FastAPI()

# Initialize templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize handlers
llm_handler = LLMHandler()
sql_parser = SQLParser()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/explain")
async def explain_sql(sql_code: str = Form(...)):
    try:
        # Parse SQL code
        parsed_sql = sql_parser.parse(sql_code)
        
        # Get explanation from LLM
        explanation = await llm_handler.get_explanation(parsed_sql)
        
        return {"explanation": explanation}
    except Exception as e:
        return {"error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
