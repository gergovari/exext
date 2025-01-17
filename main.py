from extractor import ExerciseExtractor
from merger import ExerciseMerger

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

images = extractor.extract_all(["example.pdf", "example2.pdf"])

canvas = merger.summary("test.pdf", images)
canvas.save()
