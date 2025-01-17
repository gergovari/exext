import pdfplumber
from PIL import Image
from dataclasses import dataclass
import re

class ExtractionError(Exception):    
	pass

@dataclass
class Exercise:
	start: (int, int)
	end: (int, int)
	title: bool = False
	image: Image = None
	
class ExerciseExtractor:
	def __init__(self, 
			crop_start_offset = 0, 
			crop_end_offset = 0, 
			crop_stitch_gap_start = 0, 
			crop_stitch_gap_end = 0, 
			quality = 300, 
			regex = r"^[1-9]\d*\.",
			title_regex = r"\d{2}\.\d{2}\."
		):
		self.crop_start_offset = crop_start_offset
		self.crop_end_offset = crop_end_offset
		self.crop_stitch_gap_start = crop_stitch_gap_start
		self.crop_stitch_gap_end = crop_stitch_gap_end
		self.quality = quality
		self.regex = re.compile(regex, re.MULTILINE)
		self.title_regex = title_regex

	def _get_total_image_size(self, images):
		widths, heights = zip(*(image.size for image in images))
		return (max(widths), sum(heights))
	def _stitch_images(self, images):
		final = Image.new("RGB", self._get_total_image_size(images))
		offset = 0
		for image in images:
			final.paste(image, (0, offset))
			offset += image.size[1]
		return final
	
	def _find_text_y_coord(self, page, text, occurence = 0, light_match = False, location = "top"):
		current = 0
		for obj in page.extract_words():
			if (obj["text"] == text or obj["text"][:len(text)] == text) or (light_match and text in obj["text"]):
				if current >= occurence:
					return obj[location]
				else:
					current += 1

	def _find_top_y_coord(self, page):
		try:
			obj = page.extract_words()[0]
			return obj["top"]
		except IndexError:
			return None
			

	def _find_bottom_y_coord(self, page):
		try:
			obj = page.extract_words()[-1]
			return obj["bottom"]
		except IndexError:
			return None

	def _crop_page(self, page, start, end, offset_override = (None, None)):
		try:
			start += offset_override[0] if offset_override[0] != None else self.crop_start_offset
			end += offset_override[1] if offset_override[1] != None else self.crop_end_offset
		except:
			raise ExtractionError
		if start < 0:
			start = 0
		if end > page.height:
			end = page.height
		try:
			return page.crop((0, start, page.width, end))
		except:
			raise ExtractionError
	def _crop_all(self, page):
		return self._crop_page(page, self._find_top_y_coord(page), self._find_bottom_y_coord(page))

	def _get_all_exercises(self, pdf, include_title = False):
		exercises = []
		overflow = None
		for i, page in enumerate(pdf.pages):
			page_text = page.extract_text()
			if len(page.extract_words()) > 0:
				matches = re.findall(self.regex, page_text)

				if i == 0 and include_title:
					try:
						title = re.findall(self.title_regex, page_text)[0]
						exercises.append(
							Exercise(
								(0, self._find_text_y_coord(page, title, 0, True)), 
								(0, self._find_text_y_coord(page, title, 0, True, "bottom")),
								True
							)
						)
					except IndexError:
						pass

				if overflow:
					if len(matches) <= 0:
						overflow.end = (i, 
							self._find_bottom_y_coord(page))
					else:
						overflow.end = (i, 
							self._find_text_y_coord(page, matches[0]))
					exercises.append(overflow)
					overflow = None
				for j, text in enumerate(matches):
					y = self._find_text_y_coord(page, text, matches[:j].count(text))
					if y:
						start = (i, y)
						exercise = Exercise(start, None)

						if len(matches) <= j + 1:
							exercise.end = (i, self._find_bottom_y_coord(page))
							if len(pdf.pages) <= i + 1:
								exercises.append(exercise)
							else:
								overflow = exercise
						else:
							target = matches[j + 1]
							exercise.end = (i, self._find_text_y_coord(page, 
								target, matches[:j].count(target)))
							exercises.append(exercise)
		return exercises

	def _extract_all_pages(self, pdf):
		exercises = []
		for page in pdf.pages:
			exercise = Exercise(None, None, False, self._crop_all(page).to_image(resolution=self.quality).original)
			exercises.append(exercise)
		return exercises
	
	def _is_pdf_complex(self, exercises):
		threshold = 10
		for a in exercises:
			for b in exercises:
				if a.start[0] == b.start[0] and abs(a.start[1] - b.start[1]) <= threshold and a != b:
					return True
		return False


	def extract(self, pdf, exercise):
		pages = pdf.pages[exercise.start[0]:exercise.end[0] + 1]
		images = []
		for i, page in enumerate(pages):
			if len(pages) > 1:
				if i == 0:
					cropped = self._crop_page(page, 
						exercise.start[1], 
						self._find_bottom_y_coord(page), (None, self.crop_stitch_gap_start))
				elif i + 1 >= len(pages):
					cropped = self._crop_page(page, 
						self._find_top_y_coord(page), 
						exercise.end[1], (0, self.crop_stitch_gap_end))
				else:
					cropped = page
			else:
				cropped = self._crop_page(page, exercise.start[1], exercise.end[1])
			images.append(cropped.to_image(resolution=self.quality).original)
		exercise.image = self._stitch_images(images)
		return exercise
	
	def extract_all(self, paths, include_titles = False):
		exercises = []
		for i, path in enumerate(paths):
			print()
			print()
			with pdfplumber.open(path) as pdf:
				print(f"Opening PDF: {i+1}/{len(paths)} ({round(((i+1)/len(paths))*100, 2)}%): {pdf.metadata['Title']}")
				try:
					raw_exercises = self._get_all_exercises(pdf, include_titles)
					if self._is_pdf_complex(raw_exercises):
						print("PDF is too complex to parse!")
						exercises += self._extract_all_pages(pdf)
					else:
						for j, raw_exercise in enumerate(raw_exercises):
							try:
								exercises.append(self.extract(pdf, raw_exercise))
								print(f"Extracted exercise: {j+1}/{len(raw_exercises)} ({round(((j+1)/len(raw_exercises))*100, 2)}%)")
							except ExtractionError:
								print()
								print(f"Extraction error at {j+1}")
								print()
						if len(exercises) <= 0:
							print("Can't detect exercises in PDF!")
							exercises += self._extract_all_pages(pdf)
						elif len(exercises) <= 1 and exercises[0].title:
							print("Can't detect exercises in PDF, only title!")
							del exercises[0]
							exercises += self._extract_all_pages(pdf)
				except ExtractionError:
					print()
					print(f"Extraction error at {pdf.metadata['Title']}")
					print()
		return exercises
