import sys, datetime, os, hashlib, shutil, subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QTextEdit, QPushButton, QLabel, QVBoxLayout,QMessageBox,QInputDialog,QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDir


class UI_extension_management(QWidget):
    def __init__(self):
        self.file_path = None
        super().__init__()
        self.resize(400,300)
        self.setWindowTitle('extension management')
        self.btn_import_file = QPushButton("Import extension file")
        self.btn_import_file.clicked.connect(self.get_text_file)

        self.textEditor = QTextEdit()
        self.textEditor.setReadOnly(True)

        self.btn_remove = QPushButton("Remove")
        self.btn_remove.clicked.connect(self.remove)

        self.btn_conform = QPushButton("Conform")
        self.btn_conform.clicked.connect(self.conform)
        
        self.btn_run = QPushButton("Run")
        self.btn_run.clicked.connect(self.run)
        # layout = QVBoxLayout()
        # layout.addWidget(self.btn_import_file)
        # layout.addWidget(self.textEditor)
        # layout.addWidget(self.btn_remove)
        # layout.addWidget(self.btn_conform)
        layout = QGridLayout()
        layout.addWidget(self.btn_import_file,1,0,1,3)
        layout.addWidget(self.textEditor,2,0,2,3)
        layout.addWidget(self.btn_remove,4,0)
        layout.addWidget(self.btn_conform,4,1)
        layout.addWidget(self.btn_run,4,2)
        self.setLayout(layout)

        self.program = ""

    def get_text_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)

        if dialog.exec_():
            self.file_path = dialog.selectedFiles()
            if self.file_path[0]:
                self.textEditor.clear()
                date_time = datetime.datetime.fromtimestamp(os.path.getctime(self.file_path[0]))
                head, self.file_name = os.path.split(self.file_path[0])
                md5_hash=hashlib.md5(open(self.file_path[0],'rb').read()).hexdigest()
                self.textEditor.append(f"File Name: {self.file_name}")
                self.textEditor.append(f"Last modified time: {date_time}")
                self.textEditor.append(f"MD5: {md5_hash}")
                # self.textEditor.append(f"extension language: {self.check_extension()}")
            else:
                self.file_path = None
                pass

    def remove(self):
        extension_folder_path=f'{os.path.dirname(__file__)}/api/extension/'
        try:
            all_file_name = os.listdir(extension_folder_path)
        except:
            QMessageBox.critical(self,'Error',f'open {extension_folder_path} NOT sucessfully')
        if len(all_file_name) != 0:
            select_item, ok_btn = QInputDialog.getItem(self, 'select remove extension', 'extension:',all_file_name )
            if ok_btn:
                try:
                    os.remove(f"{extension_folder_path}{select_item}")
                    QMessageBox.information(self,'information',f'remove extension {select_item} sucessfully')
                except:
                    QMessageBox.critical(self,'Error',f'remove extension {select_item} NOT sucessfully')
        elif len(all_file_name) == 0:
            QMessageBox.information(self,'information',f'no extension imported')

    def run(self):
        extension_folder_path=f'{os.path.dirname(__file__)}/api/extension/'
        try:
            all_file_name = os.listdir(extension_folder_path)
        except:
            QMessageBox.critical(self,'Error',f'open {extension_folder_path} NOT sucessfully')
        if len(all_file_name) != 0:
            select_item, ok_btn = QInputDialog.getItem(self, 'start extension', 'extension:',all_file_name )
            if ok_btn:
                # try:
                    # x = self.command(file_name=select_item)
                    select_item = f"{os.path.dirname(__file__)}/api/extension/{select_item}"
                    # print(x)
                    self.command(file_name=select_item)
                    # os.remove(f"{extension_folder_path}{select_item}")
                    # QMessageBox.information(self,'information',f'remove extension {select_item} sucessfully')
                # except:
                #     QMessageBox.critical(self,'Error',f'internal Error')
        elif len(all_file_name) == 0:
            QMessageBox.information(self,'information',f'no extension imported')

    def conform(self):
        if self.file_path == None:
            QMessageBox.critical(
                self,
                'Error',
                'The extension file not selected.\nplease select extension file '
            )
        else:
            orig_path = self.file_path[0]
            self.destination_path = f"{os.path.dirname(__file__)}/api/extension/{self.file_name}"
            try:
                shutil.copy(orig_path,self.destination_path)
                QMessageBox.information(self,'information','extension import sucessfully')
            except:
                QMessageBox.critical(self, 'internal Error', 'import file Error')
                   
    def check_extension(self,file_name):
        print("\n\n")
        print(file_name)
        print("\n\n")
        if os.access(file_name, os.X_OK) == 1:
            print("yes")
            print(file_name)

        if file_name.endswith('.py'):
            return "Python"
        elif file_name.endswith('.java') or file_name.endswith("jar") or file_name.endswith("class"):
            return "Java"
        elif file_name.endswith('.rb'):
            return "Ruby"         
        elif file_name.endswith(".sh"):
            return "Shell Script"
        elif file_name.endswith(".js"):
            return "Java Script"
        elif file_name.endswith(".go"):
            return "Go"
        elif file_name.endswith(".pl"):
            return "Perl"
        elif file_name.endswith(".R"):
            return "R"
        elif file_name.endswith(".lua"):
            return "Lua"
        elif os.access(file_name, os.X_OK):
            print("test")
            return "Executable file"

    def command(self,file_name):
        match self.check_extension(file_name):
            case "Python":
                return f"python3 {file_name}"
            case "Java":
                return f"java {file_name}"
            case "Ruby":
                return f"ruby {file_name}"
            case "Shell Script":
                return f"{file_name}"
            case "Java Script":
                return f"node {file_name}"
            case "Go":
                return f"go run {file_name}"
            case "Perl":
                return f"perl {file_name}"
            case "R":
                return f"Rscript {file_name}"
            case "Lua":
                return f"{file_name}"
            case "Executable file":
                return f"{file_name}"

    def run_program(self, file_name):
        cmd = self.command(file_name)
        print("1",cmd)
        result = subprocess.call(cmd, shell=True)
        # result = result.stdout.readlines()
        print(result)
        # self.textEditor.clear()
        # for line in result:
        #     self.textEditor.append(line)
        # return result

if __name__ == "__main__":
    app = QApplication(sys.argv)
    show = UI_extension_management()
    show.show()

    sys.exit(app.exec_())