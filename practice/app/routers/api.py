from fastapi import APIRouter

from app.models.water import WaterLog
from app.models.exercise import ExerciseLog
from app.models.sleep import SleepLog
from app.models.meal import MealLog
from app.schemas import WaterCreate, WaterOut, ExerciseCreate, ExerciseOut, SleepCreate, SleepOut, MealCreate, MealOut, ListResponse

router = APIRouter()


@router.get("/water", response_model=ListResponse[WaterOut])
async def list_water():
    logs = await WaterLog.all().order_by("-logged_at")
    return {"items": [WaterOut.model_validate(log) for log in logs], "total": len(logs)}


@router.post("/water", response_model=WaterOut)
async def create_water(payload: WaterCreate):
    log = await WaterLog.create(user_id=payload.user_id, amount_ml=payload.amount_ml)
    return WaterOut.model_validate(log)


# TODO: Exercise/Sleep/Meal API를 추가해 보세요.
@router.post("/exercise", response_model=ExerciseOut)
async def create_exercise(payload: ExerciseCreate):
    log = await ExerciseLog.create(user_id=payload.user_id, activity=payload.activity, duration_min=payload.duration_min, calories_burned=payload.calories_burned)
    return ExerciseOut.model_validate(log)

@router.post("/sleep", response_model=SleepOut)
async def create_sleep(payload: SleepCreate):
    log = await SleepLog.create(user_id=payload.user_id, sleep_date=payload.sleep_date, start_time=payload.start_time, end_time=payload.end_time, quality=payload.quality)
    return SleepOut.model_validate(log) 

@router.post("/meal", response_model=MealOut)
async def create_meal(payload: MealCreate):
    log = await MealLog.create(user_id=payload.user_id, meal_type=payload.meal_type, calories=payload.calories, note=payload.note, eaten_at=payload.eaten_at)
    return MealOut.model_validate(log)

@router.get("/exercise", response_model=ListResponse[ExerciseOut])
async def list_exercise():
    logs = await ExerciseLog.all().order_by("-logged_at")
    return {"items": [ExerciseOut.model_validate(log) for log in logs], "total": len(logs)}

@router.get("/sleep", response_model=ListResponse[SleepOut])
async def list_sleep():
    logs = await SleepLog.all().order_by("-sleep_date")
    return {"items": [SleepOut.model_validate(log) for log in logs], "total": len(logs)}

@router.get("/meal", response_model=ListResponse[MealOut])
async def list_meal():
    logs = await MealLog.all().order_by("-eaten_at")
    return {"items": [MealOut.model_validate(log) for log in logs], "total": len(logs)}    

