from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import campaigns, chat, canvas  # Add canvas

app = FastAPI(title="StratGen API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(campaigns.router)
app.include_router(chat.router)
app.include_router(canvas.router)  # Add this line

@app.get("/")
def root():
    return {"message": "StratGen API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)