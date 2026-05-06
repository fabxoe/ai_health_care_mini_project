from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import koreanize_matplotlib


from app.models.water import WaterLog
from app.services.mock_data import (
    add_exercise,
    add_meal,
    add_sleep,
    delete_exercise,
    delete_meal,
    delete_sleep,
    list_exercise,
    list_meal,
    list_sleep,
    update_exercise,
    update_meal,
    update_sleep,
)
from app.services.users import get_or_create_default_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def build_water_report(logs: list[WaterLog], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not logs:
        plt.figure(figsize=(7, 3.5))
        plt.text(0.5, 0.5, "데이터 없음", ha="center", va="center", fontsize=12)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=140)
        plt.close()
        return

    rows = [{"date": log.logged_at.date(), "amount_ml": log.amount_ml} for log in logs]
    df = pd.DataFrame(rows)
    daily = df.groupby("date", as_index=False)["amount_ml"].sum()

    plt.figure(figsize=(7, 3.5))
    plt.bar(daily["date"].astype(str), daily["amount_ml"], color="#6e7bff")
    plt.title("일별 수분 섭취량")
    plt.ylabel("ml")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


@router.get("/")
async def dashboard(request: Request):
    user = await get_or_create_default_user()
    water_logs = await WaterLog.filter(user=user).order_by("-logged_at").limit(5)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "water_logs": water_logs,
            "exercise_logs": list_exercise()[:5],
            "sleep_logs": list_sleep()[:5],
            "meal_logs": list_meal()[:5],
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
    return templates.TemplateResponse(
        request, "exercise.html", {"user": user, "logs": list_exercise()}
    )


@router.post("/exercise")
async def add_exercise_log(
    activity: str = Form(...),
    duration_min: int = Form(...),
    calories_burned: int | None = Form(None),
):
    # TODO: ORM 모델과 테이블로 교체하세요.
    add_exercise(activity, duration_min, calories_burned)
    return RedirectResponse(url="/exercise", status_code=303)


@router.post("/exercise/{log_id}/edit")
async def edit_exercise_log(
    log_id: int,
    activity: str = Form(...),
    duration_min: int = Form(...),
    calories_burned: int | None = Form(None),
    logged_at: str = Form(...),
):
    # TODO: ORM 모델과 테이블로 교체하세요.
    update_exercise(
        log_id, activity, duration_min, calories_burned, datetime.fromisoformat(logged_at)
    )
    return RedirectResponse(url="/exercise", status_code=303)


@router.post("/exercise/{log_id}/delete")
async def delete_exercise_log(log_id: int):
    # TODO: ORM 모델과 테이블로 교체하세요.
    delete_exercise(log_id)
    return RedirectResponse(url="/exercise", status_code=303)


@router.get("/sleep")
async def sleep_page(request: Request):
    user = await get_or_create_default_user()
    return templates.TemplateResponse(
        request, "sleep.html", {"user": user, "logs": list_sleep()}
    )


@router.post("/sleep")
async def add_sleep_log(
    sleep_date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    quality: int | None = Form(None),
):
    # TODO: ORM 모델과 테이블로 교체하세요.
    add_sleep(
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
    # TODO: ORM 모델과 테이블로 교체하세요.
    update_sleep(
        log_id=log_id,
        sleep_date=date.fromisoformat(sleep_date),
        start_time=datetime.fromisoformat(start_time),
        end_time=datetime.fromisoformat(end_time),
        quality=quality,
    )
    return RedirectResponse(url="/sleep", status_code=303)


@router.post("/sleep/{log_id}/delete")
async def delete_sleep_log(log_id: int):
    # TODO: ORM 모델과 테이블로 교체하세요.
    delete_sleep(log_id)
    return RedirectResponse(url="/sleep", status_code=303)


@router.get("/meal")
async def meal_page(request: Request):
    user = await get_or_create_default_user()
    return templates.TemplateResponse(
        request, "meal.html", {"user": user, "logs": list_meal()}
    )


@router.post("/meal")
async def add_meal_log(
    meal_type: str = Form(...),
    calories: int | None = Form(None),
    note: str | None = Form(None),
):
    # TODO: ORM 모델과 테이블로 교체하세요.
    add_meal(meal_type, calories, note)
    return RedirectResponse(url="/meal", status_code=303)


@router.post("/meal/{log_id}/edit")
async def edit_meal_log(
    log_id: int,
    meal_type: str = Form(...),
    calories: int | None = Form(None),
    note: str | None = Form(None),
    eaten_at: str = Form(...),
):
    # TODO: ORM 모델과 테이블로 교체하세요.
    update_meal(log_id, meal_type, calories, note, datetime.fromisoformat(eaten_at))
    return RedirectResponse(url="/meal", status_code=303)


@router.post("/meal/{log_id}/delete")
async def delete_meal_log(log_id: int):
    # TODO: ORM 모델과 테이블로 교체하세요.
    delete_meal(log_id)
    return RedirectResponse(url="/meal", status_code=303)


@router.get("/report")
async def report_page(request: Request):
    user = await get_or_create_default_user()
    logs = await WaterLog.filter(user=user).order_by("logged_at")
    output_path = Path("app/static/img/water_report.png")
    build_water_report(logs, output_path)
    total_water = sum(log.amount_ml for log in logs)
    days = len({log.logged_at.date() for log in logs})
    avg_per_day = round(total_water / days, 1) if days else 0

    return templates.TemplateResponse(
        request,
        "report.html",
        {
            "user": user,
            "chart_url": "/static/img/water_report.png",
            "total_water": total_water,
            "days": days,
            "avg_per_day": avg_per_day,
        },
    )
