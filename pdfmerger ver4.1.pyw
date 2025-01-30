from PySide6.QtWidgets import QApplication, QGraphicsScene, QMessageBox,QMainWindow,QTableWidgetItem,QTableWidget,QAbstractItemView,QGraphicsView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QEvent, QFile,QTimer,QThread,Signal,Qt,Slot
from PySide6.QtGui import QColor, QCursor,QDropEvent,QDragMoveEvent, QImage, QPixmap

import os
from tempfile import TemporaryFile

import fitz
from natsort import natsorted

#列表中文件位置栏
FilePathC = 2

#列表重定义
class MyTableWidget(QTableWidget):                        #创建自己的类，继承自QTextBrowser，已激活拖拽行为
        
        TableSignal =  Signal(str)              #信号得在这里定义才能使用
        PreRow = Signal(int)

        def __init__(self,parent):               #对于与自己建的控件的各种属性
            super(MyTableWidget, self).__init__(parent)         #这条命令意思是引用自身窗口，因此可以用下面的命令来调整尺寸
            
            # 在ui界面设置的优先级比较高
            
            self.allpaths = "" # ==> 默认文本内容
            self.message = ""
            self.viewport().installEventFilter(self)    #加上viewport才能在表格视图里触发事件
            self.shiftRow = -2                          #防止错误移动行设置的初始值
            self.horizontalHeader().sectionClicked.connect(lambda: self.setSortingEnabled(True))            #加上lambda可以连接有参数的函数
            self.rowselected = 0

        def dragEnterEvent(self, event):
            self.setSortingEnabled(False)           #在开启排序的情况下加入文件的话会导致瞬间排序，文件错位，导致有些值无法填入
            for i in range(len(event.mimeData().urls())):
                fn = event.mimeData().urls()[i].toLocalFile()   #获取文件路径
                prefilepath = os.path.split(fn)           #将所在文件位置进行分割，返回值为元组(文件目录，文件)
                if fn not in self.allpaths:                     #allpaths是str格式
                    if 'pdf' in fn:
                        self.allpaths += fn +"\n"        #去重
                        rownum = self.rowCount()
                        self.setRowCount(rownum+1)
                        self.setItem(rownum,0,QTableWidgetItem(prefilepath[1]))
                        self.setItem(rownum,FilePathC,QTableWidgetItem(fn))
                        self.message = "File Number: " + str(self.rowCount())
                    else:
                        self.message = "Unsupportted File Type!"
                    #event.accept()
                else:
                    self.message= "Repeated File!"
            self.TableSignal.emit(self.message)

        def MousePosition(self):
            RowColum = self.indexAt(self.viewport().mapFromGlobal(QCursor.pos()))
            return([ RowColum.row(), RowColum.column()])            
        
        def CopyFullRow(self,OrigRow,AimRow):
            for col in range(self.columnCount()):
                self.setItem(AimRow,col,QTableWidgetItem(self.item(OrigRow,col)))

            

        #用lambda无法正常实现功能
        # CopyFullRow = lambda self,OrigRow,AimRow : (self.setItem(AimRow,col,QTableWidgetItem(self.item(OrigRow,col))) for col in range(self.columnCount()))
        

###########################################事件检测方法3#############################################################
        def eventFilter(self, widget, event):
            if event.type() == QEvent.MouseButtonPress and event.buttons() == Qt.LeftButton:
                self.shiftRow = self.MousePosition()[0]
                self.rowselected = self.shiftRow
                self.TableSignal.emit("File " + str(self.shiftRow + 1) + " selected!")
                self.PreRow.emit(self.shiftRow)

            elif event.type() == QEvent.MouseButtonPress and event.buttons() == Qt.RightButton:
                DelRow = self.MousePosition()[0]
                self.TableSignal.emit("File " + str(DelRow+1) + " deleted!")
                self.removeRow(DelRow)
            elif event.type() == QEvent.MouseButtonRelease:
                self.shiftRow = -2      #防止意外点击导致换行参数变化
                # print( self.shiftRow)
            elif  self.shiftRow != -2 and event.type() == QEvent.DragLeave:
                self.setSortingEnabled(False)
                AimRow = self.MousePosition()[0] if self.MousePosition()[0] != -1 else self.rowCount()
                self.TableSignal.emit("File " + str(self.shiftRow) + " Shifted!" )
                self.insertRow(AimRow) 
                if self.shiftRow <= AimRow:
                    self.CopyFullRow(self.shiftRow,AimRow)
                    self.removeRow(self.shiftRow)
                else:
                    self.CopyFullRow(self.shiftRow+1,AimRow)
                    self.removeRow(self.shiftRow+1)
                self.shiftRow = -2
            else:
                pass
            return super(MyTableWidget, self).eventFilter(widget, event)



        @Slot()                     #自定义槽函数，需要在ui界面中添加声明
        def clearall(self):
            self.allpaths = ""
            self.message  = ""   
            self.clearContents()
            self.setRowCount(0)
            self.setSortingEnabled(False)


#主窗体
class PDFMerge(QMainWindow):      #新建的类是从QDialog继承下来的，将ui布局中的元素全部传递进来，作为MainWindow函数的参数
    def __init__(self,parent=None):
        super(PDFMerge, self).__init__(parent)
        QUiLoader().registerCustomWidget(MyTableWidget)                       #导入自定义模块
        # print(os.path.dirname(os.path.abspath(__file__)))
        uipath = os.path.dirname(os.path.abspath(__file__))+"\\pdf ver2.ui"   #获取ui文件的绝对路径
        ui_inf = QFile(uipath)        #导入布局文件
        ui_inf.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_inf)
        ui_inf.close()

        #控件行为设置
        self.ui.MergeButton.clicked.connect(self.merge_files)   #self.ui.控件名.控件行为.连接函数
        self.ui.testButton.clicked.connect(self.test)           #控件和信号的链接可以在ui界面中定义
        self.ui.npButton.clicked.connect(lambda : self.ShowPDFP(self.currentRow,self.prepage+1,1))
        self.ui.ppButton.clicked.connect(lambda : self.ShowPDFP(self.currentRow,self.prepage-1,-1))

        #各种参数，文件位置
        self.openfilepath = os.path.abspath(os.path.dirname("__file__"))        #文件位置，初始位置定于程序所在目录
        self.ui.FileTable.TableSignal.connect(self.ui.OutputResult.setText)
        self.ui.FileTable.PreRow.connect(self.ShowPDF)

        self.currentRow = -1
        self.prepage = 0
        self.pagecount = 0

    def test(self):
        if self.ui.FileTable.rowCount()>=1:
            for rownum in range(self.ui.FileTable.rowCount()):
                name = self.ui.FileTable.item(rownum,FilePathC).text()
                in_pdf = fitz.open(name)
                self.ui.FileTable.setItem(rownum,1,QTableWidgetItem(str(in_pdf.page_count)))


    
    def ShowPDFP(self,rownum,page,d):
        if self.currentRow == -1:
            self.ui.OutputResult.setText("No File Selected!")
        else:
            page = page - self.pagecount if page > self.pagecount else page + self.pagecount if page < 0 else page
            in_pdf = fitz.open(self.ui.FileTable.item(rownum,FilePathC).text())
            tempath = TemporaryFile(mode = 'w+b',suffix='.png')
            in_pdf[page].get_pixmap().save(tempath.name)
            self.ui.PDFViewer.setPixmap(QPixmap(tempath.name))
            self.ui.CurrentPage.setAlignment(Qt.AlignCenter)
            self.ui.CurrentPage.setText(str(page+1)+'/'+str(self.pagecount))
            self.prepage += d


    def ShowPDF(self,rownum):
        self.currentRow = rownum
        if rownum == -1:
            self.ui.OutputResult.setText("No File Selected!")
        else:
            in_pdf = fitz.open(self.ui.FileTable.item(rownum,FilePathC).text())
            self.pagecount = in_pdf.page_count
            self.prepage = 0
            self.ui.FileTable.setItem(rownum,1,QTableWidgetItem(str(self.pagecount)))
            tempath = TemporaryFile(mode = 'w+b',suffix='.png')
            in_pdf[0].get_pixmap().save(tempath.name)
            self.ui.PDFViewer.setPixmap(QPixmap(tempath.name))
            self.ui.CurrentPage.setText(str(self.prepage+1)+'/'+str(self.pagecount))

    def merge_files(self):
        out_pdf = fitz.open()
        newsize = fitz.paper_size("a4")
        if self.ui.FileTable.rowCount()>=1:
            for rownum in range(self.ui.FileTable.rowCount()):
                name = self.ui.FileTable.item(rownum,FilePathC).text()
                in_pdf = fitz.open(name)
                self.ui.FileTable.setItem(rownum,1,QTableWidgetItem(str(in_pdf.page_count)))
                self.ui.FileTable.item(rownum,0).setForeground(QColor(81, 176, 255, 255))
                for page in in_pdf:
                    if page.rect.width > page.rect.height and page.rect.width > newsize[1]*0.9:
                        new_page = out_pdf.new_page(width = newsize[0],  height = newsize[1])
                        new_page.show_pdf_page(new_page.rect, in_pdf , page.number, rotate = -90)                
                    else:
                        new_page = out_pdf.new_page(width = newsize[0],  height = newsize[1])
                        new_page.show_pdf_page(new_page.rect, in_pdf , page.number)
            
            outputname = name[0:name.rfind('/')+1] + "all.pdf"
            out_pdf.save(outputname)
            self.ui.OutputResult.setText("Output to " + outputname)
        else:
            self.ui.OutputResult.setText("No File Found!!")


if __name__ == "__main__":
    app = QApplication([])
    # app.setStyle("Fusion") #['windowsvista', 'Windows', 'Fusion']
    vm = PDFMerge()
    vm.ui.show()
    app.exec()

          