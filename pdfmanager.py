import uuid
import tempfile

class PDFManager:
	def __init__(self):
		self.temp_dir = tempfile.TemporaryDirectory()
		self.work_dir = self.temp_dir.name

	def _blob_to_pdf(self, blob):
		path = f"{self.work_dir}/{uuid.uuid4()}.pdf"
		with open(path, 'wb') as file:
			file.write(blob)
		return path
	def blobs_to_pdfs(self, blobs):
		pdfs = []
		for blob in blobs:
			pdfs.append(self._blob_to_pdf(blob))
		return pdfs
