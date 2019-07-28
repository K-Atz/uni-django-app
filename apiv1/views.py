from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from users.models import *
from users.utils import *
from rest_framework.permissions import IsAuthenticated


class CarrierMiniProfileListView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = CarrierDetailSerializer

    def get_queryset(self):
        return Carrier.objects.filter(pk=self.request.user.user_login_profile.carrier.pk)


class CarrierTermsListView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TermDetailSerializer

    def get_queryset(self):
        return self.request.user.user_login_profile.carrier.terms


class CarrierTermDetailsListView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = AttendSerializer

    def get_queryset(self):
        term_id = self.kwargs['term_id']
        return Attend.objects.filter(course__term__pk=term_id, carrier=self.request.user.user_login_profile.carrier)


class CourseStudentsListView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = AttendSerializerNoPic

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Attend.objects.filter(course__pk=course_id)


class TermSummaryView(APIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):

        car = self.request.user.user_login_profile.carrier
        term_id = int(self.kwargs['term_id'])

        carrier_attends = list(filter(lambda attend: attend.course.term.pk == term_id
                                      and attend.carrier == car and not attend.deleted_by_carrier, Attend.objects.all()))

        field_attends = list(filter(lambda attend: attend.course.term.pk == term_id
                                    and attend.carrier.subfield.field == car.subfield.field
                                    and not attend.grade == None, Attend.objects.all()))
        department_attends = list(filter(lambda attend: attend.course.term.pk == term_id
                                         and attend.carrier.subfield.field.head_department == car.subfield.field.head_department
                                         and not attend.grade == None, Attend.objects.all()))
        college_attends = list(filter(lambda attend: attend.course.term.pk == term_id
                                      and attend.carrier.subfield.field.head_department.college == car.subfield.field.head_department.college
                                      and not attend.grade == None, Attend.objects.all()))

        mydata = {
            'total_credits_taken': 0,
            'total_credits_passed': 0,
            'carrier_average': 0.0,
            'field_average': 0.0,
            'department_average': 0.0,
            'college_average': 0.0
        }

        mydata["total_credits_taken"] = sum(
            list(map(lambda x: x.course.field_course.credit, carrier_attends)))

        carrier_attends = list(
            filter(lambda attend: attend.course.are_grades_approved, carrier_attends))
        temp = list(map(lambda x: (x.course.field_course.credit,
                                   x.course.field_course.credit * x.grade), carrier_attends))

        total_credits = sum(list(map(lambda x: x[0], temp)))
        if total_credits == 0:
            mydata["carrier_average"] = None
        else:
            mydata["carrier_average"] = round(sum(list(map(lambda x: x[1], temp))) / total_credits, 2)

        carrier_attends = list(filter(lambda attend: attend.grade_status == get_key(
            GradeState, GradeState.PASSED), carrier_attends))
        mydata["total_credits_passed"] = sum(
            list(map(lambda x: x.course.field_course.credit, carrier_attends)))

        temp = list(map(lambda x: (x.course.field_course.credit,
                                   x.course.field_course.credit * x.grade), field_attends))
        total_credits = sum(list(map(lambda x: x[0], temp)))
        if total_credits == 0:
            mydata["field_average"] = None
        else:
            mydata["field_average"] = round(sum(list(map(lambda x: x[1], temp))) / total_credits, 2)

        temp = list(map(lambda x: (x.course.field_course.credit,
                                   x.course.field_course.credit * x.grade), department_attends))
        total_credits = sum(list(map(lambda x: x[0], temp)))
        if total_credits == 0:
            mydata["department_average"] = None
        else:
            mydata["department_average"] = round(sum(list(map(lambda x: x[1], temp))) / total_credits, 2)

        temp = list(map(lambda x: (x.course.field_course.credit,
                                   x.course.field_course.credit * x.grade), college_attends))
        total_credits = sum(list(map(lambda x: x[0], temp)))
        if total_credits == 0:
            mydata["college_average"] = None
        else:
            mydata["college_average"] = round(sum(list(map(lambda x: x[1], temp))) / total_credits, 2)

        results = TermSummarySerializer(mydata, many=False).data
        return Response(results)


class CarrierPreRegistrationView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = PreRegistrationSerializer

    def get_queryset(self):
        term_id = self.kwargs['term_id']
        return PreliminaryRegistration.objects.filter(term__pk=term_id, carrier=self.request.user.user_login_profile.carrier)


class CourseInformationView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = CourseInformationSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Course.objects.filter(pk=course_id)


class CarrierRecordsSummaryView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        car = self.request.user.user_login_profile.carrier
        temp_list = []

        mydata = {
            'term_title': " ",
            'total_credits_taken': 0,
            'total_credits_passed': 0,
            'average': 0.0,
            'credits_considered_in_average': 0,
            'total_credits_taken_till_now': 0,
            'total_credits_passed_till_now': 0,
            'average_till_now': 0.0,
            'credits_considered_in_average_till_now': 0
        }

        i = -1
        for t in car.terms:
            i += 1

            carrier_attends = list(filter(lambda attend: attend.course.term.pk == t.pk
                                          and attend.carrier == car and not attend.deleted_by_carrier, Attend.objects.all()))

            mydata["term_title"] = t.title

            mydata["total_credits_taken"] = sum(
                list(map(lambda x: x.course.field_course.credit, carrier_attends)))

            carrier_attends = list(
                filter(lambda attend: attend.course.are_grades_approved, carrier_attends))
            temp = list(map(lambda x: (x.course.field_course.credit,
                                       x.course.field_course.credit * x.grade), carrier_attends))

            total_credits = sum(list(map(lambda x: x[0], temp)))
            mydata["credits_considered_in_average"] = total_credits
            if total_credits == 0:
                mydata["average"] = None
            else:
                mydata["average"] = round(sum(list(map(lambda x: x[1], temp))) / total_credits, 2)

            carrier_attends = list(filter(lambda attend: attend.grade_status == get_key(
                GradeState, GradeState.PASSED), carrier_attends))
            mydata["total_credits_passed"] = sum(
                list(map(lambda x: x.course.field_course.credit, carrier_attends)))

            if i == 0:
                mydata["total_credits_taken_till_now"] = mydata["total_credits_taken"]
                mydata["total_credits_passed_till_now"] = mydata["total_credits_passed"]
                mydata["average_till_now"] = mydata["average"]
                mydata["credits_considered_in_average_till_now"] = mydata["credits_considered_in_average"]
            else:
                mydata["total_credits_taken_till_now"] = mydata["total_credits_taken"] + \
                    temp_list[i-1]["total_credits_taken_till_now"]
                mydata["total_credits_passed_till_now"] = mydata["total_credits_passed"] + \
                    temp_list[i-1]["total_credits_passed_till_now"]
                mydata["credits_considered_in_average_till_now"] = mydata["credits_considered_in_average"] + \
                    temp_list[i-1]["credits_considered_in_average_till_now"]

                mydata["average_till_now"] = round((mydata["average"] * mydata["credits_considered_in_average"] + temp_list[i-1]["average_till_now"] * temp_list[i-1]["credits_considered_in_average_till_now"]) / (mydata["credits_considered_in_average"] + temp_list[i-1]["credits_considered_in_average_till_now"]),2)

            temp_list += [mydata.copy()]

        return Response(CarrierRecordsSummarySerializer(temp_list, many=True).data)


class FieldCourseSubfieldRelationView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = FieldCourseSubfieldRelationSerializer

    def get_queryset(self):
        carrier_subfield = self.request.user.user_login_profile.carrier.subfield
        return FieldCourseSubfieldRelation.objects.filter(subfield=carrier_subfield)


class DepartmentsView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.all()


class AllTermsView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TermDetailSerializer

    def get_queryset(self):
        temp_list = list(Term.objects.all())
        temp_list.sort(key=lambda x: x.title)
        return temp_list


class CoursesScheduleView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = CourseInformationSummarySerializer

    def get_queryset(self):
        term_id = self.kwargs['term_id']
        department_id = self.kwargs['department_id']

        return Course.objects.filter(department__pk=department_id, term__pk=term_id)



class StudentCourseGradesListView(ListAPIView):

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Grade.objects.filter(
            attend__course__pk=course_id, attend__carrier__pk=self.request.user.user_login_profile.carrier.pk)

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs['course_id']
        queryset = self.get_queryset()
        serializer = GradeSerializer(queryset, many=True)
        attend = Attend.objects.filter(
            course__pk=course_id, carrier__pk=self.request.user.user_login_profile.carrier.pk)
        grade = None
        if len(attend) != 0:
            grade = attend[0].grade
        if grade == None:
            grade = 0.0
        custom_dict = {
            "final_grade": grade
        }
        response_list = serializer.data 
        response_list.append(custom_dict)
        return Response(response_list)
