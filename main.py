from extractor import ExerciseExtractor
from merger import ExerciseMerger
from google_service import GoogleHandler
from classroom import ClassroomHandler
from drive import DriveHandler

def merge_docs_to_pdf(docs, output):
	extractor = ExerciseExtractor(-30, 0, 2, 15)
	merger = ExerciseMerger()
	exercises = extractor.extract_all(docs, include_titles = True)
	canvas = merger.summary(output, exercises)
	canvas.save()

google = GoogleHandler()
classroom = ClassroomHandler(google)
drive = DriveHandler(google)

def choose_docs(classroom, drive)
	courses = classroom.get_courses()
	course = courses[5]

	assignments = classroom.get_assignments(course)
	assignment = assignments[1]

	files = []
	for material in assignment["materials"]:
		files.append(material["driveFile"]["driveFile"])

	docs = []
	for file in files:
		docs.append(blob_to_pdf(drive.get_file_as_pdf(file)))
	return docs

merge_docs_to_pdf(docs, "summary_all.pdf")
