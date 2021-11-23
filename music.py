import os
import glob
import shared
import pygame
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class Music_Window(tk.Toplevel):
	def __init__(self, root, *args, **kwargs):
		super().__init__()

		self.title("TeleVision")
		self.geometry('300x200+100+30')	
		self.configure(bg='bisque2')

		self.frame0 = tk.Frame(self, bg='bisque2')
		self.frame1 = tk.Frame(self, bg='bisque2')
		self.frames = [self.frame0, self.frame1]

		self.audio_btn  = tk.Button(self.frame0, text="Audio", command=self.audio_callback, font=shared.FONT)
		self.video_btn  = tk.Button(self.frame0, text="Video", command=self.video_callback, font=shared.FONT)
		self.music_dashboard_btns = [self.audio_btn, self.video_btn]

		self.back_btn = tk.Button(self.frame1, text="Back", command=self.back_callback, font=shared.FONT)

		# Audio Related
		self.music_path 	   = '~/'
		self.music_selected    = tk.StringVar(self)
		self.music_folder_btn  = tk.Button(self.frame0, text="Music Folder", command=self.choose_music_dir, font=('Comic Sans MS', 16, 'bold'))
		self.play_music_btn    = tk.Button(self.frame0, text="Play", command=self.play_music_callback, font=('Comic Sans MS', 16, 'bold'))
		self.stop_music_btn	   = tk.Button(self.frame0, text="Stop", command=self.stop_music_callback, font=('Comic Sans MS', 16, 'bold'))
		self.pause_music_btn   = tk.Button(self.frame0, text="Pause", command=self.pause_music_callback, font=('Comic Sans MS', 16, 'bold'))
		self.resume_music_btn  = tk.Button(self.frame0, text="Resume", command=self.resume_music_callback, font=('Comic Sans MS', 16, 'bold'))
		self.music_options     = ttk.Combobox(self.frame0, textvariable=self.music_selected, state="readonly", font=('Console', 14, 'normal'))
		self.audio_widgets     = [self.music_options, self.play_music_btn, self.stop_music_btn, self.pause_music_btn, self.resume_music_btn]

		# self.music_folder_btn.bind('<Return>', self.choose_music_dir)
		# self.play_music_btn.bind('<Return>',   self.play_music_callback)
		# self.stop_music_btn.bind('<Return>',   self.stop_music_callback)
		# self.pause_music_btn.bind('<Return>',  self.pause_music_callback)
		# self.resume_music_btn.bind('<Return>', self.resume_music_callback)

		# Video Related
		self.video_path 	  = '~'
		self.video_frame	  = tk.Frame(self.frame0, bg='bisque2')
		self.video_folder_btn = tk.Button(self.frame0, text="Video Folder", command=self.choose_video_dir, font=('Comic Sans MS', 16, 'bold'))
		self.video_scrollbar  = tk.Scrollbar(self.video_frame)
		self.video_listbox 	  = tk.Listbox(self.video_frame, yscrollcommand=self.video_scrollbar.set)
		self.play_video_btn   = tk.Button(self.frame0, text="Play Video", command=self.play_video_callback, font=('Comic Sans MS', 16, 'bold'))

		self.video_scrollbar.config(command=self.video_listbox.yview)
		self.video_listbox.bind('<Double-Button>', self.play_video_callback)
		self.video_listbox.bind('<Return>', self.play_video_callback)
		self.video_folder_btn.bind('<Return>', self.choose_video_dir)
		self.play_video_btn.bind('<Return>', self.play_video_callback)

		# Pack Frame
		self.frame0.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		# Pack Music Dashboard Buttons
		for btn in self.music_dashboard_btns:
			btn.pack(padx=5, pady=2, fill=tk.BOTH)

	def hide_frame_children(self, n):
		for child in self.frames[n].winfo_children():
			child.pack_forget()
			child.grid_forget()

		return

	def play_music_callback(self, *args, **kwargs):
		pygame.mixer.music.load(os.path.join(self.music_path, self.music_selected.get()))
		pygame.mixer.music.play(loops=0)
		
		return

	def stop_music_callback(self, *args):
		pygame.mixer.music.stop()

		return

	def pause_music_callback(self, *args):
		pygame.mixer.music.pause()
		
		return

	def resume_music_callback(self, *args):
		pygame.mixer.music.unpause()
		
		return

	def choose_music_dir(self, *args):
		tmp = filedialog.askdirectory(parent=self, initialdir=self.music_path)
		if tmp != '':
			self.music_path = tmp
			value=list(map(os.path.basename, glob.glob(os.path.join(self.music_path, "*.mp3"))))

			if len(value) == 0:
				messagebox.showinfo('Info', 'No available music')
				self.focus_set()
			else:
				self.music_options.config(value=value)
				self.music_options.current(0)

		return

	def audio_callback(self, *args):
		self.title("Play Audio")
		self.geometry('400x250+100+30')

		self.hide_frame_children(0)

		self.music_folder_btn.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
		self.music_options.grid(row=0, column=2, columnspan=2, pady=5)
		self.play_music_btn.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
		self.stop_music_btn.grid(row=1, column=2, columnspan=2, sticky=tk.W+tk.E)
		self.pause_music_btn.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
		self.resume_music_btn.grid(row=2, column=2, columnspan=2, sticky=tk.W+tk.E)

		self.back_btn.pack(side=tk.LEFT, padx=5, pady=2)

		self.bind('<Return>', self.play_music_callback)
		self.bind('<BackSpace>', self.back_callback)
		pygame.mixer.init()

		return

	def choose_video_dir(self, *args):
		tmp = filedialog.askdirectory(parent=self, initialdir=self.video_path)
		if tmp != '':
			self.video_path = tmp
			values = list(map(os.path.basename, glob.glob(os.path.join(self.video_path, "*.mp4"))))

			if len(values) == 0:
				messagebox.showinfo('Info', 'No available music')
				self.focus_set()
			else:
				self.video_listbox.delete(0, self.video_listbox.size()-1)
				for value in values:
					self.video_listbox.insert(tk.END, value)
				self.video_listbox.selection_set(0)

		return

	def play_video_callback(self, *args):
		file = self.video_listbox.get(self.video_listbox.curselection())
		os.startfile(os.path.join(self.video_path, file))

		return

	def video_callback(self, *args):
		self.title("Play Video")
		self.geometry('400x350+100+30')

		self.hide_frame_children(0)

		self.video_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.video_listbox.pack(fill=tk.X)

		self.video_folder_btn.pack(pady=2)
		self.video_frame.pack(fill=tk.BOTH, pady=2)
		self.play_video_btn.pack(pady=2)

		self.back_btn.pack(side=tk.LEFT, padx=5, pady=2)

		self.video_listbox.focus_set()

		self.bind('<BackSpace>', self.back_callback)

		return

	def back_callback(self, *args):
		self.title("Music")
		self.geometry('300x200+100+30')
		
		self.hide_frame_children(0)
		self.hide_frame_children(1)

		# Pack Music Dashboard Buttons
		for btn in self.music_dashboard_btns:
			btn.pack(padx=5, pady=2, fill=tk.BOTH)
		
		self.unbind('<Return>')
		self.unbind('<BackSpace>')

		return