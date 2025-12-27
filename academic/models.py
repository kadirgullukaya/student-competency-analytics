from django.db import models
from django.contrib.auth.models import User


# 1. TEMEL MODELLER
class Semester(models.Model):
    TERM_CHOICES = [
        ("Fall", "Güz"),
        ("Spring", "Bahar"),
        ("Summer", "Yaz"),
    ]
    name = models.CharField(max_length=50, verbose_name="Dönem Adı")
    # YENİ ALANLAR BURAYA GELDİ 👇
    year = models.IntegerField(default=2024, verbose_name="Yıl")
    term = models.CharField(
        max_length=10, choices=TERM_CHOICES, default="Fall", verbose_name="Dönem Tipi"
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # student_id olarak bıraktık çünkü DB'de böyle. Sakın student_number yapma!
    student_id = models.CharField(
        max_length=20, unique=True, verbose_name="Öğrenci Numarası"
    )
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


# 2. AKADEMİK ÇIKTILAR
class ProgramOutcome(models.Model):
    code = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return self.code


class LearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    description = models.TextField()
    program_outcomes = models.ManyToManyField(ProgramOutcome, through="OutcomeMapping")

    def __str__(self):
        return f"{self.course.code} - {self.code}"


class OutcomeMapping(models.Model):
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE)
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.learning_outcome} -> {self.program_outcome} (%{self.weight})"


# 3. DEĞERLENDİRME
class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course.code} - {self.name} (%{self.weight})"


class AssessmentWeight(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.assessment.name} -> {self.learning_outcome.code} (%{self.percentage})"


# 4. NOTLAR
class StudentScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ("student", "assessment")

    def __str__(self):
        return f"{self.student.first_name} - {self.assessment.name}: {self.score}"


# 5. KAYIT
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.first_name} -> {self.course.code}"
