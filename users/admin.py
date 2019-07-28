from django.contrib import admin
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin

admin.site.register(UserLoginProfile)
admin.site.register(Student)
admin.site.register(College)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'college']
admin.site.register(Department, DepartmentAdmin)


admin.site.register(Field)
admin.site.register(FieldCourse)
admin.site.register(Subfield)


class FieldCourseSubfieldRelationAdmin(admin.ModelAdmin):
    list_display = ['field_course', 'subfield', 'course_type']


admin.site.register(FieldCourseSubfieldRelation,
                    FieldCourseSubfieldRelationAdmin)

admin.site.register(Carrier)
admin.site.register(Professor)


class JTerm(admin.ModelAdmin):
    list_display = ['pk', 'title', 'start_date', 'end_date']
    list_filter = (
        ('start_date', JDateFieldListFilter),
        ('end_date', JDateFieldListFilter)
    )


admin.site.register(Term, JTerm)


class CourseAdmin(admin.ModelAdmin):
    list_display = ['field_course', 'section_number', 'term']
    list_filter = (
        ('midterm_exam_date', JDateFieldListFilter),
        ('final_exam_date', JDateFieldListFilter)
    )


admin.site.register(Course, CourseAdmin)


class TeachAdmin(admin.ModelAdmin):
    list_display = ['pk', 'professor', 'course', 'term']


admin.site.register(Teach, TeachAdmin)


class PrRegAdmin(admin.ModelAdmin):
    list_display = ['pk', 'carrier', 'field_course', 'term']


admin.site.register(PreliminaryRegistration, PrRegAdmin)


class AttendAdmin(admin.ModelAdmin):
    list_display = ['carrier', 'course', 'carrier_course_status']


admin.site.register(Attend, AttendAdmin)

admin.site.register(Credit)
admin.site.register(DayRange)


class DayTimeAdmin(admin.ModelAdmin):
    list_display = ['day_p', 'day_range']


admin.site.register(DayTime, DayTimeAdmin)


class DayTimeCourseRelationAdmin(admin.ModelAdmin):
    list_display = ['course', 'day_time']


admin.site.register(DayTimeCourseRelation, DayTimeCourseRelationAdmin)


class JGrade(admin.ModelAdmin):
    list_display = ['pk', 'carrier', 'course', 'title']
    list_filter = (
        ('date_examined', JDateFieldListFilter),
    )


admin.site.register(Grade, JGrade)


class RoomAdmin(admin.ModelAdmin):
    list_display = ['title', 'place']


admin.site.register(Room, RoomAdmin)

class ExamDateAdmin(admin.ModelAdmin):
    list_display = ['day_range', 'day']
admin.site.register(ExamDate, ExamDateAdmin)