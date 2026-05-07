from tortoise import fields, models
# TODO: MealLog 모델을 작성해 보세요.
# 힌트: meal_type, calories, note, eaten_at 필드가 필요합니다.

class MealLog(models.Model):
    meal_type: str = fields.CharField(max_length=20)
    calories: int | None = fields.IntField(null=True)
    note: str | None = fields.CharField(max_length=200, null=True)
    eaten_at = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField("models.User", related_name="meal_logs")

    def __str__(self) -> str:
        return f"{self.meal_type} - {self.calories}kcal ({self.eaten_at.date()})"

    class Meta:
        indexes = (
            ("user_id", "eaten_at"),
        )