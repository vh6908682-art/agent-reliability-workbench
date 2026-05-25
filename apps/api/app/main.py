from fastapi import FastAPI

from app.api.routes.agent_runs import router as agent_runs_router
from app.api.routes.evals import router as evals_router
from app.api.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(title="AgentOps Workbench API")
app.state.settings = settings
app.include_router(agent_runs_router)
app.include_router(evals_router)
app.include_router(health_router)
