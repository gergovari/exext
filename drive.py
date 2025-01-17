import requests

class DriveHandler:
	def __init__(self, google):
		self.service = google.build("drive", "v3")

	def _file_to_gdoc(self, material):
		return self.service.files().copy(fileId = material["id"], 
						body = { "mimeType": "application/vnd.google-apps.document" }).execute()
	def _gdoc_to_pdf(self, gdoc):
		try:
			return self.service.files().export(fileId=gdoc["id"], mimeType='application/pdf').execute()
		except HttpError:
			print("Export failed, retrying...")
			self._gdoc_to_pdf(gdoc)

	def _file_to_pdf(self, file):
		return self._gdoc_to_pdf(self._file_to_gdoc(file))

	def files_to_pdfs(self, files):
		docs = []
		print()
		for i, file in enumerate(files):
			print(f"Downloading {i+1}/{len(files)} ({round(((i+1)/len(files))*100, 2)}%): {file['title']}")
			docs.append(self._file_to_pdf(file))
		return docs

