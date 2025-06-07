import jwt
import time
from my_service.config.config import settings
from my_service.models.models import ArgoCDCreds
import aiohttp
from cachetools import TTLCache
from my_service.utils.logger import setup_logger

creds = ArgoCDCreds(
    username=settings.ARGOCD_USERNAME,
    password=settings.ARGOCD_PASSWORD
)
logger = setup_logger()
token_cache = TTLCache(maxsize=1, ttl=settings.TOKEN_CACHE_TTL)

async def fetch_argocd_token():
    """Fetch JWT token from ArgoCD and store it with TTL based on expiration."""
    creds = ArgoCDCreds(
        username=settings.ARGOCD_USERNAME,
        password=settings.ARGOCD_PASSWORD
    )
    
    # Use HTTP for port-forwarded ArgoCD (since kubectl port-forward terminates TLS)
    base_url = f"http://{settings.ARGOCD_URL}"
    
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as temp_session:
        try:
            async with temp_session.post(
                f"{base_url}/api/v1/session",
                json=creds.model_dump(),
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"ArgoCD authentication failed: {resp.status} - {error_text}")
                    raise Exception(f"Failed to authenticate with ArgoCD: {resp.status}")
                
                data = await resp.json()
                token = data.get("token")
                if token:
                    logger.debug("ArgoCD session token has been successfully fetched")
                    try:
                        decoded = jwt.decode(
                            token, options={"verify_signature": False})
                        exp = decoded.get("exp", int(
                            time.time()) + settings.TOKEN_CACHE_TTL)
                        ttl = max(exp - int(time.time()) - 10, 60)
                    except Exception:
                        ttl = settings.TOKEN_CACHE_TTL
                    token_cache.clear()
                    token_cache[token] = ttl
                    logger.info("Token cached successfully")
                    return token
                raise Exception("No token in response")
        except Exception as e:
            logger.error(f"Failed to fetch ArgoCD token: {e}")
            raise

async def get_token():
    """Retrieve token from cache or fetch a new one if expired."""
    if not token_cache:
        logger.info("Cache is empty, fetching a new token")
        return await fetch_argocd_token()
    logger.info("Cache hit! found token in cache")
    logger.info(f"Cache: {token_cache}")
    return next(iter(token_cache.keys()))

async def get_argocd_applications(token: str):
    """Fetch all applications from ArgoCD"""
    base_url = f"http://{settings.ARGOCD_URL}"
    connector = aiohttp.TCPConnector(ssl=False)
    
    # FIXED: Use Cookie header instead of Bearer token
    headers = {
        "Cookie": f"argocd.token={token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(
                f"{base_url}/api/v1/applications",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Failed to fetch applications: {resp.status} - {error_text}")
                    raise Exception(f"Failed to fetch applications: {resp.status}")
                
                data = await resp.json()
                logger.info(f"Fetched {len(data.get('items', []))} applications from ArgoCD")
                return data.get("items", [])
        except Exception as e:
            logger.error(f"Error fetching applications: {e}")
            raise

async def get_argocd_projects(token: str):
    """Fetch all projects from ArgoCD"""
    base_url = f"http://{settings.ARGOCD_URL}"
    connector = aiohttp.TCPConnector(ssl=False)
    
    # FIXED: Use Cookie header instead of Bearer token
    headers = {
        "Cookie": f"argocd.token={token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(
                f"{base_url}/api/v1/projects",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Failed to fetch projects: {resp.status} - {error_text}")
                    raise Exception(f"Failed to fetch projects: {resp.status}")
                
                data = await resp.json()
                logger.info(f"Fetched {len(data.get('items', []))} projects from ArgoCD")
                return data.get("items", [])
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            raise