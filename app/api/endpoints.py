from fastapi import APIRouter
from pydantic import BaseModel,Field
from datetime import datetime
from app.services.tamp_service import get_coords, get_travel_time

router = APIRouter()

class TravelRequest(BaseModel):
    start_place: str
    end_place: str
    appointment_time: datetime   # "YYYY-MM-DD HH:MM"
    prepare_minutes: int = Field(..., alias="prep_time_min")
    sensitivity: str  # "안전/보통/효율"

@router.post("/alarm-time")
async def alarm_time(req: TravelRequest):
    start_coords = await get_coords(req.start_place)
    end_coords = await get_coords(req.end_place)

    travel_minutes = await get_travel_time(start_coords, end_coords)

    if req.sensitivity == "안전":
        buffer = 15
    elif req.sensitivity == "보통":
        buffer = 5
    else:  # 효율일때
        buffer = 0

    from datetime import timedelta
    appointment_dt = req.appointment_time
    alarm_dt = appointment_dt - timedelta(minutes=(travel_minutes + req.prepare_minutes + buffer))

    return {
        "alarm_time": alarm_dt.strftime("%Y-%m-%d %H:%M")
        }
