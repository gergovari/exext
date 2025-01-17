from extractor import ExerciseExtractor
from merger import ExerciseMerger

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

exercises = extractor.extract_all(["example.pdf", "example2.pdf"], include_titles = True)

#canvas = merger.summary("test.pdf", images)
canvas = merger.practice("test.pdf", exercises)
canvas.save()
