from tortoise import fields, models

class VisionLog(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="vision_logs")
    measured_at = fields.DatetimeField()
    hospital_name = fields.CharField(max_length=100, null=True)  # 안과/안경원 이름
    
    sph_right = fields.FloatField(null=True)  # 구면도수(SPH) R
    sph_left = fields.FloatField(null=True)   # 구면도수(SPH) L
    cyl_right = fields.FloatField(null=True)  # 원주도수(CYL) R
    cyl_left = fields.FloatField(null=True)   # 원주도수(CYL) L
    axis_right = fields.IntField(null=True)   # 난시축(AX) R
    axis_left = fields.IntField(null=True)    # 난시축(AX) L
    pd = fields.FloatField(null=True)         # 동공간 거리(P.D)
    
    image_path = fields.CharField(max_length=500, null=True)  # 원본 이미지 경로

    def __str__(self) -> str:
        return f"시력 처방 ({self.measured_at.date()})"

    class Meta:
        indexes = (
            ("user_id", "measured_at"),
        )
