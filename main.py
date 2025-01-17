from extractor import ExerciseExtractor
from merger import ExerciseMerger

extractor = ExerciseExtractor(-30, 0, 2, 15)
merger = ExerciseMerger()

images = extractor.extract_all(["example2.pdf"])

for i, image in enumerate(images):
	image.save(f"test{i}.jpg")

#canvas = merger.summary("test.pdf", images)
#canvas.save()
