from google_service import GoogleHandler
from classroom import ClassroomHandler
from drive import DriveHandler
from pdfmanager import PDFManager

from stui import STUI

from extractor import ExerciseExtractor
from merger import ExerciseMerger

google = GoogleHandler()
classroom = ClassroomHandler(google)
drive = DriveHandler(google)
pdfmng = PDFManager()

ui = STUI(classroom, drive, pdfmng)

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

docs = pdfmng.blobs_to_pdfs(ui.choose_pdfs())
#docs = ["test1.pdf"]

def merge_pdfs(extractor, merger, docs, output):
	exercises = extractor.extract_all(docs, include_titles = True)
	canvas = merger.practice(output, exercises)
	canvas.save()
merge_pdfs(extractor, merger, docs, "summary_all.pdf")
