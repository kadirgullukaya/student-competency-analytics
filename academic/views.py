import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Max, Count
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
)
from .forms import (
    LearningOutcomeForm,
    AssessmentForm,
    AssessmentWeightForm,
    OutcomeMappingForm,
    EnrollmentForm,
)


def is_teacher(user):
    return user.groups.filter(name="Öğretmen").exists() or user.is_superuser


# --- 1. ANA PANEL (GENEL BAKIŞ) ---
@login_required
@user_passes_test(is_teacher)
def teacher_dashboard_home(request):
    my_courses = Course.objects.filter(teacher=request.user)
    if not my_courses.exists() and request.user.is_superuser:
        my_courses = Course.objects.all()

    total_courses = my_courses.count()
    total_students = Enrollment.objects.filter(course__in=my_courses).count()
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
    my_courses = Course.objects.filter(teacher=request.user)
    if not my_courses.exists() and request.user.is_superuser:
        my_courses = Course.objects.all()

    total_courses = my_courses.count()
    total_students = Enrollment.objects.filter(course__in=my_courses).count()
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

    # --- GRAFİK VERİLERİ (JSON DÖNÜŞÜMÜ - float() EKLENDİ) ---
    teacher_courses = Course.objects.filter(teacher=request.user)
    if not teacher_courses.exists() and request.user.is_superuser:
        teacher_courses = Course.objects.all()

    course_labels = []
    course_data = []
    for c in teacher_courses:
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


# --- DİĞER FONKSİYONLAR ---
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
    my_courses = Course.objects.filter(teacher=request.user)
    if not my_courses.exists() and request.user.is_superuser:
        assessments = Assessment.objects.all().order_by("-date")
    else:
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


# --- 9. ÖĞRENCİ DASHBOARD (GÜNCELLENMİŞ VERSİYON) ---
@login_required
def student_course_dashboard(request, course_id):
    # Güvenlik Kontrolü
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")

    course = get_object_or_404(Course, id=course_id)
    student = request.user.student

    # 1. GENEL NOT HESABI
    assessments = Assessment.objects.filter(course=course)
    total_weight = 0
    weighted_sum = 0

    student_scores = StudentScore.objects.filter(
        student=student, assessment__in=assessments
    )
    score_map = {s.assessment.id: s.score for s in student_scores}

    # Grafik Verileri
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

        # Sınıf Ortalaması
        avg_score = StudentScore.objects.filter(assessment=exam).aggregate(
            Avg("score")
        )["score__avg"]
        if avg_score:
            class_averages.append(float(round(avg_score, 1)))
        else:
            class_averages.append(0)

    current_average = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0

    # 2. LO (DERS ÇIKTISI) DETAYLI HESAP
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

        # Grafik için veri
        lo_data.append(final_success)

        # HTML Listesi için veri
        color_class = "success"  # Yeşil
        if final_success < 50:
            color_class = "danger"  # Kırmızı
        elif final_success < 70:
            color_class = "warning"  # Sarı

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


# --- 10. GİRİŞ YÖNLENDİRİCİSİ (TRAFİK POLİSİ) ---
@login_required
def home_redirect(request):
    if (
        request.user.groups.filter(name="Öğretmen").exists()
        or request.user.is_superuser
    ):
        return redirect("teacher_dashboard_home")

    elif hasattr(request.user, "student"):
        return redirect("student_course_list")

    return redirect("login")


# --- 11. ÖĞRENCİ DERS LİSTESİ (ANA SAYFA) ---
@login_required
def student_course_list(request):
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")

    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student)

    context = {"enrollments": enrollments}
    return render(request, "student_course_list.html", context)


# --- 12. GENEL BAŞARIM (PO ANALİZİ) - AĞIRLIKLI HESAPLAMA ---
@login_required
def student_general_success(request):
    if not hasattr(request.user, "student"):
        return redirect("teacher_dashboard_home")

    student = request.user.student

    # 1. PO HAVUZLARINI HAZIRLA
    all_pos = ProgramOutcome.objects.all()
    po_buckets = {
        po.code: {"earned": 0, "max": 0, "desc": po.description} for po in all_pos
    }

    # 2. ÖĞRENCİNİN TÜM DERSLERİNİ GEZ
    enrollments = Enrollment.objects.filter(student=student)

    for enrollment in enrollments:
        course = enrollment.course

        # --- A. LO BAŞARISINI HESAPLA ---
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

            # --- B. PO HESABI ---
            mappings = OutcomeMapping.objects.filter(learning_outcome=lo)

            for mapping in mappings:
                po_code = mapping.program_outcome.code
                weight = float(mapping.weight)

                contribution = lo_success_rate * weight
                max_contribution = 100 * weight

                po_buckets[po_code]["earned"] += contribution
                po_buckets[po_code]["max"] += max_contribution

    # 3. SONUÇLARI GRAFİK İÇİN HAZIRLA
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


# --- 13. EŞLEŞTİRME SİLME (YENİ EKLENEN) ---
@login_required
@user_passes_test(is_teacher)
def delete_outcome_mapping(request, mapping_id):
    # Silinecek eşleştirmeyi bul
    mapping = get_object_or_404(OutcomeMapping, id=mapping_id)

    # Silindikten sonra geri döneceğimiz LO sayfasının ID'sini sakla
    lo_id = mapping.learning_outcome.id

    if request.method == "POST":
        mapping.delete()

    return redirect("lo_mapping_detail", lo_id=lo_id)
