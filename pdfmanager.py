import uuid
import tempfile
import ray

class PDFManager:
	def __init__(self):
		self.temp_dir = tempfile.TemporaryDirectory()
		self.work_dir = self.temp_dir.name

	@ray.remote
	def blob_to_path(self, blob):
		path = f"{self.work_dir}/{uuid.uuid4()}.pdf"
		with open(path, 'wb') as file:
			file.write(blob)
		return path
