from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(title="AgentOps Workbench API")
app.state.settings = settings
app.include_router(health_router)
