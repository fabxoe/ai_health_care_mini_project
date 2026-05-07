from tortoise import fields, models

class BloodPressureLog(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="blood_pressure_logs")
    measured_at = fields.DatetimeField()
    systolic = fields.IntField()        # 최고혈압
    diastolic = fields.IntField()       # 최저혈압
    mean_pressure = fields.IntField(null=True)  # 평균혈압
    pulse = fields.IntField()           # 맥박수
    heart_burden = fields.IntField(null=True)   # 심부담
    pulse_wave_pattern = fields.CharField(max_length=100, null=True)

    image_path = fields.CharField(max_length=500, null=True)  # 원본 이미지 경로

    def __str__(self) -> str:
        return f"{self.systolic}/{self.diastolic} mmHg ({self.measured_at.date()})"

    class Meta:
        indexes = (
            ("user_id", "measured_at"),
        )
