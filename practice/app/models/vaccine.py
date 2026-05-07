from tortoise import fields, models

class VaccineLog(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="vaccine_logs")
    measured_at = fields.DatetimeField()  # 접종일
    vaccine_name = fields.CharField(max_length=100)  # 백신명 (예: 코로나19(모더나))
    dose_number = fields.CharField(max_length=50)    # 접종 차수 (예: 1차)
    hospital_name = fields.CharField(max_length=100, null=True)  # 접종기관
    
    image_path = fields.CharField(max_length=500, null=True)  # 원본 증명서 이미지 경로

    def __str__(self) -> str:
        return f"{self.vaccine_name} {self.dose_number} ({self.measured_at.date()})"

    class Meta:
        indexes = (
            ("user_id", "measured_at"),
        )
