from extractor import ExerciseExtractor

start = 1
extractor = ExerciseExtractor("example.pdf", -30)

images = extractor.extract_all()
