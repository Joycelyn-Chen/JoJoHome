import tkinter as tk
import game
import music
import kitchen
import library
import shared
from shared import *
import argparse
import os

def parse_args():
    desc = "Welcome to JoJo's House\n{}".format(shared.JOYFULNESS)
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--path2driver', type=str,
                        help='Path to driver, selenium requirement')        #, default='/Users/joycelyn/Desktop/NCNU/junior_2/Web_scraping/program/chromedriver'

    parser.add_argument('--face_cascade', help='Path to face cascade.', default=os.path.join('.', 'src', 'haarcascade_frontalface_alt.xml'))
    parser.add_argument('--camera_device', help='Camera device number.', type=int, default=0)
    parser.add_argument('--root_dir', type=str, default=os.path.join('.', 'images'),
                        help='Path to image storage')
    return check_args(parser.parse_args()) 


def kitchen_callback(path2driver):
    kitchen_window = kitchen.Kitchen_Window(root, path2driver)
    kitchen_window.focus_set()

    return


def game_callback(face_cascade, camera_device, root_dir):
    game_window = game.Game_Window(root, 
                                    face_cascade = face_cascade,
                                    camera_device = camera_device, 
                                    root_dir = root_dir)
    game_window.focus_set()

    return

def music_callback():
    music_window = music.Music_Window(root)
    music_window.focus_set()

    return

def library_callback(path2driver):
    library_window = library.Library_Window(root, path2driver=path2driver)
    library_window.focus_set()

    return

if __name__ == '__main__':
    args = parse_args()
    if args is None:
      exit()
    root = tk.Tk()
    root.title("Scrap Final Project")
    root.config(bg='olive drab')
    # root.geometry("300x200")
    #screenWidth = root.winfo_screenwidth()
    #screenHeight = root.winfo_screenheight()
    #w = 800
    #h = 600
    #root.geometry("{}x{}+{}+{}".format(w, h, (screenWidth - w)//2, (screenHeight - h)//2))      # set window size

    kitchen_btn = tk.Button(root, text="Kitchen", font=shared.MAIN_FONT, command=lambda:kitchen_callback(args.path2driver))
    game_btn    = tk.Button(root, text="Game", font=shared.MAIN_FONT, command=lambda:game_callback(args.face_cascade, args.camera_device, args.root_dir))
    lib_btn     = tk.Button(root, text="Library", font=shared.MAIN_FONT, command=lambda:library_callback(args.path2driver))
    music_btn   = tk.Button(root, text="TV", font=shared.MAIN_FONT, command=music_callback)

    kitchen_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
    game_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    lib_btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
    music_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

    root.mainloop()
