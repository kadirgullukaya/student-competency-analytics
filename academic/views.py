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
        # DÜZELTME BURADA: Decimal -> float dönüşümü
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
        # DÜZELTME BURADA: Decimal -> float dönüşümü
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
        # --- VERİLERİ JSON OLARAK GÖNDERİYORUZ ---
        "graph_comparison_labels": json.dumps(course_labels),
        "graph_comparison_data": json.dumps(course_data),
        "graph_exams_labels": json.dumps(exam_labels),
        "graph_exams_data": json.dumps(exam_data),
        # ----------------------------------------
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
