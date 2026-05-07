import os
import shutil
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path

from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import plotly.express as px

from app.models.exercise import ExerciseLog #
from app.models.meal import MealLog #
from app.models.sleep import SleepLog #
from app.models.water import WaterLog
from app.models.blood_pressure import BloodPressureLog
from app.models.inbody import InBodyLog
from app.models.cardio import CardioLog
from app.models.vision import VisionLog
from app.models.vaccine import VaccineLog
from app.models.eeg import EEGLog
from app.models.checkup import CheckupLog, CheckupImage
from app.services.users import get_or_create_default_user

router = APIRouter()

async def save_upload_file(image: UploadFile | None) -> str | None:
    if not image or not image.filename:
        return None
    upload_dir = "app/static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return f"/static/uploads/{filename}"

def delete_upload_file(image_path: str | None):
    if image_path:
        file_path = os.path.join("app", image_path.lstrip("/"))
        if os.path.exists(file_path):
            os.remove(file_path)
templates = Jinja2Templates(directory="app/templates")

def build_water_chart(logs: list[WaterLog]) -> str | None:
    if not logs: return None
    rows = [{"date": log.logged_at.date(), "amount_ml": log.amount_ml} for log in logs]
    df = pd.DataFrame(rows)
    daily = df.groupby("date", as_index=False)["amount_ml"].sum()
    
    fig = px.bar(daily, x="date", y="amount_ml", title="일별 수분 섭취량 (ml)", template="plotly_dark", color_discrete_sequence=["#8c95ff"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=20, l=20, r=20))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def build_exercise_chart(logs: list[ExerciseLog]) -> str | None:
    if not logs: return None
    rows = [{"date": log.logged_at.date(), "duration_min": log.duration_min, "activity": log.activity} for log in logs]
    df = pd.DataFrame(rows)
    daily = df.groupby(["date", "activity"], as_index=False)["duration_min"].sum()
    
    fig = px.bar(daily, x="date", y="duration_min", color="activity", title="일별 운동 시간 (분)", template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=20, l=20, r=20), barmode="stack")
    return fig.to_html(full_html=False, include_plotlyjs=False)

def build_sleep_chart(logs: list[SleepLog]) -> str | None:
    if not logs: return None
    rows = [{"date": log.sleep_date, "quality": log.quality or 0} for log in logs]
    df = pd.DataFrame(rows)
    
    fig = px.line(df, x="date", y="quality", title="일별 수면 품질 변화 (1~5)", markers=True, template="plotly_dark", color_discrete_sequence=["#29cdb5"])
    fig.update_yaxes(range=[0, 5.5])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=20, l=20, r=20))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def build_inbody_chart(logs: list[InBodyLog]) -> str | None:
    if not logs: return None
    rows = []
    for log in logs:
        rows.append({"date": log.measured_at, "value": log.weight, "metric": "체중 (kg)"})
        rows.append({"date": log.measured_at, "value": log.skeletal_muscle_mass, "metric": "골격근량 (kg)"})
        rows.append({"date": log.measured_at, "value": log.percent_body_fat, "metric": "체지방률 (%)"})
    
    df = pd.DataFrame(rows).sort_values("date")
    
    fig = px.line(df, x="date", y="value", color="metric", title="", markers=True, template="plotly_dark", 
                  color_discrete_sequence=["#ffb347", "#8c95ff", "#29cdb5"])
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)

def build_cardio_chart(logs: list[CardioLog]) -> str | None:
    if not logs: return None
    rows = [{"date": log.measured_at, "cardio_age": log.cardio_age} for log in logs if log.cardio_age is not None]
    if not rows: return None
    df = pd.DataFrame(rows).sort_values("date")
    
    fig = px.line(df, x="date", y="cardio_age", title="심뇌혈관 나이 변화 추이", markers=True, template="plotly_dark", color_discrete_sequence=["#ff6b6b"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=20, l=20, r=20))
    return fig.to_html(full_html=False, include_plotlyjs=False)


@router.get("/")
async def dashboard(request: Request):
    user = await get_or_create_default_user()
    water_logs = await WaterLog.filter(user=user).order_by("-logged_at").limit(5)
    exercise_logs = await ExerciseLog.filter(user=user).order_by("-logged_at").limit(5)
    meal_logs = await MealLog.filter(user=user).order_by("-eaten_at").limit(5)
    sleep_logs = await SleepLog.filter(user=user).order_by("-sleep_date").limit(5)   

    total_water = sum([log.amount_ml for log in await WaterLog.filter(user=user)])
    total_exercise = sum([log.duration_min for log in await ExerciseLog.filter(user=user)])

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "water_logs": water_logs,   
            "exercise_logs": exercise_logs,
            "sleep_logs": sleep_logs,
            "meal_logs": meal_logs,
            "total_water": total_water,
            "total_exercise": total_exercise,
            # "total_sleep": total_sleep,
            # "total_meal": total_meal,  
        },
    )


@router.get("/water")
async def water_page(request: Request):
    user = await get_or_create_default_user()
    logs = await WaterLog.filter(user=user).order_by("-logged_at")
    return templates.TemplateResponse(
        request, "water.html", {"user": user, "logs": logs}
    )


@router.post("/water")
async def add_water(amount_ml: int = Form(...)):
    user = await get_or_create_default_user()
    await WaterLog.create(user=user, amount_ml=amount_ml)
    return RedirectResponse(url="/water", status_code=303)


@router.post("/water/{log_id}/edit")
async def edit_water(
    log_id: int, amount_ml: int = Form(...), logged_at: str = Form(...)
):
    user = await get_or_create_default_user()
    log = await WaterLog.get_or_none(id=log_id, user=user)
    if log:
        log.amount_ml = amount_ml
        log.logged_at = datetime.fromisoformat(logged_at)
        await log.save(update_fields=["amount_ml", "logged_at"])
    return RedirectResponse(url="/water", status_code=303)


@router.post("/water/{log_id}/delete")
async def delete_water(log_id: int):
    user = await get_or_create_default_user()
    log = await WaterLog.get_or_none(id=log_id, user=user)
    if log:
        await log.delete()
    return RedirectResponse(url="/water", status_code=303)


@router.get("/exercise")
async def exercise_page(request: Request):
    user = await get_or_create_default_user()
    logs = await ExerciseLog.filter(user=user).order_by("-logged_at")
    return templates.TemplateResponse(
        request, "exercise.html", {"user": user, "logs": logs}
    )


@router.post("/exercise")
async def add_exercise_log(
    activity: str = Form(...),
    duration_min: int = Form(...),
    calories_burned: int | None = Form(None),
):
    user = await get_or_create_default_user()
    await ExerciseLog.create(
        user=user, activity=activity, duration_min=duration_min, calories_burned=calories_burned
    )
    return RedirectResponse(url="/exercise", status_code=303)


@router.post("/exercise/{log_id}/edit")
async def edit_exercise_log(
    log_id: int,
    activity: str = Form(...),
    duration_min: int = Form(...),
    calories_burned: int | None = Form(None),
    logged_at: str = Form(...),
):
    user = await get_or_create_default_user()
    log = await ExerciseLog.get_or_none(id=log_id, user=user)
    if log:
        log.activity = activity
        log.duration_min = duration_min
        log.calories_burned = calories_burned
        log.logged_at = datetime.fromisoformat(logged_at)
        await log.save(update_fields=["activity", "duration_min", "calories_burned", "logged_at"])
    return RedirectResponse(url="/exercise", status_code=303)


@router.post("/exercise/{log_id}/delete")
async def delete_exercise_log(log_id: int):
    user = await get_or_create_default_user()
    log = await ExerciseLog.get_or_none(id=log_id, user=user)
    if log:
        await log.delete()
    return RedirectResponse(url="/exercise", status_code=303)


@router.get("/sleep")
async def sleep_page(request: Request):
    user = await get_or_create_default_user()
    logs = await SleepLog.filter(user=user).order_by("-sleep_date")
    return templates.TemplateResponse(
        request, "sleep.html", {"user": user, "logs": logs}
    )


@router.post("/sleep")
async def add_sleep(
    sleep_date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    quality: int | None = Form(None),
):
    user = await get_or_create_default_user()
    await SleepLog.create(
        user=user,
        sleep_date=date.fromisoformat(sleep_date),
        start_time=datetime.fromisoformat(start_time),
        end_time=datetime.fromisoformat(end_time),
        quality=quality,
    )
    return RedirectResponse(url="/sleep", status_code=303)


@router.post("/sleep/{log_id}/edit")
async def edit_sleep_log(
    log_id: int,
    sleep_date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    quality: int | None = Form(None),
):
    user = await get_or_create_default_user()
    log = await SleepLog.get_or_none(id=log_id, user=user)
    if log:
        log.sleep_date = date.fromisoformat(sleep_date)
        log.start_time = datetime.fromisoformat(start_time)
        log.end_time = datetime.fromisoformat(end_time)
        log.quality = quality
        await log.save(update_fields=["sleep_date", "start_time", "end_time", "quality"])
    return RedirectResponse(url="/sleep", status_code=303)


@router.post("/sleep/{log_id}/delete")
async def delete_sleep_log(log_id: int):
    user = await get_or_create_default_user()
    log = await SleepLog.get_or_none(id=log_id, user=user)
    if log:
        await log.delete()
    return RedirectResponse(url="/sleep", status_code=303)


@router.get("/meal")
async def meal_page(request: Request):
    user = await get_or_create_default_user()
    logs = await MealLog.filter(user=user).order_by("-eaten_at")
    return templates.TemplateResponse(
        request, "meal.html", {"user": user, "logs": logs}
    )


@router.post("/meal")
async def add_meal(
    meal_type: str = Form(...),
    calories: int | None = Form(None),
    note: str | None = Form(None),
):
    user = await get_or_create_default_user()
    await MealLog.create(user=user, meal_type=meal_type, calories=calories, note=note)
    return RedirectResponse(url="/meal", status_code=303)


@router.post("/meal/{log_id}/edit")
async def edit_meal_log(
    log_id: int,
    meal_type: str = Form(...),
    calories: int | None = Form(None),
    note: str | None = Form(None),
    eaten_at: str = Form(...),
):
    user = await get_or_create_default_user()
    log = await MealLog.get_or_none(id=log_id, user=user)
    if log:
        log.meal_type = meal_type
        log.calories = calories
        log.note = note
        log.eaten_at = datetime.fromisoformat(eaten_at)
        await log.save(update_fields=["meal_type", "calories", "note", "eaten_at"])
    return RedirectResponse(url="/meal", status_code=303)


@router.post("/meal/{log_id}/delete")
async def delete_meal(log_id: int):
    user = await get_or_create_default_user()
    log = await MealLog.get_or_none(id=log_id, user=user)
    if log:
        await log.delete()
    return RedirectResponse(url="/meal", status_code=303)


@router.get("/blood-pressure")
async def blood_pressure_page(request: Request):
    user = await get_or_create_default_user()
    logs = await BloodPressureLog.filter(user=user).order_by("-measured_at")
    return templates.TemplateResponse(
        request, "blood_pressure.html", {"user": user, "logs": logs}
    )


@router.post("/blood-pressure")
async def add_blood_pressure(
    measured_at: str = Form(...),
    systolic: int = Form(...),
    diastolic: int = Form(...),
    mean_pressure: int | None = Form(None),
    pulse: int = Form(...),
    heart_burden: int | None = Form(None),
    pulse_wave_pattern: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    user = await get_or_create_default_user()
    image_path = await save_upload_file(image)
    
    await BloodPressureLog.create(
        user=user,
        measured_at=datetime.fromisoformat(measured_at),
        systolic=systolic,
        diastolic=diastolic,
        mean_pressure=mean_pressure,
        pulse=pulse,
        heart_burden=heart_burden,
        pulse_wave_pattern=pulse_wave_pattern,
        image_path=image_path
    )
    return RedirectResponse(url="/blood-pressure", status_code=303)


@router.post("/blood-pressure/{log_id}/edit")
async def edit_blood_pressure(
    log_id: int,
    measured_at: str = Form(...),
    systolic: int = Form(...),
    diastolic: int = Form(...),
    mean_pressure: int | None = Form(None),
    pulse: int = Form(...),
    heart_burden: int | None = Form(None),
    pulse_wave_pattern: str | None = Form(None),
):
    user = await get_or_create_default_user()
    log = await BloodPressureLog.get_or_none(id=log_id, user=user)
    if log:
        log.measured_at = datetime.fromisoformat(measured_at)
        log.systolic = systolic
        log.diastolic = diastolic
        log.mean_pressure = mean_pressure
        log.pulse = pulse
        log.heart_burden = heart_burden
        log.pulse_wave_pattern = pulse_wave_pattern
        await log.save(update_fields=[
            "measured_at", "systolic", "diastolic", "mean_pressure", 
            "pulse", "heart_burden", "pulse_wave_pattern"
        ])
    return RedirectResponse(url="/blood-pressure", status_code=303)


@router.post("/blood-pressure/{log_id}/delete")
async def delete_blood_pressure(log_id: int):
    user = await get_or_create_default_user()
    log = await BloodPressureLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/blood-pressure", status_code=303)


@router.post("/blood-pressure/{log_id}/upload-image")
async def upload_blood_pressure_image(log_id: int, image: UploadFile = File(...)):
    user = await get_or_create_default_user()
    log = await BloodPressureLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        log.image_path = await save_upload_file(image)
        await log.save()
    return RedirectResponse(url="/blood-pressure", status_code=303)


@router.get("/inbody")
async def inbody_page(request: Request):
    user = await get_or_create_default_user()
    logs = await InBodyLog.filter(user=user).order_by("measured_at")
    
    chart_html = build_inbody_chart(logs)
    
    # Reverse logs for displaying latest first in the list
    logs_reversed = list(reversed(logs))
    
    return templates.TemplateResponse(
        request, "inbody.html", {"user": user, "logs": logs_reversed, "chart_html": chart_html}
    )


@router.post("/inbody")
async def add_inbody(
    measured_at: str = Form(...),
    weight: float = Form(...),
    skeletal_muscle_mass: float = Form(...),
    body_fat_mass: float = Form(...),
    bmi: float = Form(...),
    percent_body_fat: float = Form(...),
    inbody_score: int = Form(...),
    image: UploadFile | None = File(None),
):
    user = await get_or_create_default_user()
    image_path = await save_upload_file(image)
    
    await InBodyLog.create(
        user=user,
        measured_at=datetime.fromisoformat(measured_at),
        weight=weight,
        skeletal_muscle_mass=skeletal_muscle_mass,
        body_fat_mass=body_fat_mass,
        bmi=bmi,
        percent_body_fat=percent_body_fat,
        inbody_score=inbody_score,
        image_path=image_path
    )
    return RedirectResponse(url="/inbody", status_code=303)


@router.post("/inbody/{log_id}/delete")
async def delete_inbody(log_id: int):
    user = await get_or_create_default_user()
    log = await InBodyLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/inbody", status_code=303)


@router.post("/inbody/{log_id}/upload-image")
async def upload_inbody_image(log_id: int, image: UploadFile = File(...)):
    user = await get_or_create_default_user()
    log = await InBodyLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        log.image_path = await save_upload_file(image)
        await log.save()
    return RedirectResponse(url="/inbody", status_code=303)


@router.get("/cardio")
async def cardio_page(request: Request):
    user = await get_or_create_default_user()
    logs = await CardioLog.filter(user=user).order_by("measured_at")
    chart_html = build_cardio_chart(logs)
    return templates.TemplateResponse(
        request, "cardio.html", {"user": user, "logs": list(reversed(logs)), "chart_html": chart_html}
    )


@router.post("/cardio")
async def add_cardio(
    measured_at: str = Form(...),
    hospital_name: str | None = Form(None),
    cardio_age: int | None = Form(None),
    risk_ratio: float | None = Form(None),
    risk_percent: float | None = Form(None),
    weight: float | None = Form(None),
    waist: float | None = Form(None),
    activity_note: str | None = Form(None),
    alcohol_note: str | None = Form(None),
    bp_systolic: int | None = Form(None),
    bp_diastolic: int | None = Form(None),
    smoking_status: str | None = Form(None),
    fasting_blood_sugar: int | None = Form(None),
    total_cholesterol: int | None = Form(None),
    ldl_cholesterol: int | None = Form(None),
    image: UploadFile | None = File(None),
):
    user = await get_or_create_default_user()
    image_path = await save_upload_file(image)
    
    await CardioLog.create(
        user=user,
        measured_at=datetime.fromisoformat(measured_at),
        hospital_name=hospital_name,
        cardio_age=cardio_age,
        risk_ratio=risk_ratio,
        risk_percent=risk_percent,
        weight=weight,
        waist=waist,
        activity_note=activity_note,
        alcohol_note=alcohol_note,
        bp_systolic=bp_systolic,
        bp_diastolic=bp_diastolic,
        smoking_status=smoking_status,
        fasting_blood_sugar=fasting_blood_sugar,
        total_cholesterol=total_cholesterol,
        ldl_cholesterol=ldl_cholesterol,
        image_path=image_path
    )
    return RedirectResponse(url="/cardio", status_code=303)


@router.post("/cardio/{log_id}/edit")
async def edit_cardio(
    log_id: int,
    measured_at: str = Form(...),
    hospital_name: str | None = Form(None),
    cardio_age: int | None = Form(None),
    risk_ratio: float | None = Form(None),
    risk_percent: float | None = Form(None),
    weight: float | None = Form(None),
    waist: float | None = Form(None),
    activity_note: str | None = Form(None),
    alcohol_note: str | None = Form(None),
    bp_systolic: int | None = Form(None),
    bp_diastolic: int | None = Form(None),
    smoking_status: str | None = Form(None),
    fasting_blood_sugar: int | None = Form(None),
    total_cholesterol: int | None = Form(None),
    ldl_cholesterol: int | None = Form(None),
):
    user = await get_or_create_default_user()
    log = await CardioLog.get_or_none(id=log_id, user=user)
    if log:
        log.measured_at = datetime.fromisoformat(measured_at)
        log.hospital_name = hospital_name
        log.cardio_age = cardio_age
        log.risk_ratio = risk_ratio
        log.risk_percent = risk_percent
        log.weight = weight
        log.waist = waist
        log.activity_note = activity_note
        log.alcohol_note = alcohol_note
        log.bp_systolic = bp_systolic
        log.bp_diastolic = bp_diastolic
        log.smoking_status = smoking_status
        log.fasting_blood_sugar = fasting_blood_sugar
        log.total_cholesterol = total_cholesterol
        log.ldl_cholesterol = ldl_cholesterol
        await log.save(update_fields=[
            "measured_at", "hospital_name", "cardio_age", "risk_ratio", "risk_percent",
            "weight", "waist", "activity_note", "alcohol_note", "bp_systolic",
            "bp_diastolic", "smoking_status", "fasting_blood_sugar",
            "total_cholesterol", "ldl_cholesterol"
        ])
    return RedirectResponse(url="/cardio", status_code=303)


@router.post("/cardio/{log_id}/delete")
async def delete_cardio(log_id: int):
    user = await get_or_create_default_user()
    log = await CardioLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/cardio", status_code=303)


@router.post("/cardio/{log_id}/upload-image")
async def upload_cardio_image(log_id: int, image: UploadFile = File(...)):
    user = await get_or_create_default_user()
    log = await CardioLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        log.image_path = await save_upload_file(image)
        await log.save()
    return RedirectResponse(url="/cardio", status_code=303)


@router.get("/vision")
async def vision_page(request: Request):
    user = await get_or_create_default_user()
    logs = await VisionLog.filter(user=user).order_by("-measured_at")
    return templates.TemplateResponse(
        request, "vision.html", {"user": user, "logs": logs}
    )


@router.post("/vision")
async def add_vision(
    measured_at: str = Form(...),
    hospital_name: str | None = Form(None),
    sph_right: float | None = Form(None),
    sph_left: float | None = Form(None),
    cyl_right: float | None = Form(None),
    cyl_left: float | None = Form(None),
    axis_right: int | None = Form(None),
    axis_left: int | None = Form(None),
    pd: float | None = Form(None),
    image: UploadFile | None = File(None),
):
    user = await get_or_create_default_user()
    image_path = await save_upload_file(image)

    await VisionLog.create(
        user=user,
        measured_at=datetime.fromisoformat(measured_at),
        hospital_name=hospital_name,
        sph_right=sph_right,
        sph_left=sph_left,
        cyl_right=cyl_right,
        cyl_left=cyl_left,
        axis_right=axis_right,
        axis_left=axis_left,
        pd=pd,
        image_path=image_path
    )
    return RedirectResponse(url="/vision", status_code=303)


@router.post("/vision/{log_id}/delete")
async def delete_vision(log_id: int):
    user = await get_or_create_default_user()
    log = await VisionLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/vision", status_code=303)


@router.post("/vision/{log_id}/upload-image")
async def upload_vision_image(log_id: int, image: UploadFile = File(...)):
    user = await get_or_create_default_user()
    log = await VisionLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        log.image_path = await save_upload_file(image)
        await log.save()
    return RedirectResponse(url="/vision", status_code=303)


@router.get("/vaccine")
async def vaccine_page(request: Request):
    user = await get_or_create_default_user()
    logs = await VaccineLog.filter(user=user).order_by("-measured_at")
    return templates.TemplateResponse(
        request, "vaccine.html", {"user": user, "logs": logs}
    )


@router.post("/vaccine")
async def add_vaccine(
    measured_at: str = Form(...),
    vaccine_name: str = Form(...),
    dose_number: str = Form(...),
    hospital_name: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    user = await get_or_create_default_user()
    image_path = await save_upload_file(image)

    await VaccineLog.create(
        user=user,
        measured_at=datetime.fromisoformat(measured_at),
        vaccine_name=vaccine_name,
        dose_number=dose_number,
        hospital_name=hospital_name,
        image_path=image_path
    )
    return RedirectResponse(url="/vaccine", status_code=303)


@router.post("/vaccine/{log_id}/delete")
async def delete_vaccine(log_id: int):
    user = await get_or_create_default_user()
    log = await VaccineLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/vaccine", status_code=303)


@router.post("/vaccine/{log_id}/upload-image")
async def upload_vaccine_image(log_id: int, image: UploadFile = File(...)):
    user = await get_or_create_default_user()
    log = await VaccineLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        log.image_path = await save_upload_file(image)
        await log.save()
    return RedirectResponse(url="/vaccine", status_code=303)


@router.get("/eeg")
async def eeg_page(request: Request):
    user = await get_or_create_default_user()
    logs = await EEGLog.filter(user=user).order_by("-measured_at")
    return templates.TemplateResponse(
        request, "eeg.html", {"user": user, "logs": logs}
    )


@router.post("/eeg")
async def add_eeg(
    measured_at: str = Form(...),
    eyes_condition: str | None = Form(None),
    clinician: str | None = Form(None),
    comments: str | None = Form(None),
    summary: str | None = Form(None),
    ai_interpretation: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    user = await get_or_create_default_user()
    image_path = await save_upload_file(image)

    await EEGLog.create(
        user=user,
        measured_at=datetime.fromisoformat(measured_at),
        eyes_condition=eyes_condition,
        clinician=clinician,
        comments=comments,
        summary=summary,
        ai_interpretation=ai_interpretation,
        image_path=image_path
    )
    return RedirectResponse(url="/eeg", status_code=303)


@router.post("/eeg/{log_id}/delete")
async def delete_eeg(log_id: int):
    user = await get_or_create_default_user()
    log = await EEGLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/eeg", status_code=303)


@router.post("/eeg/{log_id}/upload-image")
async def upload_eeg_image(log_id: int, image: UploadFile = File(...)):
    user = await get_or_create_default_user()
    log = await EEGLog.get_or_none(id=log_id, user=user)
    if log:
        delete_upload_file(log.image_path)
        log.image_path = await save_upload_file(image)
        await log.save()
    return RedirectResponse(url="/eeg", status_code=303)


@router.get("/checkup")
async def checkup_page(request: Request):
    user = await get_or_create_default_user()
    logs = await CheckupLog.filter(user=user).prefetch_related("images").order_by("-measured_at")
    return templates.TemplateResponse(
        request, "checkup.html", {
            "user": user, 
            "logs": logs,
            "now_date": date.today().isoformat()
        }
    )


@router.post("/checkup")
async def add_checkup(
    measured_at: str = Form(...),
    hospital_name: str | None = Form(None),
    weight: float | None = Form(None),
    bmi: float | None = Form(None),
    waist: float | None = Form(None),
    bp_systolic: int | None = Form(None),
    bp_diastolic: int | None = Form(None),
    blood_glucose: int | None = Form(None),
    hemoglobin: float | None = Form(None),
    total_cholesterol: int | None = Form(None),
    hdl_cholesterol: int | None = Form(None),
    triglycerides: int | None = Form(None),
    ldl_cholesterol: int | None = Form(None),
    ast: int | None = Form(None),
    alt: int | None = Form(None),
    y_gtp: int | None = Form(None),
    creatinine: float | None = Form(None),
    e_gfr: int | None = Form(None),
    summary: str | None = Form(None),
    judgment: str | None = Form(None),
    images: list[UploadFile] | None = File(None),
):
    user = await get_or_create_default_user()
    
    log = await CheckupLog.create(
        user=user,
        measured_at=date.fromisoformat(measured_at),
        hospital_name=hospital_name,
        weight=weight,
        bmi=bmi,
        waist=waist,
        bp_systolic=bp_systolic,
        bp_diastolic=bp_diastolic,
        blood_glucose=blood_glucose,
        hemoglobin=hemoglobin,
        total_cholesterol=total_cholesterol,
        hdl_cholesterol=hdl_cholesterol,
        triglycerides=triglycerides,
        ldl_cholesterol=ldl_cholesterol,
        ast=ast,
        alt=alt,
        y_gtp=y_gtp,
        creatinine=creatinine,
        e_gfr=e_gfr,
        summary=summary,
        judgment=judgment
    )

    if images:
        for image in images:
            if image.filename:
                image_path = await save_upload_file(image)
                await CheckupImage.create(checkup=log, image_path=image_path)
    
    return RedirectResponse(url="/checkup", status_code=303)


@router.post("/checkup/{log_id}/delete")
async def delete_checkup(log_id: int):
    user = await get_or_create_default_user()
    log = await CheckupLog.get_or_none(id=log_id, user=user).prefetch_related("images")
    if log:
        for img in log.images:
            delete_upload_file(img.image_path)
        delete_upload_file(log.image_path)
        await log.delete()
    return RedirectResponse(url="/checkup", status_code=303)


@router.post("/checkup/{log_id}/upload-image")
async def upload_checkup_image(log_id: int, images: list[UploadFile] = File(...)):
    user = await get_or_create_default_user()
    log = await CheckupLog.get_or_none(id=log_id, user=user)
    if log:
        for image in images:
            if image.filename:
                image_path = await save_upload_file(image)
                await CheckupImage.create(checkup=log, image_path=image_path)
    return RedirectResponse(url="/checkup", status_code=303)


@router.get("/report")
async def report_page(request: Request):
    user = await get_or_create_default_user()
    
    water_logs = await WaterLog.filter(user=user).order_by("logged_at")
    exercise_logs = await ExerciseLog.filter(user=user).order_by("logged_at")
    sleep_logs = await SleepLog.filter(user=user).order_by("sleep_date")
    
    water_chart = build_water_chart(water_logs)
    exercise_chart = build_exercise_chart(exercise_logs)
    sleep_chart = build_sleep_chart(sleep_logs)
    
    total_water = sum(log.amount_ml for log in water_logs)
    days = len({log.logged_at.date() for log in water_logs})
    avg_per_day = round(total_water / days, 1) if days else 0

    return templates.TemplateResponse(
        request,
        "report.html",
        {
            "user": user,
            "water_chart": water_chart,
            "exercise_chart": exercise_chart,
            "sleep_chart": sleep_chart,
            "total_water": total_water,
            "days": days,
            "avg_per_day": avg_per_day,
        },
    )
