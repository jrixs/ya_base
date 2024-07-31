import uuid

from sqlalchemy import select

from models.auth_data import History
from schemas.user import BasePagination, UserHistoryResponse, UserHistory
from services.base_services import PostgresDB


async def create_new_history_record(db_service: PostgresDB, user_id: str, record_data: str):
    db_event = History(
        id=str(uuid.uuid4()),
        user_id=user_id,
        user_agent=record_data
    )
    db_service.insert(db_event)


async def get_history_by_user(db_service: PostgresDB, user_id: str, pagination: BasePagination) -> UserHistoryResponse:
    statement = select(History).where(History.user_id == user_id).order_by(History.last_logged_at.desc()).offset(
        pagination.offset * pagination.limit).limit(pagination.limit)
    history_data = db_service.select_few(statement)
    history_list = [UserHistory.model_validate(item) for item in history_data]
    return UserHistoryResponse(id=user_id, history=history_list, total=len(history_list))
