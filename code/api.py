
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Bridge Lite API")

# Allow the frontend to communicate with the backend.
# We will restrict this to your Vercel domain after deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Bridge Lite API is running",
        "status": "online"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
