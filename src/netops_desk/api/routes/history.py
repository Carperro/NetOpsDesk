"""Rutas de la API para el Historial."""

from fastapi import APIRouter, Depends, status
from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models.history import HistoryInput, HistoryOutput
from netops_desk.history import add_log, get_logs, remove_log, clear_logs
from netops_desk.repositories.history_repository import SQLiteHistoryRepository

router = APIRouter(tags=["History"])

def get_history_repo() -> SQLiteHistoryRepository:
    return SQLiteHistoryRepository()

@router.get("/api/v1/tools/history/logs", response_model=list[HistoryOutput])
async def list_logs_endpoint(repo: SQLiteHistoryRepository = Depends(get_history_repo)):
    return get_logs(repo=repo)

@router.post("/api/v1/tools/history/logs", response_model=HistoryOutput, status_code=status.HTTP_201_CREATED)
async def create_log_endpoint(
    body: HistoryInput,
    _: None = Depends(require_json_content_type),
    repo: SQLiteHistoryRepository = Depends(get_history_repo)
):
    return add_log(repo=repo, data=body.model_dump())

@router.delete("/api/v1/tools/history/logs/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log_endpoint(
    record_id: int,
    repo: SQLiteHistoryRepository = Depends(get_history_repo)
):
    remove_log(repo=repo, record_id=record_id)
    return None

@router.delete("/api/v1/tools/history/logs", status_code=status.HTTP_204_NO_CONTENT)
async def clear_logs_endpoint(repo: SQLiteHistoryRepository = Depends(get_history_repo)):
    clear_logs(repo=repo)
    return None