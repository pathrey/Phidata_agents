from fastapi import FastAPI, HTTPException
from phi.agent import Agent
from phi.model.groq import Groq
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware to allow requests from the specific frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize the agent
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

@app.post("/generate-horror-story")
async def generate_horror_story(request: Request):
    try:
        # Get the JSON body as a dictionary
        body = await request.json()
        
        # Get the topic from the request body (topic of the horror story)
        topic = body.get("topic")
        
        # Ensure the topic is provided
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        # Generate the horror story using the topic
        prompt = f"Share a 2-sentence horror story about {topic}."
        run = agent.run(prompt)
        
        # Return the generated story as a response
        return {"story": run.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
