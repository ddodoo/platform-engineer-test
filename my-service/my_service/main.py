import uvicorn
from fastapi import FastAPI, status, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from my_service.config.config import settings
from my_service.models.models import HealthCheckResponse
from my_service.utils.logger import setup_logger
from my_service.api.v1 import api

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()
logger.debug(f"Running with config: {settings}")

# Get ArgoCD server details from environment variables
ARGOCD_SERVER = os.getenv("ARGOCD_SERVER", "argocd-server.argocd.svc.cluster.local")
ARGOCD_PORT = os.getenv("ARGOCD_PORT", "443")
SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() == "true"

# Models for ArgoCD API responses
class ApplicationStatus(BaseModel):
    application_name: str
    status: str

class ApplicationStatusResponse(BaseModel):
    applications: List[ApplicationStatus]

class Project(BaseModel):
    project_name: str
    namespace: str

class ProjectsResponse(BaseModel):
    projects: List[Project]

# Initialize FastAPI application
def get_application():
    _app = FastAPI(title=settings.FASTAPI_PROJECT_NAME)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    return _app

app = get_application()
app.include_router(api.router)

# Middleware to verify token
async def verify_token(authorization: str = Header(None)):
    """ Extract and validate the Bearer token from the request header. """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return authorization.split(" ")[1]  # Extract token

@app.get("/healthcheck")
async def healthcheck() -> HealthCheckResponse:
    logger.debug("healthcheck hit")
    return HealthCheckResponse(
        status_code=status.HTTP_200_OK,
        message="Server is running!"
    )

@app.get("/api/v1/argocd/application_status", response_model=ApplicationStatusResponse)
async def get_application_status(token: str = Depends(verify_token)):
    """ Fetch application status from ArgoCD using the provided token. """
    logger.debug("ArgoCD application status endpoint hit")

    async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
        response = await client.get(
            f"http://argocd-server.argocd.svc.cluster.local:443/api/v1/applications",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch application status")

        applications_data = response.json().get("items", [])
        applications = [
            ApplicationStatus(
                application_name=app.get("metadata", {}).get("name", ""),
                status=app.get("status", {}).get("sync", {}).get("status", "Unknown")
            )
            for app in applications_data
        ]

        return ApplicationStatusResponse(applications=applications)

@app.get("/api/v1/argocd/list_projects", response_model=ProjectsResponse)
async def list_projects(token: str = Depends(verify_token)):
    """ Fetch list of ArgoCD projects using the provided token. """
    logger.debug("ArgoCD list projects endpoint hit")

    async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
        response = await client.get(
            f"http://argocd-server.argocd.svc.cluster.local:443/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch project list")

        projects_data = response.json().get("items", [])
        projects = [
            Project(
                project_name=project.get("metadata", {}).get("name", ""),
                namespace=project.get("metadata", {}).get("namespace", "argocd")
            )
            for project in projects_data
        ]

        return ProjectsResponse(projects=projects)

if __name__ == "__main__":
    uvicorn.run("my_service.main:app", host="0.0.0.0", port=9000, reload=True)
