from google_service import GoogleHandler
from classroom import ClassroomHandler
from drive import DriveHandler
from pdfmanager import PDFManager

from stui import STUI

from extractor import ExerciseExtractor
from merger import ExerciseMerger

import ray

from itertools import chain

google = GoogleHandler()
classroom = ClassroomHandler(google)
drive = DriveHandler(google)
pdfmng = PDFManager()

ui = STUI(classroom, drive, pdfmng)

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

from datetime import datetime
from dateutil import parser

# TODO: filter config
def _is_assignment_included(assignment):
	cutoff = datetime(2022, 9, 1)
	return parser.parse(assignment["creationTime"]).timestamp() >= cutoff.timestamp()

course = ui.choose_course(classroom.get_courses())

assignments_gen = classroom.get_assignments.remote(classroom, course)
tasks = []
for assignment in ray.get(assignments_gen):
	if _is_assignment_included(ray.get(assignment)):
		files = classroom.assignment_to_files.remote(classroom, assignment)
		for file in ray.get(files):
			blob = drive.file_to_blob.remote(drive, file)
			path = pdfmng.blob_to_path.remote(pdfmng, blob)
			tasks.append(extractor.path_to_exercises.remote(extractor, path, include_title = True))

exercises = list(chain.from_iterable(ray.get(tasks)))

canvas = merger.practice("new.pdf", exercises)
canvas.save()
