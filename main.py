import argparse
from report_card_generator import Report_Card_Generator


def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('course_file_path',
                        help='the course.csv file', type=str)
    parser.add_argument('student_file_path',
                        help='the students.json file', type=str)
    parser.add_argument('tests_file_path', help='the test.csv file', type=str)
    parser.add_argument('marks_file_path', help='the marks.csv file', type=str)
    parser.add_argument('output_file_path',
                        help='the output.json file', type=str)

    args = parser.parse_args()

    course_file_path = args.course_file_path
    student_file_path = args.student_file_path
    tests_file_path = args.tests_file_path
    marks_file_path = args.marks_file_path
    output_file_path = args.output_file_path

    report = Report_Card_Generator(
        course_file_path, student_file_path, tests_file_path, marks_file_path, output_file_path)
    report.generate_output_file()


if __name__ == '__main__':
    Main()
