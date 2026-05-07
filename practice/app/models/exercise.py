
from tortoise import fields, models
# TODO: ExerciseLog 모델을 작성해 보세요.
# 힌트: activity, duration_min, calories_burned, logged_at 필드가 필요합니다.
class ExerciseLog(models.Model):
    activity: str = fields.CharField(max_length=50)
    duration_min: int = fields.IntField()
    calories_burned: int | None = fields.IntField(null=True)
    logged_at = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField("models.User", related_name="exercise_logs")

    def __str__(self) -> str:
        return f"{self.activity} - {self.duration_min}분 ({self.logged_at.date()})"