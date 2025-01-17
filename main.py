from extractor import ExerciseExtractor
from merger import ExerciseMerger

from google_service import GoogleHandler
from classroom import ClassroomHandler
from drive import DriveHandler
from pdfmanager import PDFManager

from datetime import datetime
from dateutil import parser

# TODO: filter config
def filter_assignments(assignments):
	cutoff = datetime(2023, 6, 1)
	return [assignment for assignment in assignments if parser.parse(assignment["creationTime"]).timestamp() >= cutoff.timestamp()]

def choose_elem(elems):
	for i, elem in enumerate(elems):
		name = elem.get("name", elem.get("title", str(elem)))
		print(f"{i}: {name}")
	while True:
		try:
			return elems[int(input("Selection: "))]
		except IndexError:
			print("Invalid input, choose from the numbers above!")
def choose_course():
	courses = classroom.get_courses()
	return choose_elem(courses)
def choose_docs(classroom, drive, pdfmng):
	course = choose_course()
	assignments = filter_assignments(classroom.get_assignments(course) + classroom.get_announcements(course))
	print(f"Assignments: {len(assignments)}")
	return classroom.assignments_to_docs(assignments)

def merge_docs_to_pdf(extractor, merger, docs, output):
	exercises = extractor.extract_all(docs, include_titles = True)
	canvas = merger.practice(output, exercises)
	canvas.save()

google = GoogleHandler()
classroom = ClassroomHandler(google)
drive = DriveHandler(google)
pdfmng = PDFManager()

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

docs = choose_docs(classroom, drive, pdfmng)
#docs = ["test1.pdf"]

merge_docs_to_pdf(extractor, merger, docs, "summary_all.pdf")
