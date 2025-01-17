import os.path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class GoogleHandler:
	def __init__(self, page_size = 100):
		self.page_size = page_size

	def build(self, api, version):
		return build(api, version, credentials = self._get_creds())
	def _get_creds(self):
		SCOPES = [
				'https://www.googleapis.com/auth/classroom.courses.readonly', 
				"https://www.googleapis.com/auth/classroom.course-work.readonly",
				"https://www.googleapis.com/auth/classroom.announcements.readonly",
				"https://www.googleapis.com/auth/drive.file",
				"https://www.googleapis.com/auth/drive.readonly",
				"https://www.googleapis.com/auth/drive.metadata.readonly"
			]
		creds = None
		if os.path.exists('token.json'):
			creds = Credentials.from_authorized_user_file('token.json', SCOPES)
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
						'credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)
				with open('token.json', 'w') as token:
					token.write(creds.to_json())
		return creds
