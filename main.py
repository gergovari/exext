from extractor import ExerciseExtractor
from merger import ExerciseMerger

from google_service import GoogleHandler
from classroom import ClassroomHandler
from drive import DriveHandler
from pdfmanager import PDFManager

def choose_docs(classroom, drive, pdfmng):
	courses = classroom.get_courses()
	course = courses[5]

	assignments = classroom.get_assignments(course)
	assignment = assignments[1]

	files = []
	for material in assignment["materials"]:
		files.append(material["driveFile"]["driveFile"])

	docs = []
	for file in files:
		docs.append(pdfmng.blob_to_pdf(drive.get_file_as_pdf(file)))
	return docs

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

merge_docs_to_pdf(extractor, merger, choose_docs(classroom, drive, pdfmng), "summary_all.pdf")
