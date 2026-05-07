from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


from typing import TypeIs

# [Python 3.13+] 더 완벽한 타입 좁히기 (PEP 742: TypeIs)
# 기존 TypeGuard는 if문 밖(else)에서는 원래 타입이 그대로 남는 한계가 있었으나, 
# TypeIs는 else 블록에서 int가 아님이 완벽하게 추론됩니다.
def is_valid_amount(val: int | str) -> TypeIs[int]:
    return isinstance(val, int)

class WaterCreate(BaseModel):
    user_id: int
    amount_ml: int

    # [Python 3.14/3.15] 타입 힌트 지연 평가 기본 탑재 (PEP 649)
    # 과거에는 클래스 내부에서 자기 자신의 타입을 반환할 때 에러가 나서 문자열("WaterCreate")을 쓰거나
    # 파일 최상단에 `from __future__ import annotations`를 붙여야 했지만,
    # 3.14+ 부터는 지연 평가가 기본화되어 네이티브하게 상호 참조 및 자기 참조가 가능합니다.
    def clone_with_bonus(self, bonus_ml: int) -> WaterCreate:
        return WaterCreate(user_id=self.user_id, amount_ml=self.amount_ml + bonus_ml)

# [Python 3.12+] 새로운 타입 별칭(Type Alias) 문법 (PEP 695)
# 더 이상 `from typing import TypeAlias`를 쓰지 않고 직관적으로 선언합니다.
type ModelID = int

# [Python 3.12+] 제네릭 문법 (PEP 695)
# `T = TypeVar('T')`나 `Generic[T]` 상속 없이, 클래스명 바로 뒤에 `[T]`를 붙입니다.
class ListResponse[T](BaseModel):
    items: list[T]
    total: int
    
    model_config = ConfigDict(from_attributes=True)


class WaterOut(BaseModel):
    id: ModelID
    user_id: int
    amount_ml: int
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseCreate(BaseModel):
    user_id: int
    activity: str
    duration_min: int
    calories_burned: int | None = None


class ExerciseOut(BaseModel):
    id: ModelID
    user_id: int
    activity: str
    duration_min: int
    calories_burned: int | None
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SleepCreate(BaseModel):
    user_id: int
    sleep_date: date
    start_time: datetime
    end_time: datetime
    quality: int | None = None


class SleepOut(BaseModel):
    id: ModelID
    user_id: int
    sleep_date: date
    start_time: datetime
    end_time: datetime
    quality: int | None

    model_config = ConfigDict(from_attributes=True)


class MealCreate(BaseModel):
    user_id: int
    meal_type: str
    calories: int | None = None
    note: str | None = None


class MealOut(BaseModel):
    id: ModelID
    user_id: int
    meal_type: str
    calories: int | None
    note: str | None
    eaten_at: datetime

    model_config = ConfigDict(from_attributes=True)
