from django.contrib import admin
from .models import (
    Semester,
    Student,
    Course,
    ProgramOutcome,
    LearningOutcome,
    OutcomeMapping,
    Assessment,
    AssessmentWeight,
    StudentScore,
    Enrollment,  # <-- Import'a eklendi
)

# Temel Modeller
admin.site.register(Semester)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(ProgramOutcome)
admin.site.register(Enrollment)  # <-- BURAYA EKLENDİ (Önemli!)


# LO Yönetimi (İçinde Mapping ile beraber)
class OutcomeMappingInline(admin.TabularInline):
    model = OutcomeMapping
    extra = 1


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    inlines = [OutcomeMappingInline]
    list_display = ("code", "course", "description")


# Sınav Yönetimi (İçinde Ağırlıklarla beraber)
class AssessmentWeightInline(admin.TabularInline):
    model = AssessmentWeight
    extra = 1


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    inlines = [AssessmentWeightInline]
    list_display = ("name", "course", "date")


# Öğrenci Notları
admin.site.register(StudentScore)
