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
    # 1. Ana Panel (Genel İstatistikler) - EKSİKTİ, EKLENDİ
    path("dashboard/", views.teacher_dashboard_home, name="teacher_dashboard_home"),
    # 2. Ders Listesi
    path("courses/", views.teacher_courses, name="teacher_courses"),
    # 3. Tüm Sınavlar
    path("exams/", views.exam_list, name="exam_list"),
    # --- DERS DETAYLARI ---
    path(
        "course/<int:course_id>/dashboard/",
        views.course_dashboard,
        name="course_dashboard",
    ),
    # --- ÖĞRENCİ YÖNETİMİ (Kritik Eksik Buydu!) ---
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
]
