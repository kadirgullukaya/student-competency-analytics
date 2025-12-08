from django import forms
from .models import (
    LearningOutcome,
    ProgramOutcome,
    Assessment,
    AssessmentWeight,
    OutcomeMapping,
    Enrollment,
)


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


# 3. SINAV OLUŞTURMA FORMU (GÜNCELLENDİ)
class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        # 'weight' alanını buraya ekledik
        fields = ["course", "name", "weight"]
        labels = {
            "course": "Ders Seçin",
            "name": "Sınav Adı (Örn: Vize 1, Final)",
            "weight": "Etki Oranı (%)",  # Yeni alanın etiketi
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
