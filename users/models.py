from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum
from django_jalali.db import models as jmodels
from .utils import *


class UserLoginProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='user_login_profile')

    def __str__(self):
        return str(self.user)


class Student(models.Model):
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    pic = models.ImageField(
        upload_to='pic_folder/', default='pic_folder/no-img.jpg', validators=[validate_image_size])

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class College(models.Model):
    title = models.CharField(max_length=255, blank=False, unique=True)

    def __str__(self):
        return str(self.title)


class Department(models.Model):
    title = models.CharField(max_length=255, blank=False)
    college = models.ForeignKey(
        College, on_delete=models.CASCADE, related_name='departments')

    class Meta:
        unique_together = (("title", "college"))

    def __str__(self):
        return str(self.title)


class DegreeType(enum.Enum):
    KAARDANI = 0
    KARSHENASI = 1
    ARSHAD = 2
    DOCTORI = 3

    def conv(name):
        if name == 'KAARDANI':
            return 'کاردانی'
        if name == 'KARSHENASI':
            return 'کارشناسی'
        if name == 'ARSHAD':
            return 'ارشد'
        if name == 'DOCTORI':
            return 'دکتری'
        return ' '


class Field(models.Model):
    head_department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='main_fields')
    other_departments = models.ManyToManyField(
        Department, blank=True, related_name='fields')

    title = models.CharField(max_length=255, blank=False)
    degree = enum.EnumField(DegreeType, blank=False, null=False)

    class Meta:
        unique_together = (("head_department", "title", "degree"))

    def __str__(self):
        return str(self.title)


class Credit(models.Model):
    practical_units = models.PositiveSmallIntegerField(null=False, blank=False)
    theoritical_units = models.PositiveSmallIntegerField(
        null=False, blank=False)

    class Meta:
        unique_together = (("practical_units", "theoritical_units"))

    def __str__(self):
        return str(self.practical_units)+" Practical Units and "+str(self.theoritical_units)+" Theoritical Units"


class FieldCourse(models.Model):
    corequisites = models.ManyToManyField(
        'FieldCourse', blank=True, related_name='corequisite_for')
    prerequisites = models.ManyToManyField(
        'FieldCourse', blank=True, related_name='prerequisite_for')

    serial_number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=False)
    credit_detail = models.ForeignKey(
        Credit, on_delete=models.CASCADE, related_name='field_courses')

    @property
    def credit(self):
        return int(self.credit_detail.practical_units) + int(self.credit_detail.theoritical_units)

    def __str__(self):
        return str(self.title)


class Subfield(models.Model):
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name='subfields')
    field_courses = models.ManyToManyField(
        FieldCourse, blank=False, through='FieldCourseSubfieldRelation', related_name='subfields')

    title = models.CharField(max_length=255, blank=False)

    class Meta:
        unique_together = (("field", "title"))

    @property
    def full_title(self):
        return self.field.title + "، " + self.title

    def __str__(self):
        return str(self.title)


class FieldCourseType(enum.Enum):
    EKHTIARI = 0
    OMUMI = 1
    PAYE = 2
    ASLI = 3
    TAKHASOSI_EJBARI = 4

    def conv(name):
        if name == 'EKHTIARI':
            return 'اختیاری'
        if name == 'OMUMI':
            return 'عمومی'
        if name == 'PAYE':
            return 'پایه'
        if name == 'ASLI':
            return 'اصلی'
        if name == 'TAKHASOSI_EJBARI':
            return 'تخصصی اجباری'
        return ' '


class FieldCourseSubfieldRelation(models.Model):
    field_course = models.ForeignKey(FieldCourse, on_delete=models.CASCADE)
    subfield = models.ForeignKey(Subfield, on_delete=models.CASCADE)
    suggested_term = models.PositiveSmallIntegerField(blank=True, null=True)
    course_type_num = enum.EnumField(FieldCourseType, null=False, blank=False)

    @property
    def course_type(self):
        return get_key(FieldCourseType, self.course_type_num)

    class Meta:
        unique_together = (("field_course", "subfield"))

    def __str__(self):
        return ("[ "+str(self.field_course) + " ] for [ " + str(self.subfield) + " ] is [ "
                + self.course_type + " ]")


class CarrierStatusType(enum.Enum):
    STUDYING = 0
    GRADUATED = 1
    NOT_FINISHED = 2

    def conv(name):
        if name == 'STUDYING':
            return 'در حال تحصیل'
        if name == 'GRADUATED':
            return 'فارغ التحصیل'
        if name == 'NOT_FINISHED':
            return 'انصراف از تحصیل'
        return ' '


class Term(models.Model):
    objects = jmodels.jManager()
    start_date = jmodels.jDateField(null=False, blank=False)
    end_date = jmodels.jDateField(null=False, blank=False)

    @property
    def title(self):
        if self.start_date.month > self.end_date.month:
            return str(self.start_date.year) + " دوم"
        else:
            return str(self.start_date.year) + " اول"

    class Meta:
        unique_together = (("start_date", "end_date"))

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Term, self).__init__(* args, **kwargs)
        if self.start_date is not None:
            self.old_title = self.title
        else:
            self.old_title = " "

    def clean(self):
        if (self.end_date < self.start_date) or (self.end_date.year - self.start_date.year > 1):
            raise ValidationError("Invalid Term interval!")
        elif self.title != self.old_title and self.title in list(map(lambda x: x.title, Term.objects.all())):
            raise ValidationError(
                "A term with the title <%s> is already defined!" % self.title)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Term, self).save(*args, **kwargs)


class AdmissionType(enum.Enum):
    ROOZANEH = 0
    SHABANEH = 1
    MEHMAN = 2
    ENTEGHALI = 3

    def conv(name):
        if name == 'ROOZANEH':
            return 'روزانه'
        if name == 'SHABANEH':
            return 'شبانه'
        if name == 'MEHMAN':
            return 'مهمان'
        if name == 'ENTEGHALI':
            return 'انتقالی'
        return ' '


class Carrier(models.Model):
    login_profile = models.OneToOneField(
        UserLoginProfile, on_delete=models.CASCADE, related_name='carrier')
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='carriers')
    subfield = models.ForeignKey(
        Subfield, on_delete=models.CASCADE, related_name='carriers')
    pre_reg_field_courses = models.ManyToManyField(
        FieldCourse, blank=True, through='PreliminaryRegistration', related_name='carriers')

    @property
    def degree_type(self):
        return get_key(DegreeType, self.subfield.field.degree)

    @property
    def total_credits_taken(self):
        attends = Attend.objects.filter(
            carrier=self).filter(deleted_by_carrier=False)
        return sum(list(map(lambda x: x.course.field_course.credit, attends)))

    @property
    def total_credits_passed(self):
        attends = list(filter(lambda x: x.carrier == self and x.grade_status == get_key(
            GradeState, GradeState.PASSED), Attend.objects.all()))
        return sum(list(map(lambda x: x.course.field_course.credit, attends)))

    @property
    def average(self):
        attends = list(filter(lambda x: x.carrier ==
                              self and x.grade != None, Attend.objects.all()))
        attends = list(map(lambda x: (x.course.field_course.credit,
                                      x.grade * x.course.field_course.credit), attends))
        total_credits = sum(list(map(lambda x: x[0], attends)))
        if total_credits == 0:
            return None
        return sum(list(map(lambda x: x[1], attends))) / total_credits

    @property
    def terms(self):
        carrier_terms = list(
            map(lambda x: x.term, self.registered_courses.all()))
        carrier_terms += list(map(lambda x: x.term,
                                  self.pre_reg_relations.all()))
        carrier_terms = list(set(carrier_terms))
        carrier_terms.sort(key=lambda x: x.title)
        return carrier_terms

    @property
    def entry_year(self):
        if len(self.terms) == 0:
            return None
        return self.terms[0].start_date.year

    id = models.IntegerField(primary_key=True)
    status = enum.EnumField(CarrierStatusType, blank=False)
    admission_type_num = enum.EnumField(AdmissionType, blank=False)

    @property
    def admission_type(self):
        return get_key(AdmissionType, self.admission_type_num)

    def __str__(self):
        return str(self.student)+" | "+str(self.subfield)


class Professor(models.Model):
    nickname = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return str(self.nickname) + " " + str(self.first_name) + " " + str(self.last_name)


class GenderTypeAllowed(enum.Enum):
    NOT_DEFINED = 0
    MALE = 1
    FEMALE = 2
    BOTH = 3

    def conv(name):
        if name == 'NOT_DEFINED':
            return 'تعیین نشده'
        if name == 'MALE':
            return 'مرد'
        if name == 'FEMALE':
            return 'زن'
        if name == 'BOTH':
            return 'مختلط'
        return ' '


class DayRange(models.Model):
    start = models.TimeField(blank=False, null=False)
    end = models.TimeField(blank=False, null=False)

    class Meta:
        unique_together = (("start", "end"))

    def __str__(self):
        return "Start: "+str(self.start)+" | End: "+str(self.end)


class Day(enum.Enum):
    SATURDAY = 0
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6

    def conv(name):
        if name == 'SATURDAY':
            return 'شنبه'
        if name == 'SUNDAY':
            return 'یکشنبه'
        if name == 'MONDAY':
            return 'دوشنبه'
        if name == 'TUESDAY':
            return 'سه شنبه'
        if name == 'WEDNESDAY':
            return 'چهارشنبه'
        if name == 'THURSDAY':
            return 'پنجشنبه'
        if name == 'FRIDAY':
            return 'جمعه'
        return ' '


class DayTime(models.Model):
    day_range = models.ForeignKey(DayRange, on_delete=models.CASCADE)
    day = enum.EnumField(Day, blank=False, null=False)

    class Meta:
        unique_together = (("day_range", "day"))

    @property
    def day_p(self):
        return get_key(Day, self.day)

    def __str__(self):
        return str(self.day_range)+" | Day: " + self.day_p


class ExamDate(models.Model):
    day_range = models.ForeignKey(DayRange, on_delete=models.CASCADE)
    day = jmodels.jDateField(blank=False, null=False)

    class Meta:
        unique_together = (("day_range", "day"))

    def __str__(self):
        return str(self.day_range)+" | Date: " + str(self.day)


class Room(models.Model):
    title = models.CharField(max_length=255, blank=False)
    place = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.title + " " + self.place

    class Meta:
        unique_together = (("title", "place"))


class CourseGradesStatus(enum.Enum):
    NOT_SENT = 0
    SENT = 1
    APPROVED = 2

    def conv(name):
        if name == 'NOT_SENT':
            return 'ارسال نشده'
        if name == 'SENT':
            return 'ارسال شده'
        if name == 'APPROVED':
            return 'وصول شده'
        return ' '


class Course(models.Model):
    field_course = models.ForeignKey(
        FieldCourse, on_delete=models.CASCADE, related_name='courses')
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='courses')
    subfields = models.ManyToManyField(
        Subfield, blank=True, related_name='allowed_courses', verbose_name='Subfields allowed to register the course')
    departments = models.ManyToManyField(
        Department, blank=True, related_name='allowed_courses', verbose_name='Departments allowed to register the course')
    professors = models.ManyToManyField(
        Professor, blank=False, through='Teach', related_name='courses')
    carriers = models.ManyToManyField(
        Carrier, blank=True, through='Attend', related_name='registered_courses')
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name='courses')
    grades_status_num = enum.EnumField(
        CourseGradesStatus, blank=False, null=False)

    @property
    def subfields_allowed_to_register(self):
        temp_list = []
        for item in self.subfields.all():
            temp_list += [item.full_title]
        return temp_list

    @property
    def departments_allowed_to_register(self):
        temp_list = []
        for item in self.departments.all():
            temp_list += [item.title]
        return temp_list

    @property
    def professors_list(self):
        relations = Teach.objects.filter(course__pk=self.pk)
        prof_list = []
        for item in relations:
            prof_list += [{
                'professor': str(item.professor),
                'percentage': item.percentage
            }]
        return prof_list

    @property
    def are_grades_approved(self):
        if self.grades_status_num == CourseGradesStatus.APPROVED:
            return True
        return False

    @property
    def grades_average(self):
        if not self.are_grades_approved:
            return None
        grades = list(map(lambda x: x.grade, self.attend_instances.all()))
        grades = list(filter(lambda x: x != None, grades))
        if len(grades) == 0:
            return None
        return round(sum(grades)/len(grades),2)

    @property
    def min_grade(self):
        if not self.are_grades_approved:
            return None
        grades = list(map(lambda x: x.grade, self.attend_instances.all()))
        grades = list(filter(lambda x: x != None, grades))
        if len(grades) == 0:
            return None
        return min(grades)

    @property
    def max_grade(self):
        if not self.are_grades_approved:
            return None
        grades = list(map(lambda x: x.grade, self.attend_instances.all()))
        grades = list(filter(lambda x: x != None, grades))
        if len(grades) == 0:
            return None
        return max(grades)

    @property
    def grades_status(self):
        return get_key(CourseGradesStatus, self.grades_status_num)
    objects = jmodels.jManager()
    midterm_exam_date = models.ForeignKey(
        ExamDate, on_delete=models.CASCADE, related_name='midterm_exams', null=True, blank=True)
    final_exam_date = models.ForeignKey(
        ExamDate, on_delete=models.CASCADE, related_name='final_exams', null=True, blank=True)
    section_number = models.PositiveSmallIntegerField(blank=False, null=False)
    capacity = models.PositiveSmallIntegerField(blank=False, null=False)
    students_gender = enum.EnumField(
        GenderTypeAllowed, blank=False, null=False, verbose_name='Genders allowed to register the course')
    weekly_schedule = models.ManyToManyField(
        DayTime, blank=False,  through='DayTimeCourseRelation', related_name='courses')
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='courses')

    @property
    def genders_allowed(self):
        return get_key(GenderTypeAllowed, self.students_gender)

    @property
    def class_times(self):
        temp_list = []
        for item in self.weekly_schedule.all():
            temp_list += [{
                'day': item.day_p,
                'start': item.day_range.start,
                'end': item.day_range.end
            }]
        return temp_list

    @property
    def number_of_students_registered(self):
        temp = self.attend_instances.filter(deleted_by_carrier=False)
        return len(temp)

    class Meta:
        unique_together = (("field_course", "term", "section_number"))

    def __str__(self):
        return str(self.field_course)+" | گروه "+str(self.section_number)


class DayTimeCourseRelation(models.Model):
    day_time = models.ForeignKey(DayTime, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("day_time", "course"))

    def __str__(self):
        return "Course: [ "+str(self.course)+" ]  Time: [ "+str(self.day_time)+" ]"


class Teach(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    percentage = models.PositiveSmallIntegerField(null=False, blank=False)

    @property
    def term(self):
        return self.course.term

    def __str__(self):
        return "[ "+str(self.professor) + " ] teaches [ " + str(self.course) + " ]"


class PreliminaryRegistration(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    field_course = models.ForeignKey(FieldCourse, on_delete=models.CASCADE)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.CASCADE, related_name="pre_reg_relations")

    def __str__(self):
        return "Preregistration of [ "+str(self.carrier)+" ] in [ "+str(self.field_course)+" ]"


class CourseApprovalState(enum.Enum):
    NOT_APPROVED = 0
    APPROVED = 1

    def conv(name):
        if name == 'NOT_APPROVED':
            return 'تایید نشده'
        if name == 'APPROVED':
            return 'تایید شده'
        return ' '


class GradeState(enum.Enum):
    NOT_DEFINED = 0
    PASSED = 1
    FAILED = 2

    def conv(name):
        if name == 'NOT_DEFINED':
            return 'تعیین نشده'
        if name == 'PASSED':
            return 'قبول'
        if name == 'FAILED':
            return 'مردود'
        return ' '


class Attend(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="attend_instances")
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    status = enum.EnumField(CourseApprovalState, null=False, blank=False)
    deleted_by_carrier = models.BooleanField(default=False)

    @property
    def carrier_course_status(self):
        return get_key(CourseApprovalState, self.status)

    @property
    def carrier_course_removal_status(self):
        if self.deleted_by_carrier:
            return 'حذف'
        return None

    @property
    def grade_status(self):
        if self.deleted_by_carrier:
            return None
        if not self.course.are_grades_approved:
            return None
        if self.grade == None:
            return get_key(GradeState, GradeState.NOT_DEFINED)
        elif self.grade >= 10:
            return get_key(GradeState, GradeState.PASSED)
        return get_key(GradeState, GradeState.FAILED)

    @property
    def grade(self):
        if self.deleted_by_carrier:
            return None
        if not self.course.are_grades_approved:
            return None
        sum = 0.0
        for item in self.grades.all():
            sum += (item.value / item.base_value) * item.out_of_twenty
        return round(sum,2)

    @property
    def course_type_for_carrier(self):
        qs = self.carrier.subfield.fieldcoursesubfieldrelation_set.filter(
            field_course=self.course.field_course)
        if len(qs) == 0:
            return None
        return qs[0].course_type

    class Meta:
        unique_together = (("course", "carrier"))

    def __str__(self):
        return "[ "+str(self.carrier) + " ] attends [ " + str(self.course) + " ]"


class Grade(models.Model):
    objects = jmodels.jManager()
    out_of_twenty = models.FloatField(
        null=False, blank=False, default=20.0)  # az 20 nomre
    value = models.FloatField(null=False, blank=False, default=0.0)
    base_value = models.FloatField(null=False, blank=False, default=20.0)
    date_examined = jmodels.jDateField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    attend = models.ForeignKey(
        Attend, on_delete=models.CASCADE, related_name="grades")

    @property
    def percentage(self):
        return self.out_of_twenty*100/20.0

    @property
    def carrier(self):
        return self.attend.carrier

    @property
    def course(self):
        return self.attend.course

    def __str__(self):
        return "Grade for: "+str(self.attend)+" | Title :"+str(self.title)
