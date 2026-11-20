import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import MismatchingStateError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv
from database import SessionLocal, Device
from workload_demo import read_secret

load_dotenv()
app = FastAPI()
# Session cookies are signed, not encrypted. Use a separate name for this lab.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
    session_cookie="oauth_lab_session",
    same_site="lax",
    https_only=False,  # Keep False for local HTTP development
)
# 2. CORS Middleware: Allows our WebStorm frontend (port 5173) to talk to FastAPI (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 3. Configure OAuth Client (OpenID Connect)
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth Guard Dependency (Protects CRUD endpoints)
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# --- OAUTH ROUTES ---

@app.get("/auth/login")
async def login(request: Request):
    # Force localhost to match your first Google Console entry
    redirect_uri = "http://localhost:8000/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    # Back-channel exchange: trades temporary auth code + client_secret for tokens
    try:
        token = await oauth.google.authorize_access_token(request)
    except MismatchingStateError as error:
        raise HTTPException(
            status_code=400,
            detail="Login session was lost or expired. Start again from http://localhost:5173 "
                   "and use localhost for both the frontend and backend.",
        ) from error
    user_info = token.get("userinfo")
    # Store only the small user profile in the signed session cookie
    request.session["user"] = {"email": user_info["email"], "name": user_info["name"]}
    # Send user back to WebStorm frontend
    return RedirectResponse(url="http://localhost:5173")

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}

@app.get("/auth/me")
async def read_users_me(user: dict = Depends(get_current_user)):
    return user

@app.get("/api/workload/secrets/{resource}")
def read_workload_secret(
    resource: str,
    user: dict = Depends(get_current_user),):
    principal = "inventory-worker"
    try:
        value = read_secret(principal, resource)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Worker is not permitted to read this resource",)
    return {
        "worker": principal,
        "resource": resource,
        "value": value,}

# --- CRUD ROUTES (Protected) ---

class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str

@app.get("/api/devices")
def list_devices(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Authorisation check: only return devices owned by this user
    return db.query(Device).filter(Device.owner_email == user["email"]).all()

@app.post("/api/devices")
def create_device(item: DeviceCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = Device(hostname=item.hostname, ip_address=item.ip_address, owner_email=user["email"])
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.delete("/api/devices/{device_id}")
def delete_device(device_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.owner_email == user["email"]).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return {"deleted": True}