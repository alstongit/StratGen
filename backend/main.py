from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from routes import campaigns, chat, canvas

app = FastAPI(title="StratGen API")

# CORS: allow your Vercel domain via env
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check (for Render)
@app.get("/health")
def health():
    return {"status": "ok"}

# Routes
app.include_router(campaigns.router)
app.include_router(chat.router)
app.include_router(canvas.router)

@app.get("/")
def root():
    return {"message": "StratGen API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)