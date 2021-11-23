import re
import os
import json
import queue
import shared
import threading
import webbrowser
from pprint import pprint

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


udn_category_fname = '.udn_category.json'
all_sub_category   = 'Choose All'

def get_books(url, book_queue, max_len, chrome_driver):
    counter = 0
    error_counter = 0
    browser = webdriver.Chrome(chrome_driver)
    browser.minimize_window()
    browser.get(url)
    WebDriverWait(browser, 10).until( EC.presence_of_element_located( (By.CLASS_NAME, "item-wrapper") ) )
    browser.implicitly_wait(0.5)

    height = browser.execute_script("return document.body.scrollHeight")

    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        browser.implicitly_wait(0.5)

        books = browser.find_elements_by_class_name("item")

        for idx in range(counter, len(books)):
            tmp = {}
            book = books[idx]
            
            tmp['book_name'] = book.find_element_by_class_name("wrapper-bookname").text
            tmp['book_href'] = book.find_element_by_class_name("imgwrapper").find_element_by_tag_name('a').get_attribute('href')

            counter += 1
            book_queue.put(tmp)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if counter == max_len:
            print('Exit by counter')
            break
        if height == new_height:
            error_counter += 1
            if error_counter > 200:
                error_counter = 0
                browser.maximize_window()
                browser.minimize_window()
        height = new_height
        
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight - (document.body.scrollHeight*0.2));")

    book_queue.put(-1) # End of Books
    browser.close()
    return

def show_books(book_queue, max_len):
    counter = 0

    while counter != max_len:
        data = book_queue.get()
        print(counter)
        pprint(data)

        counter += 1

    return

def get_category(url, chrome_driver):
    result = []
    browser = webdriver.Chrome(chrome_driver)
    browser.minimize_window()
    browser.get(url)
    WebDriverWait(browser, 10).until( EC.presence_of_element_located( (By.CLASS_NAME, "navbar-category") ) )

    ebook_section = browser.find_element_by_class_name("content.category.b").find_element_by_class_name('navbar').find_element_by_tag_name('section')
    
    browser2 = webdriver.Chrome(chrome_driver)  # For search sub categories
    browser2.minimize_window()
    categories = ebook_section.find_elements_by_class_name("navbar-category")
    for category in categories:
        tmp = {}

        category_tag  = category.find_element_by_tag_name('a')
        name          = category_tag.text
        total         = category_tag.find_element_by_tag_name('span').text
        category_href = category_tag.get_attribute('href')

        # Get Category Information (Layer 1)
        tmp['category']       = name.replace(total, '').strip('\n')
        tmp['total']          = int(total.strip('()'))
        tmp['category_href']  = category_href
        tmp['sub_categories'] = []

        # Get Sub-Category Information (Layer 2)
        browser2.get(category_href)
        WebDriverWait(browser, 10).until( EC.presence_of_element_located( (By.CLASS_NAME, "navbar-category") ) )
        browser2.implicitly_wait(1)

        sub_categories = browser2.find_elements_by_class_name("subcat-item")
        for sub_category in sub_categories:
            sub_tmp           = {}
            sub_name          = sub_category.find_element_by_tag_name('div').text
            sub_total         = sub_category.find_element_by_tag_name('span').text
            sub_category_href = sub_category.get_attribute('href')

            sub_tmp['category']      = sub_name.replace(sub_total, '')
            sub_tmp['total']         = int(sub_total.strip('()'))
            sub_tmp['category_href'] = sub_category_href

            tmp['sub_categories'].append(sub_tmp)

        result.append(tmp)

    browser2.close()
    browser.close()
    return result

class Library_Window(tk.Toplevel):
    def __init__(self, root, *args, **kwargs):
        super().__init__()

        self.udn_categories = None
        self.book_list = []
        self.driver_path = kwargs['path2driver']
        self.frame_bg = 'lemon chiffon'

        init_category_th = threading.Thread(target=self.init_udn_category)
        need_to_wait = self.init_interface(init_category_th)

        self.title("Library")
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = 800, 600
        self.geometry("{}x{}+{}+{}".format(w, h, (screen_width - w)//2, (screen_height - h)//2))

        self.frame0 = tk.Frame(self, bg=self.frame_bg)
        self.frame1 = tk.Frame(self, bg=self.frame_bg)
        self.frame2 = tk.Frame(self, bg=self.frame_bg)
        self.frames = [self.frame0, self.frame1, self.frame2]

        self.main_menu_selected = tk.StringVar(self)
        self.sub_menu_selected  = tk.StringVar(self)
        self.book_scrollbar     = tk.Scrollbar(self.frame1)
        self.main_menu  = ttk.Combobox(self.frame0, textvariable=self.main_menu_selected, state="readonly", font=shared.FONT)
        self.sub_menu   = ttk.Combobox(self.frame0, textvariable=self.sub_menu_selected, state="readonly", font=shared.FONT)
        self.search_btn = tk.Button(self.frame0, text="Search", font=shared.FONT, command=self.search_callback)
        self.book_lb    = tk.Listbox(self.frame1, yscrollcommand=self.book_scrollbar.set, font=shared.FONT)

        self.back_btn  = tk.Button(self.frame2, text="Back", command=self.destroy, font=shared.FONT)

        self.book_scrollbar.config(command=self.book_lb.yview)

        self.main_menu.bind("<<ComboboxSelected>>", self.main_menu_selected_event)
        self.book_lb.bind("<Double-Button>", self.open_book_event)

        self.pack_elements()

        if need_to_wait:
            init_category_th.join()
            messagebox.showinfo('Done', 'Categories are fetched successfully.')

        # Init combobox value
        self.main_menu.config(value=[ '{} ({})'.format(category["category"], category["total"]) for category in self.udn_categories ])
        self.main_menu.current(0)
        self.sub_menu.config(value=[ '{} ({})'.format(sub_category["category"], sub_category["total"]) for sub_category in self.udn_categories[self.main_menu.current()]["sub_categories"] ])
        self.sub_menu.current(0)

    def pack_elements(self):
        # Pack Frame
        for frame in self.frames:
            frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.main_menu.pack(side=tk.LEFT, padx=3, pady=2)
        self.sub_menu.pack(side=tk.LEFT, padx=3, pady=2)
        self.search_btn.pack(side=tk.LEFT, padx=3, pady=2)

        self.book_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.book_lb.pack(fill=tk.BOTH)

        self.back_btn.pack(side=tk.LEFT, padx=3, pady=2)

        return

    def init_interface(self, init_category_th):
        # UI interactive object can't be used in thread
        global udn_category_fname

        if not os.path.exists(udn_category_fname):
            messagebox.showinfo('Wait', "It will take a few minutes to initialize the categories.")
            init_category_th.start()
            return True
        elif messagebox.askyesno('Update', "Would you want to update the categories?\nIt will take a few minutes to update the categories."):
            init_category_th.start()
            return True
        else:
            with open(udn_category_fname, 'r', encoding='utf-8') as fd:
                self.udn_categories = json.load(fd)
            return False

    def init_udn_category(self):
        # Sub-Thread for get category from web
        global udn_category_fname

        udn_ebook_url = "https://reading-udn-com.autorpa.lib.ncnu.edu.tw/udnlib/ncnu/bookcategory/b"
        self.udn_categories = get_category(udn_ebook_url, self.driver_path)

        with open(udn_category_fname, 'w', encoding='utf-8') as fd:
            json.dump(self.udn_categories, fd, indent=2)

        return

    def main_menu_selected_event(self, event):
        self.sub_menu.config(value=[ '{} ({})'.format(sub_category["category"], sub_category["total"]) for sub_category in self.udn_categories[self.main_menu.current()]["sub_categories"] ])
        self.sub_menu.current(0)

        return

    def search_callback(self):
        book_queue = queue.Queue()
        main_idx   = self.main_menu.current()
        sub_idx    = self.sub_menu.current()
        data       = self.udn_categories[main_idx]["sub_categories"][sub_idx]
        self.book_list.clear()
        self.book_lb.delete(0, self.book_lb.size()-1 )

        search_book_th = threading.Thread(target=get_books, args=(data["category_href"], book_queue, data["total"], self.driver_path))
        search_book_th.start()

        while True:
            book = book_queue.get()  # key: book_name, book_href
            
            if book == -1:
                # All books are fetched
                break
            else:
                self.book_list.append(book)
                self.book_lb.insert(tk.END, book["book_name"])

        search_book_th.join()

        return

    def open_book_event(self, event):
        select_idx = self.book_lb.curselection()[0]
        browser = webdriver.Chrome(self.driver_path)
        browser.get(self.book_list[select_idx]["book_href"])
        browser.maximize_window()

        return