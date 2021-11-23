import tkinter as tk
import shared
from random import randint
from tkinter import simpledialog
from tkinter import messagebox
from detect_emotion import Detect_Emotion

HORSE = "~/-\\^"
HORSE_HEAD = '^'
TRACK_LENGTH = 40
ORIGNAL_TIME = 120
TIME = ORIGNAL_TIME # ms

def stringfy_field(field):
    return '\n'.join(field)

def init_field(total_tracks):
    result = []
    for i in range(total_tracks):
        tmp = ' ' * (TRACK_LENGTH - len(HORSE) - 1) + '|'
        tmp = HORSE + tmp 
        result.append(tmp)
    return result

def game_over(field):
    for num, track in enumerate(field):
        if track.endswith(HORSE_HEAD):
            # horse head reach final line
            return num
    return -1

def move_horse(field, track):
    if field[track][-2] == HORSE_HEAD:
        field[track] = ' ' * (TRACK_LENGTH-len(HORSE)) + HORSE
    else:
        field[track] = ' ' + field[track][:-2] + '|'
    return field

def adjust_game_speed(N):
    global TIME, ORIGNAL_TIME

    TIME = int(ORIGNAL_TIME / N)
    return

class Game_Window(tk.Toplevel):
    def __init__(self, root, face_cascade, camera_device, root_dir, *args, **kwargs):
        super().__init__()

        self.bomb_bg = 'sky blue'

        self.title("Game")
        self.geometry('300x200+100+30')
        self.configure(bg='light cyan')

        self.frame0 = tk.Frame(self, bg=self.bomb_bg)
        self.frame1 = tk.Frame(self, bg=self.bomb_bg)
        self.frames = [self.frame0, self.frame1]

        self.bomb_btn  = tk.Button(self.frame0, text="Bomb", command=self.bomb_callback, font=shared.FONT)
        self.horse_btn = tk.Button(self.frame0, text="Horse", command=self.horse_callback, font=shared.FONT)
        self.detect_btn = tk.Button(self.frame0, text="Detect Emotion", command=self.emotion_callback, font=shared.FONT)
        self.game_dashboard_btns = [self.bomb_btn, self.horse_btn, self.detect_btn]

        self.back_btn = tk.Button(self.frame1, text="Back", command=self.back_callback, font=shared.FONT)

        # Bomb Game Related
        reg = tk.Tk.register(self, func=lambda s: s.isdigit() )
        self.bomb_rule    = tk.Label(self.frame0, text="Enter 0 ~ 100 Integer.", font=shared.FONT, bg=self.bomb_bg)
        self.bomb_textbox = tk.Entry(self.frame0, font=shared.FONT, validate='key', validatecommand=(reg, "%S"))
        self.bomb_button  = tk.Button(self.frame0, text="Enter", font=shared.FONT, command=self.bomb_game_callback)
        self.bomb_label   = tk.Label(self.frame0, font=shared.FONT, bg=self.bomb_bg)
        self.bomb_widgets = [self.bomb_rule, self.bomb_textbox, self.bomb_button, self.bomb_label]
        
        self.bomb_game_answer  = randint(0, 100)
        self.bomb_game_floor   = 0
        self.bomb_game_ceiling = 100

        # Horse Game Related
        self.horse_field  = None
        self.total_tracks = None
        ## Init Horse Frame
        self.horse_frame1 = tk.Frame(self.frame0, pady=10, bg='PaleGreen3')
        self.horse_frame2 = tk.Frame(self.frame0, pady=10, bg='PaleGreen3')
        self.horse_frame3 = tk.Frame(self.frame0, pady=10, bg='PaleGreen3')
        self.horse_frames = [self.horse_frame1, self.horse_frame2, self.horse_frame3]

        ## Init Horse Label
        self.horse_label_result = tk.Label(self.horse_frame1, text='', justify='center', width=30, 
                               font=('Comic Sans MS', 18, 'bold'), fg='red', bg='PaleGreen3')
        self.horse_label_field  = tk.Label(self.horse_frame1, justify='left', bg='burlywood2', width=30, 
            font=('Comic Sans MS', 16, 'bold'))
        self.horse_label_speed  = tk.Label(self.horse_frame2, text='Speed: ', font=('Comic Sans MS', 16, 'bold'), bg='PaleGreen3')
        self.horse_label_func   = tk.Label(self.horse_frame3, text='Functional: ', font=('Comic Sans MS', 16, 'bold'), bg='PaleGreen3')

        self.horse_label_result.pack(fill=tk.BOTH)
        self.horse_label_field.pack()
        self.horse_label_speed.pack(side=tk.LEFT)
        self.horse_label_func.pack(side=tk.LEFT)

        ## Init Horse Button
        self.horse_btn_speeds = []
        for n in range(4):
            self.horse_btn_speeds.append(
                tk.Button(self.horse_frame2, text='X{}'.format(2**n), justify='center', font=('Comic Sans MS', 14, 'bold'),
                 padx=5, command=lambda n=n: adjust_game_speed(2**n)))
            self.horse_btn_speeds[n].pack(side=tk.LEFT)
        
        self.horse_btn_start = tk.Button(self.horse_frame3, text='Start', justify='center', font=('Comic Sans MS', 14, 'bold'), padx=5, 
                                  command=lambda : self.horse_start_game())
        self.horse_btn_reset = tk.Button(self.horse_frame3, text='Restart', justify='center', font=('Comic Sans MS', 14, 'bold'), padx=5, 
                                  command=lambda : self.reset_horse_game())
        self.horse_btn_quit  = tk.Button(self.horse_frame3, text='Quit', justify='center', font=('Comic Sans MS', 14, 'bold'), padx=5, 
                                  command=self.back_callback)
        
        self.horse_btn_funcs = [self.horse_btn_start, self.horse_btn_reset, self.horse_btn_quit]
        for btn in self.horse_btn_funcs:
            btn.pack(side=tk.LEFT)

        # Pack Frame
        self.frame0.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Pack Game Dashboard Buttons
        for btn in self.game_dashboard_btns:
            btn.pack(padx=5, pady=2, fill=tk.BOTH)

        #Joy 6/28
        self.face_cascade = face_cascade
        self.camera_device = camera_device
        self.root_dir = root_dir
        
    def hide_frame_children(self, n):
        for child in self.frames[n].winfo_children():
            child.pack_forget()

        return

    def bomb_callback(self):
        self.title("Bomb Game")
        self.geometry('500x300+100+30')

        self.hide_frame_children(0)

        for bomb_widget in self.bomb_widgets:
            bomb_widget.pack(padx=5, pady=2, fill=tk.BOTH)

        self.back_btn.pack(side=tk.LEFT, pady=2, padx=5)

        self.bind('<Return>', self.bomb_game_callback)
        # self.bind('<BackSpace>', self.back_callback)  # Cause problem

        return

    def horse_callback(self):
        self.total_tracks = -1
        while self.total_tracks < 0 or self.total_tracks > 15:
            self.total_tracks = simpledialog.askinteger("Number of Horse", "Hom many horses you want to have?")

            if self.total_tracks is None:
                return

            self.horse_field = init_field(self.total_tracks)
            self.horse_update_label()

            if self.total_tracks < 0 or self.total_tracks > 15:
                messagebox.showwarning("Invalid Number", "Vaild Range: 1 ~ 15")

        self.title("Horse Game")
        self.geometry('500x{}+100+30'.format(300 + self.total_tracks * 30))

        self.hide_frame_children(0)

        for frame in self.horse_frames:
            frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.back_btn.pack(side=tk.LEFT, pady=2, padx=5)

        return

    def bomb_game_callback(self, *args, **kwargs):
        number = int(self.bomb_textbox.get())
        self.bomb_textbox.delete(0, tk.END)

        if   number < self.bomb_game_floor or number > self.bomb_game_ceiling:
            self.bomb_label.configure(text="Number out of range!!", fg='red')
            self.bomb_label.after(1000, lambda : self.bomb_label.configure(text="Range: {} ~ {}".format(self.bomb_game_floor, self.bomb_game_ceiling), fg='green'))
        elif number > self.bomb_game_answer:
            self.bomb_game_ceiling = number
            self.bomb_label.configure(text="Range: {} ~ {}".format(self.bomb_game_floor, self.bomb_game_ceiling), fg='green')
        elif number < self.bomb_game_answer:
            self.bomb_game_floor = number
            self.bomb_label.configure(text="Range: {} ~ {}".format(self.bomb_game_floor, self.bomb_game_ceiling), fg='green')
        else:
            self.bomb_game_answer = randint(0, 100)
            self.bomb_game_floor   = 0
            self.bomb_game_ceiling = 100
            self.bomb_label.configure(text="Bomb Bomb Bomb", fg='red')
            self.bomb_label.after(2000, lambda : self.bomb_label.configure(text="Range: {} ~ {}".format(self.bomb_game_floor, self.bomb_game_ceiling), fg='green'))

        return

    def horse_game(self):
        win_horse = game_over(self.horse_field)
        if win_horse != -1:
            self.horse_label_result.config(text='Horse {} wins!!'.format(win_horse+1))
            self.horse_btn_reset.config(state='normal')  # Resume btn state
        else:
            track = randint(0, self.total_tracks-1)
            self.horse_field = move_horse(self.horse_field, track)
            self.horse_update_label()
            self.horse_label_field.after(TIME, lambda: self.horse_game())

        return

    def horse_update_label(self):
        self.horse_label_field.config(text=stringfy_field(self.horse_field))
        
        return

    def horse_start_game(self):
        # Set timer
        self.horse_label_field.after(TIME, lambda: self.horse_game())
        self.horse_btn_start.pack_forget()
        self.horse_btn_reset.config(state='disabled')
        
        return

    def reset_horse_game(self):
        self.horse_field = init_field(self.total_tracks)
        self.horse_label_result.config(text='')
        self.horse_label_field.after(TIME, lambda: self.horse_game())

        self.horse_btn_reset.config(state='disabled')  # Diable Reset Button
        
        return

    def emotion_callback(self):
        detect = Detect_Emotion(
                        face_cascade_name = self.face_cascade,
                        camera_device = self.camera_device, 
                        root_dir = self.root_dir)
        detect.mainloop()

        return 

    def back_callback(self, *args):
        self.title("Game")
        self.geometry('300x200+100+30')
        
        self.hide_frame_children(0)
        self.hide_frame_children(1)

        # Pack Game Dashboard Buttons
        for btn in self.game_dashboard_btns:
            btn.pack(padx=5, pady=2, fill=tk.BOTH)
        
        self.unbind('<Return>')
        self.unbind('<BackSpace>')

        return

    def enter_callback(self, *args):
        pass
