from tortoise import fields, models

class CardioLog(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="cardio_logs")
    measured_at = fields.DatetimeField()
    hospital_name = fields.CharField(max_length=100, null=True)  # 검사 기관
    cardio_age = fields.IntField(null=True)                      # 심뇌혈관 나이
    risk_ratio = fields.FloatField(null=True)                    # 발병위험 배수
    risk_percent = fields.FloatField(null=True)                  # 발병 확률 (%)
    weight = fields.FloatField(null=True)                        # 체중
    waist = fields.FloatField(null=True)                         # 허리둘레
    activity_note = fields.CharField(max_length=100, null=True)  # 신체활동
    alcohol_note = fields.CharField(max_length=100, null=True)   # 음주
    bp_systolic = fields.IntField(null=True)                     # 최고혈압
    bp_diastolic = fields.IntField(null=True)                    # 최저혈압
    smoking_status = fields.CharField(max_length=50, null=True)  # 흡연 상태
    fasting_blood_sugar = fields.IntField(null=True)             # 공복혈당
    total_cholesterol = fields.IntField(null=True)               # 총 콜레스테롤
    ldl_cholesterol = fields.IntField(null=True)                 # LDL 콜레스테롤

    image_path = fields.CharField(max_length=500, null=True)  # 원본 이미지 경로

    def __str__(self) -> str:
        return f"심뇌혈관위험평가 ({self.measured_at.date()}) - {self.hospital_name}"

    class Meta:
        indexes = (
            ("user_id", "measured_at"),
        )
