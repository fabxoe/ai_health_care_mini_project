from tortoise import fields, models

class EEGLog(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="eeg_logs")
    measured_at = fields.DatetimeField()  # 검사 일시
    eyes_condition = fields.CharField(max_length=50, null=True)  # 검사 조건 (예: Eyes Open)
    clinician = fields.CharField(max_length=100, null=True)      # 담당의/임상가
    comments = fields.CharField(max_length=200, null=True)       # 코멘트/특이사항 (예: FP1,FP2,T6,PZ)
    summary = fields.TextField(null=True)                        # 소견/요약 (예: 베타파 과활성)
    ai_interpretation = fields.TextField(null=True)              # AI 심층 분석 결과
    
    image_path = fields.CharField(max_length=500, null=True)  # 결과지 원본 이미지 경로

    def __str__(self) -> str:
        return f"정량화 뇌파(qEEG) 검사 ({self.measured_at.date()})"

    class Meta:
        indexes = (
            ("user_id", "measured_at"),
        )
