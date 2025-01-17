from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

class ExerciseMerger:
	def __init__(self, path):
		self.path = path
	
	def _draw_exercise(self, c, image, y):
		height = image.size[1] * (c._pagesize[1]/image.size[0])
		c.drawImage(ImageReader(image), 
			0, , c._pagesize[0], height)
	
	def practice(self, images):
		c = canvas.Canvas(self.path)
		bg = ImageReader(Image.open("bg.jpg"))
		for image in images:
			c.drawImage(bg, 0, 0, *(c._pagesize))
			self._draw_exercise(c, image, c._pagesize[1] - height)
			c.showPage()
		c.save()
	
	def summary(self, images):
		c = canvas.Canvas(self.path)
		total_height = 0
		for image in images:
			height = image.size[1] * (c._pagesize[1]/image.size[0])
			total_height += height
			if total_height > c._pagesize[1]:
				total_height = 0
				c.showPage()
			self._draw_exercise(c, image, c._pagesize[1] - total_height)
		c.save()
