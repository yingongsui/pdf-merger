from PySide6.QtWidgets import QApplication, QMessageBox,QFileDialog,QMainWindow,QTextBrowser,QProgressBar,QTextEdit
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,QTimer,QThread,Signal

from MyOwnWidgets import MyTextViewer

import os
import re

from PyPDF4 import PdfFileMerger


#主窗体
class PDFMerge(QMainWindow):      #新建的类是从QDialog继承下来的，将ui布局中的元素全部传递进来，作为MainWindow函数的参数
    def __init__(self):
        QUiLoader().registerCustomWidget(MyTextViewer)                       #导入自定义模块

        ui_inf = QFile("pdf ver0.ui")        #导入布局文件
        ui_inf.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_inf)
        ui_inf.close()

        self.filelist = []

        #控件行为设置
        self.ui.OKButton.clicked.connect(self.find_files)     #self.ui.控件名.控件行为.连接函数
        self.ui.MergeButton.clicked.connect(self.merge_files)
        self.ui.clearallButton.clicked.connect(self.clearall)
        #self.ui.FilesBrowser.setText('Please Drag Files Here')
        
        #各种参数，文件位置
        #self.i = 0              #按键次数记录变量
        self.openfilepath = os.path.abspath(os.path.dirname("__file__"))        #文件位置，初始位置定于程序所在目录


    def find_files(self):
        #self.filelist = QFileDialog.getOpenFileNames(None, "Please select files", self.openfilepath)
        print(self.ui.FilesBrowser.allfileslist)
        #self.ui.FilesTable.setCurrentCell(1, 1,'a')
    
    def merge_files(self):
        fname = self.ui.FilesBrowser.allfileslist
        merger = PdfFileMerger()
        i = 1
        for name in fname:
            self.ui.Fileslist.addItem( str(i) + " : " + name[name.rfind('/')+1:])
            merger.append(name)
            i+=1
            #print(name)
            
        merger.write(name[0:name.rfind('/')+1] + "all.pdf")
    
    def clearall(self):
        self.ui.FilesBrowser.clearall()
        self.ui.Fileslist.clear()


if __name__ == "__main__":
    app = QApplication([])
    vm = PDFMerge()
    vm.ui.show()
    app.exec()

          