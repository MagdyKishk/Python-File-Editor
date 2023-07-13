#------------Imports-------------#

import os
from pynput import keyboard
from pynput.keyboard import Key
from rich.console import Console
from rich.layout import Layout
from rich.rule import Rule
from rich.panel import Panel

#------------Important Variables--------#

scrolable = False
line_index = 0
console = Console()

#--------------Control Classes-------------#

class UI:
	"""
	UI Class
	It is a class to contorl the ui built using Rich module
	"""
	layout = Layout()

	@classmethod
	def base(self):
		"""
		base - is UI class method that create the basic UI Parts
		example: Header / Main / Command layouts
		"""
		UI.layout.split_column(
			Layout(name="Header", size=3),
			Layout(name="Main"),
			Layout(name="Command", size=3))
		UI.layout["Header"].update(Panel(Rule("File Explorer", characters="#"), border_style="green"))
		UI.layout["Main"].update(Panel("", border_style="green"))
		UI.layout["Command"].update(Panel("", border_style="green"))
		UI.refresh()

	@classmethod
	def clear_terminal(self):
		"""
		clear_terminal - is UI class method that clears
		the Terminal using cls command for windows
		clear command for Unix
		"""
		os.system("cls" if os.name == "nt" else "clear")

	@classmethod
	def refresh(self):
		"""
		refresh - is UI class method that refresh the ui by
		clearing the terminal from the current ui and
		printing it again Usually used to print
		ui layout after appling changes
		"""
		global max_lines
		update_max_lines()
		UI.clear_terminal()
		console.height = max_lines + 8
		console.print(UI.layout)

	@classmethod
	def main_layout(self, text):
		"""
		main_layout - is UI class method that control
		the content of the main section
		@text: the text to show in main section
		"""
		UI.layout["Main"].update(Panel(text, border_style="green"))
		UI.refresh()

	@classmethod
	def command_layout(self, text):
		"""
		command_layout - is UI class method that control
		the content of the command section
		@text: the text to show in command section
		"""
		UI.layout["Command"].update(Panel(text, border_style="green"))
		UI.refresh()

	@classmethod
	def starter(self):
		"""
		starter - is UI class method that uses UI classmethods
		to create the basic start page for the app
		"""
		UI.base()
		UI.main_layout(get_dir_content(True))
		UI.command_layout("Change Directory / Open File")


class Keyboard_handler:
	"""
	Keyboard class
	is a class to contorl the keyboard
	for example scrolling
	"""

	@classmethod
	def manage_scroll(self, key):
		"""
		manage_scroll
		is a Keyboard class method that scroll
		the content if scroable conetn using up & down
		arrow keys
		@key: the key pressed
		"""
		global scrolable, line_index, dir_content, file_content, file_or_dir
		lines_count = (dir_content if file_or_dir == "dir" else file_content).count("\n") + 1
		if key is key.up:
			content = scroll_page("up", dir_content if file_or_dir == "dir" else file_content, max_lines=max_lines)
			UI.main_layout(content)
			print(" > ", end="", flush=True)
		if key is key.down:
			content = scroll_page("down", dir_content if file_or_dir == "dir" else file_content, max_lines=max_lines)
			UI.main_layout(content)
			print(" > ", end="", flush=True)
		if key is Key.esc:
			line_index = 0
			content = get_lines(dir_content, max_lines=max_lines)
			scrolable = is_scrollable(dir_content, max_lines=max_lines)
			file_or_dir = "dir"
			UI.main_layout(content)
			Keyboard_handler.stop_keyboard_listener()
		message = []
		message.append("↑") if line_index > 0 else ""
		message.append("↓") if line_index + max_lines < lines_count else ""
		message.append("esc")
		UI.command_layout(" / ".join(message))

	@classmethod
	def start_keyboard_listener(self):
		"""
		start_keyboard_listener - is a Keyboard class method
		that starts the keyboard listener
		"""
		global listener
		listener = keyboard.Listener(on_press=Keyboard_handler.manage_scroll)
		listener.start()
		listener.join()

	@classmethod
	def stop_keyboard_listener(self):
		"""
		stop_keyboard_listener - is a Keyboard class method
		that stops the keyboard listener
		"""
		global listener
		listener.stop()


def get_file_content(file_name: str) -> str:
	with open(file_name, 'r') as file:
		return file.read()

def get_lines(text: str, max_lines: int) -> str:
	global line_index
	if is_scrollable(text, max_lines):
		lines = text.split('\n')
		current_lines = '\n'.join(lines[line_index:line_index + max_lines])
		return current_lines
	else:
		return text

def is_scrollable(text: str, max_lines: int) -> bool:
	lines = text.count('\n') + 1
	return lines > max_lines

def move_dir(new_dir: str) -> None:
	if os.path.exists(new_dir):
		os.chdir(new_dir)

def scroll_page(direction: str, text: str, max_lines: int) -> str:
	global line_index
	number_of_lines = text.count('\n') + 1
	if direction == 'up':
		if line_index > 0:
			line_index -= 1
	elif direction == 'down':
		if line_index + max_lines < number_of_lines:
			line_index += 1
	return get_lines(text, max_lines)

def get_dir_content(organize=False) -> str:
	content = os.listdir()
	content.append('..')
	content.append('.')
	content = sorted(content)
	for i in range(len(content)):
		if os.path.isdir(content[i]):
			content[i] = f"[green]{content[i]}[/]"
		elif os.path.isfile(content[i]):
			content[i] = f"[red]{content[i]}[/]"
	return '\n'.join(content) if organize else content

def get_user_input(text):
	global user_input
	UI.command_layout(text)
	user_input = input(" > ").lower()


def update_max_lines():
	global max_lines
	max_lines = os.get_terminal_size().lines - 9


def manage_user_input():
	global scrolable, dir_content, file_content, file_or_dir
	update_max_lines()
	if scrolable:
		get_user_input("Change Directory / Open File / [S] to Scroll")
		if user_input == "s":
			Keyboard_handler.start_keyboard_listener()
		else:
			scrolable = False
	else:
		get_user_input("Change Directory / Open File")
	if os.path.isdir(user_input):
		move_dir(user_input)
		dir_content = get_dir_content(True)
		scrolable = is_scrollable(dir_content, max_lines=max_lines)
		if scrolable:
			content = get_lines(dir_content, max_lines=max_lines)
		else:
			content = dir_content
		file_or_dir = "dir"
		UI.main_layout(content)
	elif os.path.isfile(user_input):
		file_content = get_file_content(user_input)
		scrolable = is_scrollable(file_content, max_lines=max_lines)
		if scrolable:
			content = get_lines(file_content, max_lines=max_lines)
		else:
			content = file_content
		file_or_dir = "file"
		UI.main_layout(content)


def main():
	manage_user_input()
	main()


if __name__ == "__main__":
	UI.starter()
	main()