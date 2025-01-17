from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

class ExerciseMerger:
	def _draw_exercise(self, c, image, y):
		height = image.size[1] * (c._pagesize[1]/image.size[0])
		c.drawImage(ImageReader(image), 
			0, y, c._pagesize[0], height)
	
	def practice(self, path, images):
		c = canvas.Canvas(path)
		bg = ImageReader(Image.open("bg.jpg"))
		for image in images:
			c.drawImage(bg, 0, 0, *(c._pagesize))
			self._draw_exercise(c, image, c._pagesize[1] - height)
			c.showPage()
		return c
	
	def summary(self, path, images):
		c = canvas.Canvas(path)
		total_height = 0
		for image in images:
			height = image.size[1] * (c._pagesize[1]/image.size[0])
			total_height += height
			if total_height > c._pagesize[1]:
				total_height = 0
				# TODO: if exercise bigger than a WHOLE page...
				c.showPage()
			self._draw_exercise(c, image, c._pagesize[1] - total_height)
		return c
