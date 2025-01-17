from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

class ExerciseMerger:
	def _draw_exercise(self, c, image, y):
		height = image.size[1] * (c._pagesize[1]/image.size[0])
		c.drawImage(ImageReader(image), 
			0, y, c._pagesize[0], height)
	
	def _crop_to_pages(self, size, image):
		pass # TODO: implement for exercises larger than a page, although we run the risk of cutting through text

	def practice(self, path, exercises):
		c = canvas.Canvas(path)
		bg = ImageReader(Image.open("bg.jpg"))
		title = None
		for exercise in exercises:
			image = exercise.image
			if exercise.title:
				title = exercise.image
				continue
			c.drawImage(bg, 0, 0, *(c._pagesize))
			if title:
				height = title.size[1] * (c._pagesize[1]/image.size[0])
				self._draw_exercise(c, title, c._pagesize[1] - height)
				title = None
			height += image.size[1] * (c._pagesize[1]/image.size[0])
			self._draw_exercise(c, image, c._pagesize[1] - height)
			c.showPage()
			height = 0
		return c
	
	def summary(self, path, exercises):
		c = canvas.Canvas(path)
		total_height = 0
		for exercise in exercises:
			image = exercise.image
			height = image.size[1] * (c._pagesize[1]/image.size[0])
			total_height += height
			if total_height > c._pagesize[1]:
				total_height = height
				c.showPage()
			self._draw_exercise(c, image, c._pagesize[1] - total_height)
		return c
