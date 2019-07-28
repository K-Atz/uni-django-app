from django.urls import include, path
from .views import *

urlpatterns = [
    path("carrier/mini_profile/", CarrierMiniProfileListView.as_view()),
    path("carrier/terms/", CarrierTermsListView.as_view()),
    path("carrier/terms/<term_id>/", CarrierTermDetailsListView.as_view()),
    path("carrier/terms/gradessummary/<term_id>/", TermSummaryView.as_view()),
    path("carrier/terms/preregistration/<term_id>/", CarrierPreRegistrationView.as_view()),
    path("courses/<course_id>/", CourseInformationView.as_view()),
    path("carrier/records_summary/", CarrierRecordsSummaryView.as_view()),
    path("carrier/subfield_courses/", FieldCourseSubfieldRelationView.as_view()),
    path("departments/", DepartmentsView.as_view()),
    path("terms/", AllTermsView.as_view()),
    path("courses_schedule/<term_id>/<department_id>/", CoursesScheduleView.as_view()),
    path("course/<course_id>/student_list/", CourseStudentsListView.as_view()),
    path("course/<course_id>/grades/", StudentCourseGradesListView.as_view()),
]
