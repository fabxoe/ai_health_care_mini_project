from tortoise import fields, models

class CheckupLog(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="checkup_logs")
    measured_at = fields.DateField()
    hospital_name = fields.CharField(max_length=100, null=True)
    
    # Obesity
    weight = fields.FloatField(null=True)
    bmi = fields.FloatField(null=True)
    waist = fields.FloatField(null=True)
    
    # Blood Pressure
    bp_systolic = fields.IntField(null=True)
    bp_diastolic = fields.IntField(null=True)
    
    # Key Lab Values
    blood_glucose = fields.IntField(null=True) # 공복혈당
    hemoglobin = fields.FloatField(null=True) # 혈색소
    
    # Lipids
    total_cholesterol = fields.IntField(null=True)
    hdl_cholesterol = fields.IntField(null=True)
    triglycerides = fields.IntField(null=True)
    ldl_cholesterol = fields.IntField(null=True)
    
    ast = fields.IntField(null=True) # 간기능
    alt = fields.IntField(null=True)
    y_gtp = fields.IntField(null=True)
    
    creatinine = fields.FloatField(null=True) # 신장
    e_gfr = fields.IntField(null=True) # 신사구체여과율
    
    # General
    summary = fields.TextField(null=True) # 종합소견
    judgment = fields.CharField(max_length=50, null=True) # 판정 (정상A, 정상B 등)
    
    image_path = fields.CharField(max_length=255, null=True) # Keep for backward compatibility or as 'main' image
    created_at = fields.DatetimeField(auto_now_add=True)

    images: fields.ReverseRelation["CheckupImage"]

    class Meta:
        table = "checkup_logs"
        ordering = ["-measured_at"]

class CheckupImage(models.Model):
    id = fields.IntField(pk=True)
    checkup = fields.ForeignKeyField("models.CheckupLog", related_name="images")
    image_path = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "checkup_images"
