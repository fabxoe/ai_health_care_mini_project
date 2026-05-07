from tortoise import fields, models

# TODO: SleepLog 모델을 작성해 보세요.
# 힌트: sleep_date, start_time, end_time, quality 필드가 필요합니다.

class SleepLog(models.Model):
    sleep_date = fields.DateField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    quality: int | None = fields.IntField(null=True)
    user = fields.ForeignKeyField("models.User", related_name="sleep_logs")

    def __str__(self) -> str:
        return f"{self.sleep_date} {self.start_time} - {self.end_time} (품질: {self.quality})"

    class Meta:
        indexes = (
            ("user_id", "sleep_date"),
        )