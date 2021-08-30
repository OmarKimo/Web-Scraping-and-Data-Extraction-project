# PyQT (GUI) imports
from PySide2.QtGui import QFont, QStandardItemModel
from PySide2.QtCore import QDateTime, QThread, Qt, SIGNAL
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QDateEdit
)
import sys

# Web scraping imports
import requests
from bs4 import BeautifulSoup
from utils import *

# other imports
import os
import csv
from datetime import datetime
import subprocess
from time import sleep
from string import capwords

url = "https://registers.maryland.gov/RowNetWeb/Estates/frmEstateSearch2.aspx"


class CheckableComboBox(QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))
        self.checkedItems = []

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if not index.row():
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
                for itm in self.checkedItems:
                    itm.setCheckState(Qt.Unchecked)
                self.checkedItems.clear()
            else:
                item.setCheckState(Qt.Checked)
                for i in range(1, self.count()):
                    itm = self.model().item(i)
                    itm.setCheckState(Qt.Checked)
                    if itm not in self.checkedItems:
                        self.checkedItems.append(itm)
        else:
            select_all = self.model().item(0)
            select_all.setCheckState(Qt.Unchecked)
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
                if item in self.checkedItems:
                    self.checkedItems.remove(item)
            else:
                item.setCheckState(Qt.Checked)
                if item not in self.checkedItems:
                    self.checkedItems.append(item)


class myThread(QThread):
    def __init__(self, checkedItems, in_date_range_from, in_date_range_to, optionsDict):
        QThread.__init__(self)
        self.checkedItems, self.in_date_range_from, self.in_date_range_to, self.optionsDict = checkedItems, in_date_range_from, in_date_range_to, optionsDict

    def run(self):
        Errors = []
        try:
            data = []
            list_header = ["County", "Estate Number", "Filing Date", "Date of Death", "Type", "Status", "Name", "Decedent Name", "Will", "Date of Will", "Personal Reps First", "Personal Reps Middle", "Personal Reps Last", "Personal Reps Address", "PR Address 2", "PR City", "PR State", "PR Zip Code", "Date Opened", "Date Closed", "Attorney First", "Attorney Middle", "Attorney Last", "Attorney Address", "Attorney Address 2", "Attorney City", "Attorney State", "Attorney Zip Code"
                           ]
            idx = 0
            sess = requests.session()
            folder_name = datetime.now().strftime("%Y-%m-%d at %I.%M.%S %p")

            if getattr(sys, 'frozen', False):
                script_path = os.path.abspath(sys.executable)
                print(f"script abs path (from executable): {script_path}")
            else:
                script_path = os.path.abspath(__file__)
                print(f"script abs path (from script): {script_path}")

            cur_dir = os.path.dirname(script_path)  # os.getcwd()
            print(f"current directory is {cur_dir}")

            save_folder = os.path.join(cur_dir, folder_name)
            if not os.path.exists(save_folder):
                os.mkdir(save_folder)
                print(f"{save_folder} is created")

            save_file = os.path.join(save_folder, "result.csv")
            print(f"saved excel file path is {save_file}")

            basedir = os.path.dirname(save_file)
            print(f"save directory is {basedir}")

            if not os.path.isfile(save_file):
                print("file not there")
                # os.system(f'echo test > "{save_file}"')
                subprocess.Popen(
                    f'echo test > "{save_file}"', shell=True, close_fds=True)
                sleep(2)
                if os.path.isfile(save_file):
                    print("file created")

            with open(save_file, newline='', mode="w") as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(list_header)

                for item in self.checkedItems:
                    in_county = item.text()
                    print(in_county)

                    res = sess.get(url, headers=browser_headers)
                    soup = BeautifulSoup(res.content, 'html.parser')

                    for key in ["__VIEWSTATEGENERATOR", "__VIEWSTATE", "__EVENTVALIDATION"]:
                        request_data[key] = soup.find(
                            name="input", attrs={"id": key})["value"]
                    request_data['cboCountyId'] = self.optionsDict[in_county]
                    request_data["DateOfFilingFrom"] = self.in_date_range_from
                    request_data["DateOfFilingTo"] = self.in_date_range_to

                    res = sess.post(url, headers=browser_headers,
                                    data=request_data)
                    soup = BeautifulSoup(res.content, 'html.parser')

                    links = []
                    table = soup.find(name="table", attrs={
                        "id": "dgSearchResults"})
                    if not table:
                        print(
                            f"Search Criteria Returned No Results. [{in_county} from {self.in_date_range_from} to {self.in_date_range_to}]")
                        continue
                    print(
                        f"Counting records for {in_county} from {self.in_date_range_from} to {self.in_date_range_to}....")
                    HTML_data = table.findAll(name="tr")
                    cnt = 0
                    for element in HTML_data[1:-1]:
                        try:
                            cols = element.findAll("td")
                            cnt += 1
                            col_data = []
                            for col in cols:
                                col_data.append(capwords(col.text))
                                try:
                                    links.append(
                                        f"https://registers.maryland.gov/RowNetWeb/Estates/{col.find('a')['href']}")
                                    col_data[-1] = col_data[-1].lstrip("0")
                                except:
                                    continue
                            data.append(col_data)
                        except:
                            continue

                    rest = HTML_data[-1]
                    current_page = 1

                    while True:
                        print(f"Page {current_page} with total {cnt} records.")
                        try:
                            current_page += 1
                            next_link = rest.find(
                                name="a", href=True, text=str(current_page))["href"]
                            for key in target.keys():
                                if key == "__EVENTTARGET":
                                    target[key] = next_link[next_link.find(
                                        "'")+1:next_link.find(',')-1]
                                else:
                                    target[key] = soup.find(
                                        name="input", attrs={"id": key})["value"]
                            res = sess.post(
                                url, headers=browser_headers, data=target)

                        except:
                            try:
                                next_link = rest.findAll(
                                    name="a", href=True, text="...")[-1]
                                if next_link.find_next(name="a", href=True):
                                    break
                                next_link = next_link["href"]
                                for key in target.keys():
                                    if key == "__EVENTTARGET":
                                        target[key] = next_link[next_link.find(
                                            "'")+1:next_link.find(',')-1]
                                    else:
                                        target[key] = soup.find(
                                            name="input", attrs={"id": key})["value"]
                                res = sess.post(
                                    url, headers=browser_headers, data=target)

                            except:
                                break

                        soup = BeautifulSoup(res.content, 'html.parser')
                        table = soup.find(name="table", attrs={
                            "id": "dgSearchResults"})

                        HTML_data = table.findAll("tr")

                        for element in HTML_data[1:-1]:
                            try:
                                cols = element.findAll("td")
                                cnt += 1
                                col_data = []
                                for col in cols:
                                    col_data.append(capwords(col.text))
                                    try:
                                        links.append(
                                            f"https://registers.maryland.gov/RowNetWeb/Estates/{col.find('a')['href']}")
                                        col_data[-1] = col_data[-1].lstrip("0")
                                    except:
                                        continue
                                data.append(col_data)
                            except:
                                continue

                        rest = HTML_data[-1]

                    print(
                        f"There are total of {cnt} records for {in_county} from {self.in_date_range_from} to {self.in_date_range_to}.")

                    self.emit(SIGNAL('setMaximum(int)'), cnt)
                    for index, link in enumerate(links):
                        try:
                            self.emit(SIGNAL('setValue(int)'), index+1)
                            print(
                                f"Extracting record #{index+1} with link: {link}")

                            response = sess.get(link, headers=browser_headers)
                            try:
                                response.raise_for_status()
                            except:
                                res = response.text
                                first = res.find("ResetId=")+len("ResetId=")
                                new_id = res[first:res.find('"', first)]
                                browser_headers["Cookie"] = f"ASP.NET_SessionId={new_id}"
                                response = sess.get(link, headers=browser_headers)

                            soup = BeautifulSoup(response.content, 'html.parser')
                            data[idx].append(
                                capwords(soup.find(name="span", attrs={"id": "lblName"}).text))
                            data[idx].append(
                                capwords(soup.find(name="span", attrs={"id": "lblWill"}).text))
                            data[idx].append(capwords(soup.find(name="span", attrs={
                                "id": "lblDateOfWill"}).text))
                            # https://registers.maryland.gov/RowNetWeb/Estates/frmDocketImages.aspx?src=row&RecordId=975129107
                            # https://registers.maryland.gov/RowNetWeb/Estates/frmDocketImages.aspx?src=row&RecordId=975544913
                            personal_reps = soup.find(
                                name="span", attrs={"id": "lblPersonalReps"}).text
                            tmp = 0
                            l_names = []
                            while tmp < len(personal_reps):
                                found = personal_reps.find("[", tmp)
                                if found == -1:
                                    break
                                personal_reps_name = personal_reps[tmp:found]
                                found2 = personal_reps.find("]", found+1)
                                personal_reps_rest = personal_reps[found+1:found2]
                                tmp = found2+1
                                l_names.append(
                                    (personal_reps_name, personal_reps_rest))

                            rem = len(data[idx])
                            if not l_names:
                                l_names = [("", "")]

                            ret = split_name(l_names[0][0])
                            for item in ret:
                                data[idx].append(capwords(item))

                            ret = split_address(l_names[0][1])
                            for item in ret:
                                data[idx].append(item)

                            data[idx].append(capwords(soup.find(name="span", attrs={
                                "id": "lblDateOpened"}).text))
                            data[idx].append(capwords(soup.find(name="span", attrs={
                                "id": "lblDateClosed"}).text))
                            attorney = soup.find(name="span", attrs={
                                "id": "lblAttorney"}).text

                            tmp = 0
                            l_attorney = []
                            while tmp < len(attorney):
                                found = attorney.find("[", tmp)
                                if found == -1:
                                    break
                                attorney_name = attorney[tmp:found]
                                found2 = attorney.find("]", found+1)
                                attorney_rest = attorney[found+1:found2]
                                tmp = found2+1
                                l_attorney.append((attorney_name, attorney_rest))

                            rem2 = len(data[idx])
                            if not l_attorney:
                                l_attorney = [("", "")]
                            ret = split_name(l_attorney[0][0])
                            for item in ret:
                                data[idx].append(capwords(item))

                            ret = split_address(l_attorney[0][1])
                            for item in ret:
                                data[idx].append(item)

                            csv_writer.writerow(data[idx])

                            if len(l_names) > 1:
                                t_rem = rem
                                for i in range(1, len(l_names)):
                                    rem = t_rem
                                    ret = split_name(l_names[i][0])
                                    for item in ret:
                                        data[idx][rem] = capwords(item)
                                        rem += 1

                                    ret = split_address(l_names[i][1])
                                    for item in ret:
                                        data[idx][rem] = item
                                        rem += 1
                                    csv_writer.writerow(data[idx])

                            if len(l_attorney) > 1:
                                t_rem2 = rem2
                                for i in range(1, len(l_attorney)):
                                    rem2 = t_rem2
                                    ret = split_name(l_attorney[i][0])
                                    for item in ret:
                                        data[idx][rem2] = capwords(item)
                                        rem2 += 1

                                    ret = split_address(l_attorney[i][1])
                                    for item in ret:
                                        data[idx][rem2] = item
                                        rem2 += 1
                                    csv_writer.writerow(data[idx])
                            idx += 1
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            Errors.append(f"Problem with record #{index+1} with link: {link}")
                    print(
                        f"Extracting {in_county} records from {self.in_date_range_from} to {self.in_date_range_to} is done.")
            print("Finished.")
            if Errors:
                print("\n\nErrors happened: ")
                for i, error in enumerate(Errors):
                    print(f"#{i}: {error}")
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return


class PlotWidget(QWidget):
    def __init__(self, optionsDict, parent=None):
        super().__init__(parent)

        self.options = optionsDict

        self.DEFAULT_FONT = QFont("Calibri", 15)

        self.setWindowTitle("Web Scraping / Data Extraction")
        self.setMinimumWidth(500)

        self.county_label = QLabel("County: ")
        self.county_label.setFont(self.DEFAULT_FONT)
        self.county = CheckableComboBox()
        self.county.setFont(self.DEFAULT_FONT)
        for i, item in enumerate(self.options.keys()):
            self.county.addItem(item)
            item = self.county.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)

        self.from_label = QLabel("Range (From): ")
        self.from_label.setFont(self.DEFAULT_FONT)
        self.date_range_from = QDateEdit(calendarPopup=True)
        self.date_range_from.setDateTime(QDateTime.currentDateTime())
        self.date_range_from.setDisplayFormat("MM/dd/yyyy")

        self.to_label = QLabel("Range (To): ")
        self.to_label.setFont(self.DEFAULT_FONT)
        self.date_range_to = QDateEdit(calendarPopup=True)
        self.date_range_to.setDateTime(QDateTime.currentDateTime())
        self.date_range_to.setDisplayFormat("MM/dd/yyyy")

        self.submit = QPushButton(text="Search")
        self.submit.setFont(self.DEFAULT_FONT)

        self.progress = QProgressBar()

        #  Create layout
        input_layout1 = QHBoxLayout()
        input_layout1.addWidget(self.county_label)
        input_layout1.addWidget(self.county)

        input_layout2 = QHBoxLayout()
        input_layout2.addWidget(self.from_label)
        input_layout2.addWidget(self.date_range_from)
        input_layout2.addWidget(self.to_label)
        input_layout2.addWidget(self.date_range_to)

        input_layout3 = QHBoxLayout()
        input_layout3.addWidget(self.submit)

        input_layout4 = QHBoxLayout()
        input_layout4.addWidget(self.progress)

        vlayout = QVBoxLayout()
        vlayout.addLayout(input_layout1)
        vlayout.addLayout(input_layout2)
        vlayout.addLayout(input_layout3)
        vlayout.addLayout(input_layout4)
        self.setLayout(vlayout)

        self.submit.clicked.connect(self.runLongTask)

    def runLongTask(self):

        self.thread = myThread(self.county.checkedItems, self.date_range_from.date(
        ).toString("MM/dd/yyyy"), self.date_range_to.date().toString("MM/dd/yyyy"), self.options)
        self.connect(self.thread, SIGNAL("setMaximum(int)"),
                     self.progress.setMaximum)
        self.connect(self.thread, SIGNAL(
            "setValue(int)"), self.progress.setValue)
        self.connect(self.thread, SIGNAL("finished()"),
                     lambda: self.setEnabled(True))
        self.thread.start()
        self.setEnabled(False)


if __name__ == "__main__":

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    county_form = soup.find(name="select", attrs={"id": "cboCountyId"})
    optionsDict = {}
    for option in county_form.find_all("option"):
        optionsDict[option.text] = option["value"]

    app = QApplication(sys.argv)
    w = PlotWidget(optionsDict)
    w.show()
    sys.exit(app.exec_())
