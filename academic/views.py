import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.db.models import Avg, Max, Count
from django.contrib import messages

# --- EKLENEN KÜTÜPHANELER (AYARLAR İÇİN) ---
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .models import (
    Course,
    LearningOutcome,
    Assessment,
    AssessmentWeight,
    ProgramOutcome,
    Student,
    StudentScore,
    OutcomeMapping,
    Enrollment,
    Semester,
)
from .forms import (
    LearningOutcomeForm,
    AssessmentForm,
    AssessmentWeightForm,
    OutcomeMappingForm,
    EnrollmentForm,
    StudentCreationForm,
    CourseForm,
    SemesterForm,
    ProgramOutcomeForm,
)


# --- YETKİ KONTROLLERİ ---


def is_teacher(user):
    # Hem "Öğretmen" hem de "Bölüm Başkanı" öğretmen paneline girebilir
    return (
        user.groups.filter(name__in=["Öğretmen", "Bölüm Başkanı"]).exists()
        or user.is_superuser
    )


def is_department_head(user):
    # Sadece Bölüm Başkanı (veya Superuser) girebilir
    return user.groups.filter(name="Bölüm Başkanı").exists() or user.is_superuser


# --- 1. ANA PANEL (GENEL BAKIŞ) ---
@login_required
@user_passes_test(is_teacher)
def teacher_dashboard_home(request):
    # Eğer Bölüm Başkanı ise TÜM dersleri görsün, değilse sadece kendi dersleri
    if is_department_head(request.user):
        my_courses = Course.objects.all()
    else:
        my_courses = Course.objects.filter(teacher=request.user)
        if not my_courses.exists() and request.user.is_superuser:
            my_courses = Course.objects.all()

    total_courses = my_courses.count()
    total_students = Enrollment.objects.filter(course__in=my_courses).distinct().count()
    total_exams = Assessment.objects.filter(course__in=my_courses).count()
    recent_exams = Assessment.objects.filter(course__in=my_courses).order_by("-date")[
        :5
    ]

    context = {
        "courses": my_courses,
        "stats": {
            "total_courses": total_courses,
            "total_students": total_students,
            "total_exams": total_exams,
        },
        "recent_exams": recent_exams,
    }
    return render(request, "dashboard_home.html", context)


# --- 2. DERS LİSTESİ ---
@login_required
@user_passes_test(is_teacher)
def teacher_courses(request):
    # 1. Hangi dersleri göstereceğimizi belirle
    if is_department_head(request.user):
        my_courses = Course.objects.all()
    else:
        my_courses = Course.objects.filter(teacher=request.user)

    # 2. İSTATİSTİKLERİ HESAPLA
    total_courses = my_courses.count()

    # Tüm derslerdeki tekil öğrenci sayısı
    total_students = (
        Enrollment.objects.filter(course__in=my_courses)
        .values("student")
        .distinct()
        .count()
    )

    # Toplam sınav sayısı
    total_exams = Assessment.objects.filter(course__in=my_courses).count()

    context = {
        "courses": my_courses,
        "stats": {
            "total_courses": total_courses,
            "total_students": total_students,
            "total_exams": total_exams,
        },
    }
    return render(request, "teacher_courses.html", context)


# --- 3. DERS DASHBOARD (GRAFİKLİ) ---
@login_required
@user_passes_test(is_teacher)
def course_dashboard(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Güvenlik: Başka hocanın dersine girmeye çalışırsa engelle (Bölüm Başkanı hariç)
    if (
        not is_department_head(request.user)
        and course.teacher != request.user
        and not request.user.is_superuser
    ):
        return redirect("teacher_dashboard_home")

    lo_form = LearningOutcomeForm(initial={"course": course})
    assessment_form = AssessmentForm(initial={"course": course})

    if request.method == "POST":
        if "lo_submit" in request.POST:
            lo_form = LearningOutcomeForm(request.POST)
            if lo_form.is_valid():
                new_lo = lo_form.save(commit=False)
                new_lo.course = course
                new_lo.save()
                return redirect("course_dashboard", course_id=course.id)
        elif "assessment_submit" in request.POST:
            assessment_form = AssessmentForm(request.POST)
            if assessment_form.is_valid():
                new_exam = assessment_form.save(commit=False)
                new_exam.course = course
                new_exam.save()
                return redirect("course_dashboard", course_id=course.id)

    outcomes = LearningOutcome.objects.filter(course=course)
    assessments = Assessment.objects.filter(course=course).order_by("-date")

    # İstatistikler
    course_average = (
        StudentScore.objects.filter(assessment__course=course).aggregate(Avg("score"))[
            "score__avg"
        ]
        or 0
    )
    max_score = (
        StudentScore.objects.filter(assessment__course=course).aggregate(Max("score"))[
            "score__max"
        ]
        or 0
    )
    total_students = Enrollment.objects.filter(course=course).count()

    # Grafik Verileri
    all_courses = (
        Course.objects.all()
        if is_department_head(request.user)
        else Course.objects.filter(teacher=request.user)
    )

    course_labels = []
    course_data = []
    for c in all_courses:
        avg = (
            StudentScore.objects.filter(assessment__course=c).aggregate(Avg("score"))[
                "score__avg"
            ]
            or 0
        )
        course_labels.append(c.code)
        course_data.append(float(round(avg, 1)))

    exam_labels = []
    exam_data = []
    for exam in assessments.reverse():
        avg = (
            StudentScore.objects.filter(assessment=exam).aggregate(Avg("score"))[
                "score__avg"
            ]
            or 0
        )
        exam_labels.append(exam.name)
        exam_data.append(float(round(avg, 1)))

    recent_exam = assessments.first()
    risky_students = (
        StudentScore.objects.filter(assessment=recent_exam, score__lt=50)
        if recent_exam
        else []
    )

    context = {
        "active_course": course,
        "lo_form": lo_form,
        "assessment_form": assessment_form,
        "outcomes": outcomes,
        "assessments": assessments,
        "stats": {
            "average": round(course_average, 1),
            "max": max_score,
            "students": total_students,
        },
        "graph_comparison_labels": json.dumps(course_labels),
        "graph_comparison_data": json.dumps(course_data),
        "graph_exams_labels": json.dumps(exam_labels),
        "graph_exams_data": json.dumps(exam_data),
        "risky_students": risky_students,
    }
    return render(request, "teacher_dashboard.html", context)


# --- BÖLÜM BAŞKANI YÖNETİM FONKSİYONLARI (YENİ) ---


# 🔥 YENİ EKLENEN: BÖLÜM BAŞKANI ANA MENÜSÜ
@login_required
@user_passes_test(is_department_head)
def department_head_dashboard(request):
    """
    Bölüm Başkanı için ana menü.
    Buradan Ders Yönetimi, Öğrenci Yönetimi gibi sayfalara gidecek.
    """
    return render(request, "department_head_dashboard.html")


# A. ÖĞRENCİ YÖNETİMİ
@login_required
@user_passes_test(is_department_head)
def manage_students(request):
    students = Student.objects.all().select_related("user").order_by("student_id")
    return render(request, "manage_students.html", {"students": students})


@login_required
@user_passes_test(is_department_head)
def add_student(request):
    if request.method == "POST":
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Öğrenci başarıyla eklendi.")
            return redirect("manage_students")
    else:
        form = StudentCreationForm()
    return render(request, "add_student.html", {"form": form})


@login_required
@user_passes_test(is_department_head)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        user = student.user
        user.delete()
        messages.success(request, "Öğrenci ve ilişkili veriler silindi.")
    return redirect("manage_students")


# B. DERS YÖNETİMİ
@login_required
@user_passes_test(is_department_head)
def manage_courses(request):
    courses = Course.objects.all().select_related("teacher", "semester")

    # --- EKLENEN KISIM: İSTATİSTİKLER ---
    # 1. Toplam Ders Sayısı
    total_courses = courses.count()

    # 2. Toplam Öğrenci Sayısı (Tüm derslere kayıtlı tekil öğrenci sayısı)
    total_students = (
        Enrollment.objects.filter(course__in=courses)
        .values("student")
        .distinct()
        .count()
    )

    # 3. Toplam Sınav Sayısı
    total_exams = Assessment.objects.filter(course__in=courses).count()

    context = {
        "courses": courses,
        "stats": {
            "total_courses": total_courses,
            "total_students": total_students,
            "total_exams": total_exams,
        },
    }
    return render(request, "manage_courses.html", context)


@login_required
@user_passes_test(is_department_head)
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ders başarıyla oluşturuldu.")
            return redirect("manage_courses")
    else:
        form = CourseForm()
    return render(request, "add_course.html", {"form": form})


@login_required
@user_passes_test(is_department_head)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Ders silindi.")
    return redirect("manage_courses")


# C. DÖNEM YÖNETİMİ
@login_required
@user_passes_test(is_department_head)
def manage_semesters(request):
    semesters = Semester.objects.all().order_by("name")
    return render(request, "manage_semesters.html", {"semesters": semesters})


@login_required
@user_passes_test(is_department_head)
def add_semester(request):
    if request.method == "POST":
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Dönem başarıyla eklendi.")
            return redirect("manage_semesters")
    else:
        form = SemesterForm()
    return render(request, "add_semester.html", {"form": form})


@login_required
@user_passes_test(is_department_head)
def delete_semester(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    if request.method == "POST":
        semester.delete()
        messages.success(request, "Dönem silindi.")
    return redirect("manage_semesters")


# D. PO (PROGRAM ÇIKTISI) YÖNETİMİ
@login_required
@user_passes_test(is_department_head)
def manage_program_outcomes(request):
    # Program Çıktılarını (PO) Çek
    pos = ProgramOutcome.objects.all().order_by("code")

    # 🔥 YENİ: Öğrenme Çıktılarını (LO) da Çek (Ders bilgisiyle beraber)
    # Course bilgisiyle beraber çektiğimiz için select_related kullanıyoruz (Performans artışı)
    los = (
        LearningOutcome.objects.all()
        .select_related("course")
        .order_by("course__code", "code")
    )

    context = {"pos": pos, "los": los}
    return render(request, "manage_program_outcomes.html", context)


@login_required
@user_passes_test(is_department_head)
def add_program_outcome(request):
    if request.method == "POST":
        form = ProgramOutcomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Program Çıktısı (PO) eklendi.")
            return redirect("manage_program_outcomes")
    else:
        form = ProgramOutcomeForm()
    return render(request, "add_program_outcome.html", {"form": form})


@login_required
@user_passes_test(is_department_head)
def delete_program_outcome(request, po_id):
    po = get_object_or_404(ProgramOutcome, id=po_id)
    if request.method == "POST":
        po.delete()
        messages.success(request, "PO silindi.")
    return redirect("manage_program_outcomes")


# --- DİĞER MEVCUT FONKSİYONLAR ---


@login_required
@user_passes_test(is_teacher)
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.course = course
            enrollment.save()
            return redirect("course_students", course_id=course.id)
    else:
        form = EnrollmentForm()
    enrollments = Enrollment.objects.filter(course=course)
    return render(
        request,
        "course_students.html",
        {"course": course, "enrollments": enrollments, "form": form},
    )


@login_required
@user_passes_test(is_teacher)
def exam_list(request):
    if is_department_head(request.user):
        assessments = Assessment.objects.all().order_by("-date")
    else:
        my_courses = Course.objects.filter(teacher=request.user)
        assessments = Assessment.objects.filter(course__in=my_courses).order_by("-date")
    return render(request, "exam_list.html", {"assessments": assessments})


@login_required
@user_passes_test(is_teacher)
def assessment_detail(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    weights = AssessmentWeight.objects.filter(assessment=assessment)
    if request.method == "POST":
        form = AssessmentWeightForm(request.POST)
        if form.is_valid():
            weight = form.save(commit=False)
            weight.assessment = assessment
            weight.save()
            return redirect("assessment_detail", assessment_id=assessment.id)
    else:
        form = AssessmentWeightForm()
    form.fields["learning_outcome"].queryset = LearningOutcome.objects.filter(
        course=assessment.course
    )
    return render(
        request,
        "assessment_detail.html",
        {"assessment": assessment, "weights": weights, "form": form},
    )


@login_required
@user_passes_test(is_teacher)
def enter_grades(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    enrollments = Enrollment.objects.filter(course=assessment.course)
    students = [e.student for e in enrollments]
    if request.method == "POST":
        for student in students:
            score_value = request.POST.get(f"score_{student.id}")
            if score_value:
                StudentScore.objects.update_or_create(
                    student=student,
                    assessment=assessment,
                    defaults={"score": score_value},
                )
        return redirect("enter_grades", assessment_id=assessment.id)
    existing_scores = StudentScore.objects.filter(assessment=assessment)
    score_dict = {score.student.id: score.score for score in existing_scores}
    return render(
        request,
        "enter_grades.html",
        {"assessment": assessment, "students": students, "score_dict": score_dict},
    )


@login_required
@user_passes_test(is_teacher)
def lo_mapping_detail(request, lo_id):
    lo = get_object_or_404(LearningOutcome, id=lo_id)
    mappings = OutcomeMapping.objects.filter(learning_outcome=lo)
    if request.method == "POST":
        form = OutcomeMappingForm(request.POST)
        if form.is_valid():
            mapping = form.save(commit=False)
            mapping.learning_outcome = lo
            mapping.save()
            return redirect("lo_mapping_detail", lo_id=lo.id)
    else:
        form = OutcomeMappingForm()
    return render(
        request,
        "lo_mapping_detail.html",
        {"lo": lo, "mappings": mappings, "form": form},
    )


@login_required
@user_passes_test(is_teacher)
def delete_outcome_mapping(request, mapping_id):
    mapping = get_object_or_404(OutcomeMapping, id=mapping_id)
    lo_id = mapping.learning_outcome.id
    if request.method == "POST":
        mapping.delete()
    return redirect("lo_mapping_detail", lo_id=lo_id)


# --- ÖĞRENCİ PANELİ ---


@login_required
def student_course_dashboard(request, course_id):
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student
    assessments = Assessment.objects.filter(course=course)
    total_weight = 0
    weighted_sum = 0
    student_scores = StudentScore.objects.filter(
        student=student, assessment__in=assessments
    )
    score_map = {s.assessment.id: s.score for s in student_scores}
    exam_labels = []
    my_scores = []
    class_averages = []
    for exam in assessments:
        exam_labels.append(exam.name)
        if exam.id in score_map:
            my_score = float(score_map[exam.id])
            my_scores.append(my_score)
            weighted_sum += my_score * exam.weight
            total_weight += exam.weight
        else:
            my_scores.append(0)
        avg_score = StudentScore.objects.filter(assessment=exam).aggregate(
            Avg("score")
        )["score__avg"]
        class_averages.append(float(round(avg_score, 1)) if avg_score else 0)
    current_average = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0
    learning_outcomes = LearningOutcome.objects.filter(course=course)
    lo_labels = []
    lo_data = []
    lo_details = []
    for lo in learning_outcomes:
        lo_labels.append(f"{lo.code}")
        relevant_weights = AssessmentWeight.objects.filter(learning_outcome=lo)
        lo_total_score = 0
        lo_max_possible = 0
        for aw in relevant_weights:
            exam = aw.assessment
            if exam.id in score_map:
                student_exam_score = float(score_map[exam.id])
                effect = float(aw.percentage)
                lo_total_score += student_exam_score * effect
                lo_max_possible += 100 * effect
        final_success = 0
        if lo_max_possible > 0:
            final_success = float(round((lo_total_score / lo_max_possible) * 100, 1))
        lo_data.append(final_success)
        color_class = (
            "success"
            if final_success >= 70
            else "warning" if final_success >= 50 else "danger"
        )
        lo_details.append(
            {
                "code": lo.code,
                "description": lo.description,
                "score": final_success,
                "color": color_class,
            }
        )
    context = {
        "course": course,
        "student": student,
        "current_average": current_average,
        "assessments": assessments,
        "score_map": score_map,
        "radar_labels": json.dumps(lo_labels),
        "radar_data": json.dumps(lo_data),
        "exam_labels": json.dumps(exam_labels),
        "my_scores": json.dumps(my_scores),
        "class_averages": json.dumps(class_averages),
        "lo_details": lo_details,
    }
    return render(request, "student_dashboard.html", context)


@login_required
def student_course_list(request):
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student)
    return render(request, "student_course_list.html", {"enrollments": enrollments})


@login_required
def student_general_success(request):
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")
    student = request.user.student
    all_pos = ProgramOutcome.objects.all()
    po_buckets = {
        po.code: {"earned": 0, "max": 0, "desc": po.description} for po in all_pos
    }
    enrollments = Enrollment.objects.filter(student=student)
    for enrollment in enrollments:
        course = enrollment.course
        assessments = Assessment.objects.filter(course=course)
        student_scores = StudentScore.objects.filter(
            student=student, assessment__in=assessments
        )
        score_map = {s.assessment.id: s.score for s in student_scores}
        learning_outcomes = LearningOutcome.objects.filter(course=course)
        for lo in learning_outcomes:
            relevant_weights = AssessmentWeight.objects.filter(learning_outcome=lo)
            lo_total = 0
            lo_max_possible = 0
            for aw in relevant_weights:
                if aw.assessment.id in score_map:
                    lo_total += float(score_map[aw.assessment.id]) * float(
                        aw.percentage
                    )
                    lo_max_possible += 100 * float(aw.percentage)
            lo_success_rate = 0
            if lo_max_possible > 0:
                lo_success_rate = (lo_total / lo_max_possible) * 100
            mappings = OutcomeMapping.objects.filter(learning_outcome=lo)
            for mapping in mappings:
                po_code = mapping.program_outcome.code
                weight = float(mapping.weight)
                contribution = lo_success_rate * weight
                max_contribution = 100 * weight
                po_buckets[po_code]["earned"] += contribution
                po_buckets[po_code]["max"] += max_contribution
    po_labels = []
    po_scores = []
    po_details = []
    for code, data in po_buckets.items():
        final_score = 0
        if data["max"] > 0:
            final_score = round((data["earned"] / data["max"]) * 100, 1)

        po_labels.append(code)
        po_scores.append(final_score)
        color = (
            "success"
            if final_score >= 70
            else "warning" if final_score >= 50 else "danger"
        )
        po_details.append(
            {
                "code": code,
                "description": data["desc"],
                "score": final_score,
                "color": color,
            }
        )
    context = {
        "student": student,
        "po_labels": json.dumps(po_labels),
        "po_scores": json.dumps(po_scores),
        "po_details": po_details,
    }
    return render(request, "student_general_success.html", context)


# --- ÖĞRENCİ NOTLARIM SAYFASI (GÜNCELLENDİ: Ders Bazlı Gruplama) ---
@login_required
def student_grades(request):
    """
    Öğrencinin notlarını derslere göre gruplayarak ve ortalama hesaplayarak gösterir.
    """
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")

    student = request.user.student

    # Tüm notları çek
    all_scores = (
        StudentScore.objects.filter(student=student)
        .select_related("assessment", "assessment__course")
        .order_by("assessment__course__code", "-assessment__date")
    )

    # Veriyi Python tarafında gruplayalım
    # Yapı: { course_id: {'course': course_obj, 'scores': [], 'total': 0, 'weights': 0} }
    courses_data = {}

    for s in all_scores:
        course = s.assessment.course
        if course.id not in courses_data:
            courses_data[course.id] = {
                "course": course,
                "scores": [],
                "weighted_sum": 0,
                "total_weight": 0,
                "average": 0
            }
        
        # Sınavı listeye ekle
        courses_data[course.id]["scores"].append(s)
        
        # Ağırlıklı ortalama hesabı için veri topla (Basit ortalama değil, ağırlıklı ortalama)
        # Not: Assessment modelinde 'weight' (yüzde etki) alanı olduğunu varsayıyoruz.
        # Eğer weight yoksa direkt aritmetik ortalama alırız.
        weight = s.assessment.weight if hasattr(s.assessment, 'weight') else 1
        courses_data[course.id]["weighted_sum"] += float(s.score) * float(weight)
        courses_data[course.id]["total_weight"] += float(weight)

    # Ortalamaları hesapla ve listeye çevir
    grouped_grades = []
    for cid, data in courses_data.items():
        if data["total_weight"] > 0:
            # Eğer ağırlık sistemi varsa
            avg = data["weighted_sum"] / data["total_weight"]
            # Eğer weight yüzdelikse (örn toplam 100 değilse) ve basit ortalama isteniyorsa:
            # avg = data["weighted_sum"] / len(data["scores"]) # (Basit aritmetik için bunu açabilirsin)
        else:
            avg = 0
            
        data["average"] = round(avg, 1)
        grouped_grades.append(data)

    context = {"grouped_grades": grouped_grades}
    return render(request, "student_grades.html", context)


# --- ÖĞRENCİ AYARLAR SAYFASI (YENİ EKLENDİ) ---
@login_required
def student_settings(request):
    """
    Öğrencinin profil bilgilerini gördüğü ve şifresini değiştirebildiği sayfa.
    """
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")
    
    student = request.user.student
    user = request.user

    # Şifre Değiştirme İşlemi
    if request.method == 'POST':
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            # Oturumun düşmemesi için hash güncelliyoruz
            update_session_auth_hash(request, user)
            messages.success(request, 'Şifreniz başarıyla güncellendi!')
            return redirect('student_settings')
        else:
            messages.error(request, 'Lütfen hataları düzeltin.')
    else:
        password_form = PasswordChangeForm(user)

    context = {
        'student': student,
        'password_form': password_form
    }
    return render(request, "student_settings.html", context)


# 🔥 TRAFİK POLİSİ (YÖNLENDİRME MERKEZİ)
@login_required
def home_redirect(request):
    """
    Kullanıcıyı rolüne göre yönlendirir.
    Rolü yoksa, sanki hatalı giriş yapmış gibi başa döndürür.
    """
    # 1. BÖLÜM BAŞKANI
    if is_department_head(request.user):
        return redirect("department_head_dashboard")

    # 2. ÖĞRETMEN
    if request.user.groups.filter(name="Öğretmen").exists():
        return redirect("teacher_dashboard_home")

    # 3. ÖĞRENCİ
    elif hasattr(request.user, "student"):
        return redirect("student_course_list")

    # 4. HİÇBİRİ DEĞİLSE -> HATA VER VE AT
    # Kullanıcıya "Rolün yok" demek yerine genel bir hata veriyoruz.
    messages.error(request, "Hatalı kullanıcı adı veya şifre.")
    logout(request)
    return redirect("login")