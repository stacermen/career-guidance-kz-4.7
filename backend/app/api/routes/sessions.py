from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import User
from app.schemas.schemas import SessionCreate, SessionOut

router = APIRouter()


@router.post("/session", response_model=SessionOut)
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)) -> SessionOut:
    user = User(name=payload.name, age=payload.age, education_level=payload.education_level)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return SessionOut.model_validate(user)
