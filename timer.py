import pandas as pd
import os
import time
import sys
import json
import pyrebase
import firebasedata
from PyQt6.QtCore import QTime, QTimer, QElapsedTimer
#from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QCheckBox, QComboBox
from PyQt6.QtWidgets import *

fireData = firebasedata.firebaseapi()
firebase=pyrebase.initialize_app(fireData)
db=firebase.database()

#class DbScreen()
class StopwatchWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        appdata_path = os.path.expanduser('~\\AppData\\Local')
        self.json_folder = os.path.join(appdata_path, 'Mir4Exp')
        self.json_file = os.path.join(self.json_folder, 'data.json')
        self.combo = QComboBox()
        #items = ["item1", "item2", "item3"]
        #self.combo.addItems(items)
        self.combobox_item = self.combo.currentText()
        self.add_button = QPushButton("Adicionar Spot")
        self.add_button.clicked.connect(self.add_item)
        self.load_data()

        self.delete_button = QPushButton("Deletar Spot")
        self.delete_button.clicked.connect(self.remove_item)
        #self.time = QTime()
        self.time = QTimer()
        self.time.timeout.connect(self.update_time)
        
        self.timer = QElapsedTimer()
        #self.timer.timeout.connect(self.update_time)
        #self.timer.start()
        # Create a label to display the elapsed time
        self.time_label = QLabel("00:00:00")

        # Create input fields for the 2 values
        #self.label = ("Level")
        self.input1 = QLineEdit()
        self.input2 = QLineEdit()
        #self.input3 = QLineEdit()

        # Create a button to start the stopwatch
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)

        # Create a button to stop the stopwatch
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)

        self.level_input = QLineEdit()
        self.level_label = QLabel("Level:")
        

        # Create a button to calculate the result
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)

        # Create a label to display the result
        self.result_label = QLabel()
        self.result1_label = QLabel()

        self.save_checkbox = QCheckBox("Save to Database")
        #self.save_checkbox.stateChanged.connect(self.save_to_database)
        


        # Create a layout to organize the widgets
        layout = QGridLayout(self)
        #layout.addLayout(self.label, 0, 0)
        #layout.addWidget(self.input3, 0, 1)
        layout.addWidget(self.time_label, 1, 0, 1, 2)
        layout.addWidget(self.start_button, 2, 0)
        layout.addWidget(self.stop_button, 2, 1)
        layout.addWidget(self.input1, 3, 0)
        layout.addWidget(self.input2, 3, 1)
        layout.addWidget(self.calculate_button, 4, 0, 1, 2)
        layout.addWidget(self.result_label, 7, 0, 1, 2)
        layout.addWidget(self.result1_label, 8, 0, 1, 2)
        layout.addWidget(self.level_label, 0, 0)
        layout.addWidget(self.level_input, 0, 1)
        layout.addWidget(self.combo, 5, 0, 1, 2)
        layout.addWidget(self.add_button, 6, 0, 1, 1)
        layout.addWidget(self.delete_button, 6, 1, 1, 1)
        layout.addWidget(self.save_checkbox)
        
        
    def add_item(self):
        text, ok = QInputDialog.getText(self, "Adicionar Spot", "Nome do Spot:")
        if ok:
            if not os.path.exists(self.json_folder):
                os.makedirs(self.json_folder)
                self.combo.addItem(text)
                self.save_data()
            else:
                self.combo.addItem(text)
                self.save_data()

    def remove_item(self):
        # Remove the currently selected item from the combo box
        current_item = self.combo.currentIndex()
        self.combo.removeItem(current_item)
        self.save_data()

    def save_data(self):
        items = [self.combo.itemText(i) for i in range(self.combo.count())]
        with open(self.json_file, "w") as f:
            json.dump(items, f)

    def load_data(self):
        try:
            with open(self.json_file, "r") as f:
                items = json.load(f)
                for item in items:
                    self.combo.addItem(item)
        except FileNotFoundError:
            pass


    def start(self):
        # Start the timer and reset the elapsed time
        self.time.start(1000)
        self.timer.start()
        self.timer.restart()
        

    def stop(self):
        # Stop the timer
        self.time.stop()
        #self.timer.stop()
        self.elapsed = self.timer.elapsed()

    def update_time(self):
        # Update the elapsed time display
        elapsed = self.timer.elapsed()
        hours, minutes, seconds = elapsed // 3600000, elapsed % 3600000 // 60000, elapsed % 60000 // 1000
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def calculate(self):
        
        # Get the 2 input values
        #df = pd.read_csv(r"C:\Users\gusta\OneDrive\Área de Trabalho\levels.csv")
        #df = df.loc[:,'Required']
        
        level = int(self.level_input.text())
        level = level + 1
        exp = db.child("Level").order_by_child("Level").equal_to(level).get()
        exp = exp.val()
        exp = dict(exp)
        required = [item['Required'] for item in exp.values()]
        exp = required[0]        
        value1 = float(self.input1.text())
        value2 = float(self.input2.text())
        value1 = (value1 / 100) * exp
        valuetotal = value2        
        value2 = (value2 / 100) * exp
        # Calculate the result using the elapsed time        
        #elapsed = self.timer.elapsed() / 1000
        elapsed = self.elapsed / 1000        
        elapsed = int(elapsed)        
        result = (value2 - value1) / elapsed
        result1 = result
        resultdb = result       
        result = result * 60
        resulttotal = result      
        result = 'Exp por min: ',int(result)
        result1 = result1 * 3600        
        result1 = 'Exp por hora: ', int(result1)
        valuetotal = (valuetotal / 100 ) - 1
        
        valuetotal = abs(valuetotal)
        valuetotal = valuetotal * exp        
        valuetotal = int(valuetotal) 
        resulttotal = int(resulttotal)
        valuetotal = valuetotal / resulttotal
        

        # Calculate the number of days
        days = valuetotal // 1440
        days = round(days)
        # Calculate the number of minutes left
        minutes_left = valuetotal % 1440

        # Calculate the number of hours
        hours = minutes_left // 60
        hours = round(hours)
        # Calculate the number of minutes left
        minutes = minutes_left % 60
        minutes = round(minutes)

        diastotais = (f"Faltam {days} dias, {hours} horas, e {minutes} minutos para pegar level.")
        print(diastotais)
        print(elapsed)
        combobox_item = self.combo.currentText()
        self.result_label.setText(str(result))
        self.result1_label.setText(str(diastotais))
        resultdb = resultdb * 60
        if self.save_checkbox.isChecked():           
            
            
            data = {
            "expperminute": resultdb,
            "level": level,            
            "location": combobox_item
            }
        #db.child("Results").push().set(data)
            db.child("Results").push(data)

    
   

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open(r'styles.qss', 'r') as f:
            style = f.read()
    app.setStyleSheet(style)
    stopwatch = StopwatchWidget()
    stopwatch.show()
    sys.exit(app.exec())
