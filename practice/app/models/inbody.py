from tortoise import fields, models

class InBodyLog(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="inbody_logs")
    measured_at = fields.DatetimeField()
    weight = fields.FloatField()                 # 체중 (kg)
    skeletal_muscle_mass = fields.FloatField()   # 골격근량 (kg)
    body_fat_mass = fields.FloatField()          # 체지방량 (kg)
    bmi = fields.FloatField()                    # BMI
    percent_body_fat = fields.FloatField()       # 체지방률 (%)
    inbody_score = fields.IntField()             # 인바디 점수

    image_path = fields.CharField(max_length=500, null=True)  # 원본 이미지 경로

    def __str__(self) -> str:
        return f"InBody {self.inbody_score}점 ({self.measured_at.date()})"

    class Meta:
        indexes = (
            ("user_id", "measured_at"),
        )
