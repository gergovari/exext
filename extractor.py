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
			regex = r"\b([1-9]\d*\.)[^\S\r\n]",
			title_regex = r"\d{2}\.\d{2}\."
		):
		self.crop_start_offset = crop_start_offset
		self.crop_end_offset = crop_end_offset
		self.crop_stitch_gap_start = crop_stitch_gap_start
		self.crop_stitch_gap_end = crop_stitch_gap_end
		self.quality = quality
		self.regex = regex
		self.title_regex = title_regex
		self.occurence = {}

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
	
	def _find_text_y_coord(self, page, text, occurence = 0, light_match = False):
		current = 0
		for obj in page.extract_words():
			if obj["text"] == text or (light_match and text in obj["text"]):
				if current >= occurence:
					return obj["top"]
				else:
					current += 1

	def _find_top_y_coord(self, page):
		obj = page.extract_words()[0]
		return obj["top"]

	def _find_bottom_y_coord(self, page):
		obj = page.extract_words()[-1]
		return obj["bottom"]

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
		return page.crop((0, start, page.width, end))

	def _get_all_exercises(self, pdf, include_title = False):
		exercises = []
		overflow = None
		for i, page in enumerate(pdf.pages):
			matches = re.findall(self.regex, page.extract_text())

			if i == 0 and include_title:
				try:
					title = re.findall(self.title_regex, page.extract_text())[0]
					exercises.append(
						Exercise(
							(0, self._find_text_y_coord(page, title, 0, True)), 
							(0, self._find_text_y_coord(page, matches[0])),
							True
						)
					)
				except IndexError:
					pass

			if overflow:
				if len(matches) <= 0:
					overflow.end = (i, 
						self._find_bottom_y_coord(page))
					if len(pdf.pages) <= i + 1:
						exercises.append(overflow)
						overflow = None
				elif matches[0] in page.extract_words()[0]["text"]:
					exercises.append(overflow)
					overflow = None

			for j, text in enumerate(matches):
				if not text in self.occurence:
					self.occurence[text] = 0
				y = self._find_text_y_coord(page, text, self.occurence[text])
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
						if matches[j] == matches[j + 1]:
							self.occurence[text] += 1
						exercise.end = (i, self._find_text_y_coord(page, 
							matches[j + 1], self.occurence[text]))
						exercises.append(exercise)
		return exercises

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
		for path in paths:
			with pdfplumber.open(path) as pdf:
				raw_exercises = self._get_all_exercises(pdf, include_titles)
				for i, raw_exercise in enumerate(raw_exercises):
					try:
						exercises.append(self.extract(pdf, raw_exercise))
					except ExtractionError:
						print(f"Extraction error: {pdf.pages[0].extract_text()[:100]}")
		return exercises
