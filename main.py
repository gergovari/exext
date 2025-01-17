from extractor import ExerciseExtractor
from merger import ExerciseMerger

from google_service import GoogleHandler
from classroom import ClassroomHandler
from drive import DriveHandler
from pdfmanager import PDFManager

from datetime import datetime
from dateutil import parser

# TODO: filter by title
def assignments_to_materials(assignments):
	materials = []
	for assignment in assignments:
		try:
			materials += assignment["materials"]
		except KeyError:
			continue
	return materials
def materials_to_files(materials):
	files = []
	for material in materials:
		try:
			files.append(material["driveFile"]["driveFile"])
		except KeyError:
			continue
	return files
def files_to_docs(files):
	docs = []
	for file in files:
		docs.append(pdfmng.blob_to_pdf(drive.get_file_as_pdf(file)))
	return docs

# TODO: filter by title
def filter_assignments(assignments):
	cutoff = datetime(2022, 9, 1)
	return [assignment for assignment in assignments if parser.parse(assignment["creationTime"]).timestamp()>= cutoff.timestamp()]

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
	assignments = filter_assignments(classroom.get_assignments(course))
	materials = assignments_to_materials(assignments)
	files = materials_to_files(materials)
	return files_to_docs(files)

def merge_docs_to_pdf(extractor, merger, docs, output):
	exercises = extractor.extract_all(docs, include_titles = True)
	canvas = merger.summary(output, exercises)
	canvas.save()

google = GoogleHandler()
classroom = ClassroomHandler(google)
drive = DriveHandler(google)
pdfmng = PDFManager()

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

#docs = choose_docs(classroom, drive, pdfmng)
docs = ["example.pdf"]

merge_docs_to_pdf(extractor, merger, docs, "summary_all.pdf")
