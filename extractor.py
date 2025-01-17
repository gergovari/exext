import pdfplumber
from PIL import Image

class ExerciseExtractor:
	def __init__(self, path, start = 1, crop_start_offset = 0, crop_end_offset = 0):
		self.path = path
		self.start = start
		self.crop_start_offset = crop_start_offset
		self.crop_end_offset = crop_end_offset

	def _get_total_image_size(self, images):
		widths, heights = zip(*(image.original.size for image in images))
		return (max(widths), sum(heights))
	def _stitch_images(self, images):
		final = Image.new("RGB", self._get_total_image_size(images))
		offset = 0
		for image in images:
			final.paste(image.original, (0, offset))
			offset += image.original.size[1]
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

	def _crop_page(self, page, start, end, ignore_offset = (False, False)):
		if not ignore_offset[0]:
			start += self.crop_start_offset
		if not ignore_offset[1]:
			end += self.crop_end_offset
		if start < 0:
			start = 0
		if end > page.height:
			end = page.height
		return page.crop((0, start, page.width, end))

	def extract(self, num):
		images = []
		already_started = False
		with pdfplumber.open(self.path) as pdf:
			for i, page in enumerate(pdf.pages):
				if already_started:
					start = self._find_top_y_coord(page)
				else:
					start = self._find_text_y_coord(page, f"{num}.")

				end = self._find_text_y_coord(page, f"{num+1}.")
				can_continue = not end
				if not end:
					end = self._find_bottom_y_coord(page)

				if start:
					image = self._crop_page(page, start, end, 
						(
							already_started, 
							not i + 1 == len(pdf.pages) and can_continue
						)).to_image(resolution=300) 
					if can_continue:
						already_started = True
						images.append(image)
					else:
						return image
			if len(images) > 0:
				return self._stitch_images(images)
	
	def extract_all(self):
		images = []
		# FIXME: can't account for missing numbers or weird schemes...
		for i in range((self.start - 1) + self.get_exercise_count()):
			image = self.extract(i + 1)
			if image:
				images.append(image)
		return images

	def get_exercise_count(self):
		with pdfplumber.open(self.path) as pdf:
			total = 0
			for page in pdf.pages:
				# FIXME: can't account for out of order / missing numbers
				while f"{self.start + total}." in page.extract_text():
					total += 1
			return total
