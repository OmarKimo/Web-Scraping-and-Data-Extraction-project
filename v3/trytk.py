import requests
from bs4 import BeautifulSoup
import threading
from scraping_extraction import request
import tkinter as tk
from ChecklistCombobox import ChecklistCombobox
from tkcalendar import DateEntry


class GUI:
    def __init__(self, options) -> None:
        self.window = tk.Tk()

        self.DEFAULT_FONT = ("Calibri", 15)
        self.optionsDict= options

        self.window.title("Web Scraping / Data Extraction")
        self.window.minsize(350, 150)
        self.window.config(padx=30, pady=10)

        self.county_label = tk.Label(
            self.window, text="County: ", font=self.DEFAULT_FONT)
        self.county_label.grid(row=1, column=1)

        self.county = ChecklistCombobox(
            self.window, state='readonly', values=self.optionsDict.keys())
        self.county.grid(row=1, column=2)

        self.from_label = tk.Label(
            self.window, text="Range (From): ", font=self.DEFAULT_FONT)
        self.from_label.grid(row=2, column=1)

        self.date_range_from = DateEntry(
            self.window, date_pattern='mm/dd/yyyy', showweeknumbers=False)
        self.date_range_from.grid(row=2, column=2)

        self.to_label = tk.Label(
            self.window, text="Range (To): ", font=self.DEFAULT_FONT)
        self.to_label.grid(row=3, column=1)

        self.date_range_to = DateEntry(
            self.window, date_pattern='mm/dd/yyyy', showweeknumbers=False)
        self.date_range_to.grid(row=3, column=2)

        self.submit = tk.Button(
            text="Search", font=self.DEFAULT_FONT, command=self.launch_Thread)
        self.submit.grid(row=4, column=1, columnspan=2)

        self.window.mainloop()

    def launch_Thread(self):
        checkedItems = [b.cget('text') for b, v in zip(
            self.county.checkbuttons, self.county.variables) if v.get() == 1 and b.cget('text') != ""]
        date_from = self.date_range_from.get_date().strftime("%m/%d/%Y")
        date_to = self.date_range_to.get_date().strftime("%m/%d/%Y")
        t = threading.Thread(target=lambda: request(
            checkedItems, date_from, date_to, self.optionsDict, self))
        t.start()

# pyinstaller -F --hidden-import "babel.numbers" trytk.py

if __name__ == "__main__":

    url = "https://registers.maryland.gov/RowNetWeb/Estates/frmEstateSearch2.aspx"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    county_form = soup.find(name="select", attrs={"id": "cboCountyId"})
    optionsDict = {}
    for option in county_form.find_all("option"):
        optionsDict[option.text] = option["value"]

    obj = GUI(optionsDict)
