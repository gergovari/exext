from ui import UI

import ray

class STUI(UI):
	def _choose_elem(self, elems):
		for i, elem in enumerate(elems):
			name = elem.get("name", elem.get("title", str(elem)))
			print(f"{i}: {name}")
		while True:
			try:
				return elems[int(input("Selection: "))]
			except IndexError:
				print("Invalid input, choose from the numbers above!")
	def choose_course(self, courses):
		return self._choose_elem(courses)
