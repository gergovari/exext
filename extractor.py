import pdfplumber
from PIL import Image
from dataclasses import dataclass
import re

@dataclass
class Exercise:
	start: (int, int)
	end: (int, int)
	
class ExerciseExtractor:
	def __init__(self, 
			crop_start_offset = 0, 
			crop_end_offset = 0, 
			crop_stitch_gap_start = 0, 
			crop_stitch_gap_end = 0, 
			quality = 300, 
			regex = r"\b([1-9]\d*\.)\s"
		):
		self.crop_start_offset = crop_start_offset
		self.crop_end_offset = crop_end_offset
		self.crop_stitch_gap_start = crop_stitch_gap_start
		self.crop_stitch_gap_end = crop_stitch_gap_end
		self.quality = quality
		self.regex = regex

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
	
	def _find_text_y_coord(self, page, text):
		for obj in page.extract_words():
			if obj["text"] == text:
				return obj["top"]

	def _find_top_y_coord(self, page):
		obj = page.extract_words()[0]
		return obj["top"]

	def _find_bottom_y_coord(self, page):
		obj = page.extract_words()[-1]
		return obj["bottom"]

	def _crop_page(self, page, start, end, offset_override = (None, None)):
		start += offset_override[0] if offset_override[0] != None else self.crop_start_offset
		end += offset_override[1] if offset_override[1] != None else self.crop_end_offset
		if start < 0:
			start = 0
		if end > page.height:
			end = page.height
		return page.crop((0, start, page.width, end))

	def _get_all_exercises(self, pdf):
		exercises = []
		overflow = None
		for i, page in enumerate(pdf.pages):
			matches = re.findall(self.regex, page.extract_text())

			if overflow:
				if len(matches) <= 0:
					overflow.end = (i, 
						self._find_bottom_y_coord(page))
					if len(pdf.pages) <= i + 1:
						exercises.append(overflow)
						overflow = None
				elif matches[0] in page.extract_words()[0]:
					overflow.end = (i, self._find_text_y_coord(page, matches[0]))
					exercises.append(overflow)
					overflow = None
				else:
					continue

			for j, text in enumerate(matches):
				y = self._find_text_y_coord(page, text)
				if y:
					start = (i, y)
					exercise = Exercise(start, None)
					
					if len(matches) <= j + 1 and len(pdf.pages) > i + 1:
						exercise.end = (i, self._find_bottom_y_coord(page))
						overflow = exercise
					else:
						exercise.end = (i, self._find_text_y_coord(page, matches[j + 1]))
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
		return self._stitch_images(images)
	
	def extract_all(self, paths):
		images = []
		for path in paths:
			with pdfplumber.open(path) as pdf:
				exercises = self._get_all_exercises(pdf)
				for exercise in exercises:
					images.append(self.extract(pdf, exercise))
		return images
