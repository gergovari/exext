import requests

class DriveHandler:
	def __init__(self, google):
		self.service = google.build("drive", "v3")

	def _file_to_gdoc(self, material):
		return self.service.files().copy(fileId = material["id"], 
						body = { "mimeType": "application/vnd.google-apps.document" }).execute()
	def _gdoc_to_pdf(self, gdoc):
		return self.service.files().export(fileId=gdoc["id"], mimeType='application/pdf').execute()

	def get_file_as_pdf(self, file):
		return self._gdoc_to_pdf(self._file_to_gdoc(file))
