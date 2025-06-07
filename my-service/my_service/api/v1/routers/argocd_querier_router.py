from fastapi import Depends, HTTPException
from my_service.dependencies import get_token, get_argocd_applications, get_argocd_projects
from my_service.utils.logger import setup_logger
from my_service.models.models import ApplicationStatusResponse, ProjectsResponse, ApplicationStatus, ProjectInfo
from fastapi import APIRouter

router = APIRouter(
    prefix="/argocd",  # Fixed typo: was "arogocd"
    tags=["argocd"],
)

logger = setup_logger()

@router.get("/application_status", response_model=ApplicationStatusResponse)
async def application_status(token: str = Depends(get_token)):
    """Fetches all ArgoCD applications statuses
    
    Args:
        token (str, optional): ArgoCD authentication token. Defaults to Depends(get_token).
    
    Returns:
        ApplicationStatusResponse: concise application metadata json structure
    """
    try:
        logger.info("Fetching ArgoCD applications status")
        
        # Fetch applications from ArgoCD
        applications_data = await get_argocd_applications(token)
        
        # Transform data to match expected response format
        applications = []
        for app in applications_data:
            app_name = app.get("metadata", {}).get("name", "unknown")
            
            # Get sync status from status.sync.status field
            sync_status = app.get("status", {}).get("sync", {}).get("status", "Unknown")
            
            applications.append(ApplicationStatus(
                application_name=app_name,
                status=sync_status
            ))
        
        logger.info(f"Successfully fetched {len(applications)} applications")
        return ApplicationStatusResponse(applications=applications)
        
    except Exception as e:
        logger.error(f"Failed to fetch application status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch application status: {str(e)}")

@router.get("/list_projects", response_model=ProjectsResponse)
async def list_projects(token: str = Depends(get_token)):
    """Fetches all argocd projects names and namespaces to which they are configured
    
    Args:
        token (str, optional): ArgoCD authentication token. Defaults to Depends(get_token).
    
    Returns:
        ProjectsResponse: concise argocd projects metadata json structure
    """
    try:
        logger.info("Fetching ArgoCD projects")
        
        # Fetch projects from ArgoCD
        projects_data = await get_argocd_projects(token)
        
        # Transform data to match expected response format
        projects = []
        for project in projects_data:
            project_name = project.get("metadata", {}).get("name", "unknown")
            
            # ArgoCD projects are created in the argocd namespace by default
            # The namespace where the project config is stored is typically 'argocd'
            project_namespace = project.get("metadata", {}).get("namespace", "argocd")
            
            projects.append(ProjectInfo(
                project_name=project_name,
                namespace=project_namespace
            ))
        
        logger.info(f"Successfully fetched {len(projects)} projects")
        return ProjectsResponse(projects=projects)
        
    except Exception as e:
        logger.error(f"Failed to fetch projects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")