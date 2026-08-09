import sys
from PyQt5.QtWidgets import QInputDialog, QApplication, QWidget,  QGridLayout, QListWidget,  QPushButton ,QMessageBox,QFileDialog
from PyQt5.QtCore import QDir
import os

class UI_gobuster_filter_list_editer(QWidget):
    def __init__(self, *args, **kwargs,):
        super().__init__(*args, **kwargs)
        self.final_conform_wordlist = []
        self.setWindowTitle('Gobuster Filter List Viewer')
        self.setGeometry(100, 100, 400, 300)
        layout = QGridLayout(self)
        self.setLayout(layout)
        self.list_widget = QListWidget(self)
        read_wordlist = self.open_default_wordlist_txt()
        if read_wordlist == False:
            QMessageBox.warning(
            self,
            'Warning',
            'Insert Default Gobuster wordlists NOT sucessfuly!\n\nPlease input the name to this page list viewer'
        )
            
        self.list_widget.addItems(self.default_regex_array)
        layout.addWidget(self.list_widget, 0, 0, 6, 1)

        # create buttons
        add_button = QPushButton('Add')
        add_button.clicked.connect(self.add)

        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(self.remove)

        clear_button = QPushButton('Clear ALL')
        clear_button.clicked.connect(self.clear)

        import_button =  QPushButton('import txt')
        import_button.clicked.connect(self.import_custom_wordlist)

        conform_button = QPushButton('Conform')
        conform_button.clicked.connect(self.conform)

        layout.addWidget(add_button, 0, 1)
        layout.addWidget(remove_button, 1, 1)
        layout.addWidget(clear_button, 2, 1)
        layout.addWidget(import_button, 3,1)
        layout.addWidget(conform_button, 5, 1)


    def open_default_wordlist_txt(self):
        path = f"{os.path.dirname(__file__)}/api/gobuster/gobuster_default_url_filter.txt"
        self.default_regex_array = []
        try:
            with open(path) as file:
                lines = file.readlines()
                for line in lines:
                    line = line.rstrip("\n")
                    self.default_regex_array.append(line.replace(".*",""))
                return True
        except:
            print("FileNotFoundError")
            return False 
    
    def import_custom_wordlist(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)
        if dialog.exec_():
            file_name = dialog.selectedFiles()
            if file_name[0].endswith('.txt'):
                with open(file_name[0]) as file:
                    lines = file.readlines()
                    self.clear()
                    for line in lines:
                        line = line.rstrip("\n")
                        self.default_regex_array.append(line.replace(".*",""))
            self.list_widget.addItems(self.default_regex_array)
            QMessageBox.information(self,
            'information',
            'Insert sustom wordlist sucessfully')
            
    def add(self):
        text, ok_btn = QInputDialog.getText(self, 'Add a New name', 'New filter name:')
        if ok_btn and text:
            self.list_widget.addItem(text)

    def remove(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            current_item = self.list_widget.takeItem(current_row)
            del current_item

    def clear(self):
        self.list_widget.clear()

    def conform(self):
        self.final_conform_wordlist = []
        if self.list_widget.count() != 0 :
            for line in range(self.list_widget.count()):
                self.final_conform_wordlist.append(f".*{self.list_widget.item(line).text()}.*")
            with open(f"{os.path.dirname(__file__)}/api/gobuster/gobuster_temp_URL_filter.txt", 'w') as file:
                for text in self.final_conform_wordlist:
                    file.write(f"{text}\n")
            # print (self.final_conform_wordlist)
            # return self.final_conform_wordlist
            self.close()
        else:
            QMessageBox.warning(self,'Warning','gobuster filter list connot empty!!!')

    
    def get_final_conform_wordlist(self):
        return self.final_conform_wordlist
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_gobuster_filter_list_editer()
    window.show()
    sys.exit(app.exec())