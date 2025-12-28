from django.contrib import admin
from .models import (
    Department,       # <--- YENİ EKLENEN
    Semester,
    Student,
    Course,
    ProgramOutcome,
    LearningOutcome,
    OutcomeMapping,
    Assessment,
    AssessmentWeight,
    StudentScore,
    Enrollment,
)

# --- 1. YENİ EKLENEN: BÖLÜM YÖNETİMİ ---
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# --- TEMEL MODELLER ---

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Listede görünecek sütunlar (Bölüm eklendi)
    list_display = ('student_id', 'first_name', 'last_name', 'department', 'user')
    # Sağ tarafta filtreleme menüsü
    list_filter = ('department',) 
    # Arama çubuğu
    search_fields = ('student_id', 'first_name', 'last_name', 'user__username')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'semester')
    list_filter = ('semester', 'teacher')
    search_fields = ('code', 'name')

@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')

# --- LO YÖNETİMİ (Inline Yapısı Korundu) ---
class OutcomeMappingInline(admin.TabularInline):
    model = OutcomeMapping
    extra = 1

@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    inlines = [OutcomeMappingInline]
    list_display = ("code", "course", "description")
    list_filter = ('course',)

# --- SINAV YÖNETİMİ (Inline Yapısı Korundu) ---
class AssessmentWeightInline(admin.TabularInline):
    model = AssessmentWeight
    extra = 1

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    inlines = [AssessmentWeightInline]
    list_display = ("name", "course", "date", "weight")
    list_filter = ('course',)

# --- DİĞERLERİ ---

@admin.register(StudentScore)
class StudentScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'score')
    list_filter = ('assessment__course', 'assessment')
    search_fields = ('student__first_name', 'student__student_id')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date')
    list_filter = ('course', 'student__department') # Bölüme göre kayıtları süzebilirsin