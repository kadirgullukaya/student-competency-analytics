from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# --- 0. YENİ EKLENEN: BÖLÜM MODELİ ---
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Bölüm Adı")

    def __str__(self):
        return self.name


# 1. TEMEL MODELLER (OBS Parçaları)
class Semester(models.Model):
    name = models.CharField(max_length=50)  # Örn: "Fall 2025"

    def __str__(self):
        return self.name


class Student(models.Model):
    # Bu satır öğrenciyi giriş yapan kullanıcıya bağlar
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # 🔥 YENİ EKLENEN: Bölüm İlişkisi
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bölüm")

    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"


class Course(models.Model):
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses"
    )

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.teacher.username if self.teacher else 'Atanmamış'}"


# 2. AKADEMİK ÇIKTILAR (OUTCOMES)
class ProgramOutcome(models.Model):
    code = models.CharField(max_length=10)  # Örn: PO1
    description = models.TextField()  # Açıklama metni

    def __str__(self):
        return self.code


class LearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)  # Örn: LO1
    description = models.TextField()

    # Hangi LO, Hangi PO'yu ne kadar etkiliyor?
    program_outcomes = models.ManyToManyField(ProgramOutcome, through="OutcomeMapping")

    def __str__(self):
        return f"{self.course.code} - {self.code}"


class OutcomeMapping(models.Model):
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE)
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE)
    weight = models.DecimalField(
        max_digits=3, decimal_places=2, help_text="Örn: 0.50 (%50)"
    )

    def __str__(self):
        return f"{self.learning_outcome} -> {self.program_outcome} (%{self.weight})"


# 3. DEĞERLENDİRME (Sınavlar)
class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Örn: Midterm 1
    date = models.DateField(auto_now_add=True)

    # --- YENİ EKLENEN ALAN: Sınavın Ağırlığı ---
    weight = models.IntegerField(
        default=0, help_text="Genel not ortalamasına etkisi (%)"
    )
    # -------------------------------------------

    def __str__(self):
        return f"{self.course.code} - {self.name} (%{self.weight})"


class AssessmentWeight(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Örn: 60 için 60 yazınız."
    )

    def __str__(self):
        return f"{self.assessment.name} -> {self.learning_outcome.code} (%{self.percentage})"


# 4. ÖĞRENCİ NOTLARI
class StudentScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Öğrencinin aldığı not (0-100)"
    )

    class Meta:
        unique_together = ("student", "assessment")

    def __str__(self):
        return f"{self.student.first_name} - {self.assessment.name}: {self.score}"


# 5. DERS KAYDI (ENROLLMENT)
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.first_name} -> {self.course.code}"


# --- MEVCUT ESKİ KODLAR (Lesson, Grade) ---
class Lesson(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Ders Kodu")
    name = models.CharField(max_length=100, verbose_name="Ders Adı")
    credit = models.IntegerField(default=3, verbose_name="Kredi")

    def __str__(self):
        return f"{self.code} - {self.name}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', verbose_name="Öğrenci")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Ders")
    
    # Notlar (0-100 arası)
    midterm = models.IntegerField(
        verbose_name="Vize", 
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    final = models.IntegerField(
        verbose_name="Final", 
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        unique_together = ('student', 'lesson')
        verbose_name = "Not"
        verbose_name_plural = "Notlar"

    @property
    def average(self):
        if self.midterm is None or self.final is None:
            return None
        
        avg = (self.midterm * 0.4) + (self.final * 0.6)
        return round(avg, 2)

    @property
    def status(self):
        avg = self.average
        if avg is None:
            return "Devam Ediyor"
        return "Geçti" if avg >= 50 else "Kaldı"