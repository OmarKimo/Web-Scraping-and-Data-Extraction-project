from PySide2.QtGui import QFont, QIcon, QStandardItemModel
from PySide2.QtCore import QDateTime, Qt, QObject, SIGNAL
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QDateEdit
)
import sys
from bs4 import BeautifulSoup
import requests
import threading
from scraping_extraction import request

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


class PlotWidget(QWidget):
    def __init__(self, optionsDict, parent=None):
        super().__init__(parent)

        self.options = optionsDict

        self.DEFAULT_FONT = QFont("Calibri", 15)
        self.DEFAULT_ICON = QIcon("Python.png")

        self.setWindowTitle("Web Scraping / Data Extraction")
        self.setWindowIcon(self.DEFAULT_ICON)
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

        self.stop = QPushButton("Stop")
        self.stop.setFont(self.DEFAULT_FONT)
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

        vlayout = QVBoxLayout()
        vlayout.addLayout(input_layout1)
        vlayout.addLayout(input_layout2)
        vlayout.addLayout(input_layout3)
        self.setLayout(vlayout)

        self.dialog = QMessageBox()
        self.dialog.setFont(self.DEFAULT_FONT)
        self.dialog.setWindowIcon(self.DEFAULT_ICON)

        QObject.connect(self.submit, SIGNAL("clicked()"), self.launch_Thread)

    def launch_Thread(self):
        t = threading.Thread(target=lambda: request(self.county.checkedItems, self.date_range_from.date(
        ).toString("MM/dd/yyyy"), self.date_range_to.date().toString("MM/dd/yyyy"), self.options, self))
        t.start()

# pyinstaller -F --add-data "Python.png;." plotter.py

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
