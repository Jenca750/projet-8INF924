import os
import httpx
import docker
import logging

NTFY_URL = os.getenv("NTFY_URL", "http://ntfy:80")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "doorbell")
DOCKER_NTFY_CONTAINER = os.getenv("DOCKER_NTFY_CONTAINER", "iot_ntfy")

logger = logging.getLogger(__name__)

# Docker client connects to the socket mounted in the container
try:
    docker_client = docker.from_env()
except Exception as e:
    logger.error(f"Failed to initialize docker client: {e}")
    docker_client = None

SYSTEM_USER = os.getenv("NTFY_SYSTEM_USER")
SYSTEM_PASS = os.getenv("NTFY_SYSTEM_PASS")

_system_user_created = False

def _ensure_system_user():
    global _system_user_created
    if _system_user_created:
        return
    success, out = _run_ntfy_cli("user list")
    if success and SYSTEM_USER not in out:
        ntfy_add_user(SYSTEM_USER, SYSTEM_PASS, role="admin")
    _system_user_created = True

def push_notification(title: str, message: str, tags: list = None):
    """Push a notification to the ntfy topic via HTTP using system backend user"""
    _ensure_system_user()
    
    headers = {
        "Title": title,
    }
    if tags:
        headers["Tags"] = ",".join(tags)

    try:
        # Use docker compose service name "ntfy"
        url = f"http://ntfy:80/{NTFY_TOPIC}"
        with httpx.Client() as client:
            response = client.post(url, data=message.encode('utf-8'), headers=headers, auth=(SYSTEM_USER, SYSTEM_PASS))
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Failed to push notification to ntfy: {e}")
        return False

def _run_ntfy_cli(cmd: str, env: dict = None):
    if not docker_client:
        logger.error("Docker client not initialized. Cannot run ntfy CLI.")
        return False, "Docker client not initialized"
    
    try:
        container = docker_client.containers.get(DOCKER_NTFY_CONTAINER)
        full_cmd = f"ntfy {cmd}"
        exit_code, output = container.exec_run(full_cmd, environment=env)
        
        output_str = output.decode('utf-8') if output else ""
        if exit_code != 0:
            logger.error(f"ntfy CLI failed: {output_str}")
            return False, output_str
            
        return True, output_str
    except Exception as e:
        logger.error(f"Error executing ntfy CLI: {e}")
        return False, str(e)

def ntfy_add_user(username: str, password: str, role: str = "user"):
    """Adds a user to ntfy via docker exec"""
    success, output = _run_ntfy_cli(f"user add --role={role} {username}", env={"NTFY_PASSWORD": password})
    if success:
        # Give user read access to the specific topic (admins already have global read/write)
        if role != "admin":
            _run_ntfy_cli(f"access {username} {NTFY_TOPIC} read-only")
    return success

def ntfy_change_password(username: str, new_password: str):
    """Changes a user's password in ntfy via docker exec"""
    return _run_ntfy_cli(f"user change-pass {username}", env={"NTFY_PASSWORD": new_password})

def ntfy_delete_user(username: str):
    """Deletes a user from ntfy via docker exec"""
    return _run_ntfy_cli(f"user del {username}")
