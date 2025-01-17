class ClassroomHandler:
	def __init__(self, google):
		self.google = google
		self.service = google.build("classroom", "v1")

	def get_courses(self):
		courses = []
		request = self.service.courses().list(pageSize=self.google.page_size)
		while request:
			response = request.execute()
			courses += response.get("courses", [])
			request = self.service.courses().list_next(request, response)
		return courses

	def get_assignments(self, course):
		assignments = []
		request = self.service.courses().courseWork().list(courseId = course["id"], pageSize = self.google.page_size, orderBy = "updateTime asc")
		while request:
			response = request.execute()
			assignments += response.get("courseWork", [])
			request = self.service.courses().courseWork().list_next(request, response)
		return assignments
