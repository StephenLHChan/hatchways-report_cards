import csv
import json


class Report_Card_Generator:
    def __init__(self, course_file_path: str, student_file_path: str, tests_file_path: str, marks_file_path: str, output_file_path: str):
        self.course_file_path = course_file_path
        self.student_file_path = student_file_path
        self.tests_file_path = tests_file_path
        self.marks_file_path = marks_file_path
        self.output_file_path = output_file_path

        self.student_data = self.__read_students_csv()
        self.courses_data = self.__read_courses_csv()
        self.tests_data = self.__read_tests_csv()
        self.test_mark_data = self.__merge_marks_with_test()
        self.students_performance = self.__get_students_performance()
        self.output_file = self.generate_output_file()

    # output = {id : [course_id, weight]}
    def __read_tests_csv(self,) -> dict:
        tests_data = {}
        with open(self.tests_file_path, 'r') as tests_file:
            tests_reader = csv.DictReader(tests_file)

            for record in tests_reader:
                tests_data[int(record['id'])] = [
                    int(record['course_id']), float(record['weight'])]
        return tests_data

    # output: [test_id, student_id, mark, course_id, weight]
    def __merge_marks_with_test(self,) -> list:
        test_data = self.tests_data
        marks_data = []
        with open(self.marks_file_path, 'r') as marks_file:
            marks_reader = csv.DictReader(marks_file)

            for record in marks_reader:
                marks_data_row = [int(record['test_id']),
                                  int(record['student_id']), float(record['mark'])]
                marks_data_row.extend(test_data.get(marks_data_row[0]))
                marks_data.append(marks_data_row)
        return marks_data

    # output: {id:[name, teacher]}
    def __read_courses_csv(self,) -> dict:
        courses_data = {}
        with open(self.course_file_path, 'r') as courses_file:
            courses_reader = csv.DictReader(courses_file)

            for record in courses_reader:
                courses_data[int(record['id'])] = [
                    record['name'], record['teacher']]
        return courses_data

    # output: {id : name}
    def __read_students_csv(self,) -> dict:
        students_data = {}
        with open(self.student_file_path, 'r') as students_file:
            students_reader = csv.DictReader(students_file)

            for record in students_reader:
                students_data[int(record['id'])] = record['name']
        return students_data

    # output: { student_id: {course_id : averageCourseMark}}
    def __get_students_performance(self,) -> dict:

        def get_weighted_mark(mark: float, weight: float) -> float:
            return mark * weight / 100

        students_performance = {}
        for record in self.test_mark_data:
            student_id = record[1]
            mark = record[2]
            course_id = record[3]
            weight = record[-1]

            course_mark_map = {}

            if student_id not in students_performance:
                students_performance[student_id] = course_mark_map
                if(course_id not in course_mark_map):
                    course_mark_map[course_id] = get_weighted_mark(
                        mark, weight)
                else:
                    course_mark_map[course_id] += get_weighted_mark(
                        mark, weight)

            else:
                course_mark_map = students_performance[student_id]
                if (course_id not in course_mark_map):
                    course_mark_map[course_id] = get_weighted_mark(
                        mark, weight)
                else:
                    course_mark_map[course_id] += get_weighted_mark(
                        mark, weight)

        return students_performance

    def __calculate_total_average(self, student_id: int) -> float:
        sum = 0.0
        courses_performance = self.students_performance[student_id]
        for course in courses_performance.keys():
            sum += courses_performance[course]
        return sum / len(courses_performance)

    def __generate_output_content(self) -> dict:
        students_performance = self.students_performance
        student_list = []

        for student_id in sorted(students_performance.keys()):
            student = {}
            student['id'] = student_id
            student['name'] = self.student_data[student_id]
            student['totalAverage'] = round(
                self.__calculate_total_average(student_id), 2)
            courses_list = []
            for course_id in students_performance[student_id].keys():
                course = {}
                course['id'] = course_id
                course['name'] = self.courses_data[course_id][0]
                course['teacher'] = self.courses_data[course_id][1]
                course['courseAverage'] = round(
                    students_performance[student_id][course_id], 2)
                courses_list.append(course)
            student['courses'] = courses_list
            student_list.append(student)

        output = {}
        output['students'] = student_list
        return output

    def __generate_error_content(self) -> dict:
        return {'error': 'Invalid course weights'}

    def generate_output_file(self) -> None:
        output_content = self.__generate_output_content() if self.__is_weigth_valid(
        ) else self.__generate_error_content()
        with open(self.output_file_path, 'w') as output_file:
            output_file.write(json.dumps(output_content, indent=4))

    def __is_weigth_valid(self) -> bool:
        tests_data = self.tests_data
        course_weight_total = {}
        for test_weight_pair in tests_data.values():
            if test_weight_pair[0] not in course_weight_total:
                course_weight_total[test_weight_pair[0]] = test_weight_pair[1]
            else:
                course_weight_total[test_weight_pair[0]] += test_weight_pair[1]

        for weight_total in course_weight_total.values():
            if weight_total != 100:
                return False
        return True
