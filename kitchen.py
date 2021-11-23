import tkinter as tk
from tkinter import Tk, Text, Button, LEFT, BOTTOM, Frame, StringVar, Entry, Listbox
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium.webdriver.support.select import Select 
from tkhtmlview import HTMLLabel
import shared

# Recipe zone
'''
Root source: https://docs.google.com/spreadsheets/u/1/d/1VDPZRCiOIBljBQuXs9-d1v378ZUAqxQOYPlNb3eRlCM/htmlview?fbclid=IwAR0YAViCJO0vMOpMA2VL1XEd890RCy06qhCyxh7rPcJKafter9mcDfKePG8#
Recipe source: https://g0v.hackpad.tw/YfPwmisU9Hp
Icook: https://icook.tw/search/牛肉%20燉/
    - https://icook.tw/recipes/377281
天天里仁: https://www.leezen.com.tw/article_list.php?t=1
料理美食：https://cook.sub.tw/s/牛肉/?p=2 

'''


class Kitchen_Window(tk.Tk):
    def __init__(self, root, driverPath):
        super().__init__()
        self.title("Welcome to the kitchen")

        self.driverPath = driverPath 

        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        w = 800
        h = 600
        self.geometry("{}x{}+{}+{}".format(w, h, (screenWidth - w)//2, (screenHeight - h)//2))  # set window size
        self.configure(bg="lavender blush")

        self.frame0 = tk.Frame(self, bg='lavender blush')
        self.frame1 = tk.Frame(self, bg='lavender blush')
        self.frame2 = tk.Frame(self, bg='lavender blush')
        self.frame3 = tk.Frame(self, bg='lavender blush')
        self.frames = [self.frame0, self.frame1, self.frame2, self.frame3]

        self.create_widgets()

    def create_widgets(self):
        """ create a widget
        """
        meat_list = ['牛肉', '豬肉', '羊肉', '雞肉', '海鮮', '蔬食']
        self.meat_value = tk.StringVar(self)
        self.meat_value.set(meat_list[0])
        meat_choices = tk.OptionMenu(self.frames[0], self.meat_value, *meat_list)
        cook_list = ['清燉', '紅燒', '咖哩', '白醬', '紅醬', '青醬', '']
        self.cook_value = tk.StringVar(self)
        self.cook_value.set(cook_list[0])
        cook_choices = tk.OptionMenu(self.frames[0], self.cook_value, *cook_list)
        prompt1 = tk.Label(self.frames[0], text = "選擇關鍵字: ",  font = shared.FONT, bg='lavender blush')
        self.searchBtn = Button(self.frames[0], text = " Search ", font = shared.FONT, command=self.search_options)

        meat_choices.config(width = 10, padx = 10, pady = 5, font = shared.FONT, bg='lavender blush')
        cook_choices.config(width = 10, padx = 10, pady = 5, font = shared.FONT, bg='lavender blush')
        prompt1.pack(side = tk.LEFT)
        meat_choices.pack(side = tk.LEFT)
        cook_choices.pack(side = tk.LEFT)
        self.searchBtn.pack(side = tk.LEFT)

        self.frame1_0 = tk.Frame(self.frames[1], bg='lavender blush')
        self.frame1_1 = tk.Frame(self.frames[1], bg='lavender blush')
        self.nameLB = Listbox(self.frame1_0, width = 40)
        self.ingredientLB = Listbox(self.frame1_1, width = 40, selectmode=tk.EXTENDED)

        self.nameLB.pack(padx=10,pady=10, fill = tk.BOTH, expand = True)              #.grid(row = 0, column = 0, columnspan = 2) 
        self.ingredientLB.pack(padx=10,pady=10, fill = tk.BOTH, expand = True)        #.grid(row = 0, column = 2, columnspan = 2) 

        self.confirmBtn = Button(self.frames[1], text = " Confirm ", font = shared.FONT, command=self.scrap_recipe)
        self.confirmBtn.pack(padx=10,pady=10, side = tk.RIGHT)                  #.grid(row = 0, column = 0, columnspan = 2)
        
        self.nameLB.bind("<<ListboxSelect>>", self.itemSelected)
        self.nameLB.selection_set(0)

        self.scrollbar = tk.Scrollbar(self.frames[3])
        self.lbl = HTMLLabel(self.frames[3], yscrollcommand=self.scrollbar.set)
        self.lbl.pack(side = tk.LEFT, expand = True) 
        self.lbl.fit_height()
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.config(command=self.lbl.yview)
        self.lbl.config(yscrollcommand=self.scrollbar.set)
        

        self.frame0.pack(side=tk.TOP, fill=tk.BOTH)    
        self.frame1.pack(side=tk.TOP, fill=tk.BOTH)
        self.frame1_0.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame1_1.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame2.pack(side=tk.TOP, fill=tk.BOTH)  
        self.frame3.pack(side=tk.TOP, fill=tk.BOTH)  

    def search_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('-headless')
        chrome = webdriver.Chrome(executable_path = self.driverPath)

        #get the input keywords and make the below url
        url = 'https://icook.tw/search/{}%20{}/'.format(self.meat_value.get(), self.cook_value.get())
        chrome.get(url)
        chrome.minimize_window()
        page = chrome.page_source
        bsObj = BeautifulSoup(page, "html.parser")
        self.search_results = {}
        recipes = bsObj.find_all("li", {"class" : "browse-recipe-item"})
        for item in recipes:
            link = item.find('a', href = True)['href']
            for tmp in item.a.article.find_all("div", {"class" : "browse-recipe-content"}):
                name = tmp.div.h2.get_text()[15:-1]
                ingredient = tmp.div.p.get_text()[15:-1]
            self.search_results[name] = {}
            self.search_results[name]['ingredient'] = self.split_ingredient(ingredient)
            self.search_results[name]['link'] = "{}{}".format("https://icook.tw/", link)
        #set the name and ingredient in the entries
        self.nameLB = self.insert_data(self.nameLB, self.search_results.keys())
        chrome.close()

    def split_ingredient(self, ingredient):
        ingredient = ingredient[3:]
        return ingredient.split('、')


    def itemSelected(self, event):
        obj = event.widget
        index = obj.curselection() 
        if len(index) != 0:
            self.show_ingredients(index[0])

    def show_ingredients(self, index):
        self.name = self.get_key_by_id(index)
        self.ingredientLB = self.insert_data(self.ingredientLB, self.search_results[self.name]['ingredient'])

    def get_key_by_id(self, index):
        i = 0
        for key in self.search_results:
            if i == index:
                return key
            i += 1
        return 'Nothing'

    def insert_data(self, lb, data):
        if lb.size() != 0:
            lb.delete(0, tk.END)
        for item in data:
            lb.insert(tk.END, item)
        return lb

    def scrap_recipe(self):
        # scrape the page back     
        chrome = webdriver.Chrome(executable_path=self.driverPath)
        url = self.search_results[self.name]['link']
        chrome.get(url)
        chrome.minimize_window()
        page = chrome.page_source
        bsObj = BeautifulSoup(page, "html.parser")

        # extract the step area
        self.step_results = {}
        recipes = bsObj.find("ul", {"class" : "recipe-details-steps"}).find_all('li', {'class' : 'recipe-details-step-item'})

        for i, item in enumerate(recipes):
            img_link = item.figure.a.img['src']
            step = item.figcaption.p.get_text()
            self.step_results[i] = {}
            self.step_results[i]['img_link'] = img_link
            self.step_results[i]['step'] = step
        # show in a HTML label
        html = ""
        for step in self.step_results:
            #print("{}. {}".format(step, self.step_results[step]['img_link']))
            html += "<li><img src='{}'><p>{}. {}</p></li>".format(self.step_results[step]['img_link'], step + 1, self.step_results[step]['step'])
        self.lbl.set_html(html = html)

        chrome.minimize_window()