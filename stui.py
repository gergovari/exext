from ui import UI

from datetime import datetime
from dateutil import parser

import ray

class STUI(UI):
	# TODO: filter config
	def _is_assignment_included(self, assignment):
		cutoff = datetime(2023, 6, 1)
		return parser.parse(assignment["creationTime"]).timestamp() >= cutoff.timestamp()
	def _filter_assignments(self, assignments):
		return [assignment for assignment in assignments if self._is_assignment_included(assignment)]

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
		courseworks = self.classroom.get_courseworks.remote(self.classroom, course)
		announcements = self.classroom.get_announcements.remote(self.classroom, course)
		assignments = self._filter_assignments(ray.get(courseworks) + ray.get(announcements))
		print(f"Assignments: {len(assignments)}")
		return self.drive.files_to_pdfs(self.classroom.assignments_to_files(assignments))
