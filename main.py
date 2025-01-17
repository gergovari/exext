from extractor import ExerciseExtractor
from merger import ExerciseMerger

extractor = ExerciseExtractor("example.pdf", 1, -30)
merger = ExerciseMerger("test.pdf")

images = extractor.extract_all()

merger.summary(images)
