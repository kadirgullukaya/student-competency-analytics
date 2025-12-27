from django import forms
from django.contrib.auth.models import User
from .models import (
    LearningOutcome,
    ProgramOutcome,
    Assessment,
    AssessmentWeight,
    OutcomeMapping,
    Enrollment,
    Student,
    Course,
    Semester,
)

# --- BÖLÜM BAŞKANI İÇİN YENİ FORMLAR (YÖNETİM) ---


# A. ÖĞRENCİ OLUŞTURMA FORMU (User + Student birleşik)
class StudentCreationForm(forms.ModelForm):
    first_name = forms.CharField(label="Ad", max_length=30)
    last_name = forms.CharField(label="Soyad", max_length=30)
    email = forms.EmailField(label="E-posta", required=True)
    # DÜZELTME: Modeldeki 'student_id' alanıyla eşleşmesi için isim güncellendi
    student_id = forms.CharField(label="Öğrenci Numarası", max_length=20)
    password = forms.CharField(label="Şifre", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        # 1. Önce Django User oluştur
        user = super().save(commit=False)
        # Kullanıcı adı olarak öğrenci numarasını kullanıyoruz
        user.username = self.cleaned_data["student_id"]
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            # 2. Sonra Student profilini oluştur ve bağla
            # DÜZELTME: Model alanı 'student_id' olduğu için burası düzeltildi
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data["student_id"],
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
            )
        return user


# B. DERS EKLEME FORMU
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code", "semester", "teacher"]
        labels = {
            "name": "Ders Adı",
            "code": "Ders Kodu",
            "semester": "Dönem",
            "teacher": "Dersi Veren Öğretmen",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
            if field in ["semester", "teacher"]:
                self.fields[field].widget.attrs.update({"class": "form-select"})


# C. DÖNEM EKLEME FORMU
class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        # DÜZELTME: Modelde olmayan 'year' ve 'term' alanları kaldırıldı.
        fields = ["name"]
        labels = {
            "name": "Dönem Adı (Örn: 2024-2025 Güz)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


# --- MEVCUT FORMLAR ---


# 1. LO EKLEME FORMU
class LearningOutcomeForm(forms.ModelForm):
    class Meta:
        model = LearningOutcome
        fields = ["course", "code", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "course": "Ders Seçin",
            "code": "LO Kodu (Örn: LO1)",
            "description": "Açıklama",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "placeholder": "..."}
            )


# 2. PO FORMU
class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ["code", "description"]
        labels = {
            "code": "PO Kodu (Örn: PO1)",
            "description": "Program Çıktısı Açıklaması",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "placeholder": "..."}
            )


# 3. SINAV OLUŞTURMA FORMU
class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ["course", "name", "weight"]
        labels = {
            "course": "Ders Seçin",
            "name": "Sınav Adı (Örn: Vize 1, Final)",
            "weight": "Etki Oranı (%)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "placeholder": "..."}
            )


# 4. SINAV DETAY (LO AĞIRLIĞI) FORMU
class AssessmentWeightForm(forms.ModelForm):
    class Meta:
        model = AssessmentWeight
        fields = ["learning_outcome", "percentage"]
        labels = {
            "learning_outcome": "İlgili Ders Çıktısı (LO)",
            "percentage": "Etki Oranı (%)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "placeholder": "..."}
            )


# 5. LO -> PO EŞLEŞTİRME FORMU
class OutcomeMappingForm(forms.ModelForm):
    class Meta:
        model = OutcomeMapping
        fields = ["program_outcome", "weight"]
        labels = {
            "program_outcome": "Hedeflenen Program Çıktısı (PO)",
            "weight": "Katkı Oranı (0.0 - 1.0 arası)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "placeholder": "..."}
            )


# 6. ÖĞRENCİ EKLEME (ENROLLMENT) FORMU
class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student"]
        labels = {"student": "Öğrenci Seç"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-select"})
