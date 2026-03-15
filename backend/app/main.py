from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from .api.endpoints import router as api_router
from .api.auth import router as auth_router
from .db.session import init_db
import uvicorn

# OAuth2 scheme — tells Swagger UI where the login endpoint is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(
    title="Neural BI Synthesis API",
    description="""
    ## Overview
    Secure enterprise-grade API for autonomous data synthesis and Conversational Business Intelligence.
    
    ### Core Capabilities
    - **Security & Identity**: JWT-secured operative management and session authorization.
    - **Neural Synthesis**: Natural language processing for real-time data analysis and visualization.
    - **Matrix Management**: Isolated data ingestion and physical asset lifecycle control.

    ---
    ### How to authenticate in docs:
    1. Call **POST /api/auth/register** to create an account.
    2. Call **POST /api/auth/login** — enter your email as `username` and your `password`.
    3. Copy the `access_token` from the response.
    4. Click the **Authorize 🔒** button at the top and paste the token.
    """,
    version="2.5.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
init_db()

# Include Routers
app.include_router(auth_router, prefix="/api")
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Neural BI API Online"}
