from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from academic import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # --- GİRİŞ / ÇIKIŞ ---
    path("", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # --- ANA MENÜLER (DASHBOARD) ---
    path("dashboard/", views.teacher_dashboard_home, name="teacher_dashboard_home"),
    path("courses/", views.teacher_courses, name="teacher_courses"),
    path("exams/", views.exam_list, name="exam_list"),
    # --- DERS DETAYLARI ---
    path(
        "course/<int:course_id>/dashboard/",
        views.course_dashboard,
        name="course_dashboard",
    ),
    path(
        "course/<int:course_id>/students/",
        views.course_students,
        name="course_students",
    ),
    # --- SINAV İŞLEMLERİ ---
    path(
        "assessment/<int:assessment_id>/",
        views.assessment_detail,
        name="assessment_detail",
    ),
    path(
        "assessment/<int:assessment_id>/grades/",
        views.enter_grades,
        name="enter_grades",
    ),
    # --- PO EŞLEŞTİRME ---
    path("lo/<int:lo_id>/mapping/", views.lo_mapping_detail, name="lo_mapping_detail"),
    # YENİ EKLENEN: EŞLEŞTİRME SİLME LİNKİ
    path(
        "mapping/<int:mapping_id>/delete/",
        views.delete_outcome_mapping,
        name="delete_outcome_mapping",
    ),
    # --- ÖĞRENCİ PANELİ VE YÖNLENDİRMELER ---
    path("dashboard/redirect/", views.home_redirect, name="home_redirect"),
    path(
        "student/course/<int:course_id>/",
        views.student_course_dashboard,
        name="student_course_dashboard",
    ),
    path("student/courses/", views.student_course_list, name="student_course_list"),
    path(
        "student/general-success/",
        views.student_general_success,
        name="student_general_success",
    ),
]
