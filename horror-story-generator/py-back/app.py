from fastapi import FastAPI, HTTPException, Request
from phi.agent import Agent
from phi.model.groq import Groq
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS middleware to allow requests from the specific frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["your url or "*"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize the AI agents
scene = Agent(
    role="generate scene description",
    instructions=["Generate a detailed horror scene description in 100 words."],
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

story_generate = Agent(
    role="generate story",
    instructions=["Write a short horror story based on the provided topic."],
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

multi_agent = Agent(
    team=[scene, story_generate],
    instructions=["Always include heading of scene and story."],
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

@app.post("/generate-horror-story")
async def generate_horror_story(request: Request):
    try:
        # Get the JSON body as a dictionary
        body = await request.json()
        
        # Get the prompts for both scene and story from request body
        scene_prompt = body.get("scene_prompt")
        story_prompt = body.get("story_prompt")
        
        # Ensure both prompts are provided
        if not scene_prompt or not story_prompt:
            raise HTTPException(status_code=400, detail="Both scene_prompt and story_prompt are required")

        # Generate the horror scene (short scary moment)
        scene_result = multi_agent.run(scene_prompt)

        # Generate the full horror story
        story_result = multi_agent.run(story_prompt)

        return {
            "scene": scene_result.content.strip(),
            "story": story_result.content.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "Server is running smoothly."}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
