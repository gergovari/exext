from ui import UI

from datetime import datetime
from dateutil import parser

class STUI(UI):
	# TODO: filter config
	def _filter_assignments(self, assignments):
		cutoff = datetime(2023, 6, 1)
		return [assignment for assignment in assignments if parser.parse(assignment["creationTime"]).timestamp() >= cutoff.timestamp()]

	def _choose_elem(self, elems):
		for i, elem in enumerate(elems):
			name = elem.get("name", elem.get("title", str(elem)))
			print(f"{i}: {name}")
		while True:
			try:
				return elems[int(input("Selection: "))]
			except IndexError:
				print("Invalid input, choose from the numbers above!")
	def _choose_course(self):
		return self._choose_elem(self.classroom.get_courses())
	def choose_pdfs(self):
		course = self._choose_course()
		assignments = self._filter_assignments(self.classroom.get_assignments(course) + self.classroom.get_announcements(course))
		print(f"Assignments: {len(assignments)}")
		return self.drive.files_to_pdfs(self.classroom.assignments_to_files(assignments))
