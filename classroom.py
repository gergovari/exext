import ray

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

	@ray.remote
	def get_courseworks(self, course):
		assignments = []
		request = self.service.courses().courseWork().list(courseId = course["id"], pageSize = self.google.page_size, orderBy = "updateTime asc")
		while request:
			response = request.execute()
			assignments += response.get("courseWork", [])
			request = self.service.courses().courseWork().list_next(request, response)
		return assignments
	
	@ray.remote
	def get_announcements(self, course):
		announcements = []
		request = self.service.courses().announcements().list(courseId = course["id"], 
								      pageSize=self.google.page_size,
								      orderBy = "updateTime asc")
		while request:
			response = request.execute()
			announcements += response.get("announcements", [])
			request = self.service.courses().announcements().list_next(request, response)
		return announcements

	def _assignments_to_materials(self, assignments):
		materials = []
		for assignment in assignments:
			try:
				materials += assignment["materials"]
			except KeyError:
				continue
		return materials
	def _materials_to_files(self, materials):
		files = []
		for material in materials:
			try:
				files.append(material["driveFile"]["driveFile"])
			except KeyError:
				continue
		return files
	def assignments_to_files(self, assignments):
		return self._materials_to_files(self._assignments_to_materials(assignments))


