from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from pypdf import PdfReader
from phi.tools.duckduckgo import DuckDuckGo
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from io import BytesIO

app = FastAPI()

# CORS middleware to allow requests from the specific frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

api_key = "your-groq-key or do by setx cmd"  # Replace with your actual key
os.environ["GROQ_API_KEY"] = api_key  # Set in environment

# Function to extract text from a PDF file (either from a URL or local file path)
def extract_text_from_pdf(pdf_path):
    try:
        # Check if the input is a URL (starts with 'http://', 'https://')
        if pdf_path.lower().startswith(('http://', 'https://')):
            # Check if it's a Google Drive URL
            if "drive.google.com" in pdf_path:
                # Extract Google Drive file ID
                file_id = pdf_path.split('/d/')[1].split('/')[0]
                # Construct direct download URL
                pdf_path = f"https://drive.google.com/uc?export=download&id={file_id}"

            # It's a URL, download the PDF
            response = requests.get(pdf_path)
            if response.status_code != 200:
                raise ValueError(f"Failed to download PDF from URL: {pdf_path}")
            
            # Use BytesIO to treat the content like a file
            pdf_bytes = BytesIO(response.content)
            reader = PdfReader(pdf_bytes)
        
        elif os.path.exists(pdf_path):
            # It's a file path, read directly from storage
            reader = PdfReader(pdf_path)
        
        else:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text from all pages in the PDF
        extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        if not extracted_text:
            raise ValueError("No extractable text found in PDF")
        
        return extracted_text

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")


# Agents
web_agent = Agent(
    name="Web Agent",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    role="search job according to summary of resume",
    instructions=["Search jobs directly from 5 related companies' career pages", "always include sources"],
    show_tool_calls=True,
    markdown=True,
)

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

@app.post("/find")
async def find_jobs(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    
    pdf_path = data.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=400, detail="Missing 'pdf_path' in request body")
    
    pdf_text = extract_text_from_pdf(pdf_path)
    
    run: RunResponse = agent.run("Summarize: " + pdf_text)
    result: RunResponse = web_agent.run(run.content)
    
    return {"summary": run.content, "jobs": result.content}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
