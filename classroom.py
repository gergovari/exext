import ray
import itertools

class ClassroomHandler:
	def __init__(self, google):
		self.google = google
		self.service = google.build("classroom", "v1")

	def get_courses(self):
		courses = []
		request = self.service.courses().list(pageSize=self.google.page_size)
		while request:
			response = request.execute()
			for course in response.get("courses", []):
				courses.append(course)
			request = self.service.courses().list_next(request, response)
		return courses
	
	@ray.remote(num_returns="dynamic")
	def get_assignments(self, course):
		coursework_gen = ray.get(self._get_coursework.remote(self, course))
		announcements_gen = ray.get(self._get_announcements.remote(self, course))
		for coursework, announcement in itertools.zip_longest(coursework_gen, announcements_gen):
			if coursework:
				yield ray.get(coursework)
			if announcement:
				yield ray.get(announcement)

	@ray.remote(num_returns="dynamic")
	def _get_coursework(self, course):
		request = self.service.courses().courseWork().list(courseId = course["id"], 
								   pageSize = self.google.page_size, 
								   orderBy = "updateTime asc")
		while request:
			response = request.execute()
			for coursework in response.get("courseWork", []):
				yield coursework
			request = self.service.courses().courseWork().list_next(request, response)

	@ray.remote(num_returns="dynamic")
	def _get_announcements(self, course):
		request = self.service.courses().courseWork().list(courseId = course["id"], 
								   pageSize = self.google.page_size, 
								   orderBy = "updateTime asc")
		while request:
			response = request.execute()
			for announcements in response.get("announcements", []):
				yield announcements
			request = self.service.courses().announcements().list_next(request, response)
	
	@ray.remote(num_returns="dynamic")
	def assignment_to_files(self, assignment):
		for material in assignment.get("materials", []):
			file = material.get("driveFile", {}).get("driveFile")
			if file:
				yield file

