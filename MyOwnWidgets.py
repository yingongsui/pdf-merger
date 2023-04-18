from PySide6.QtWidgets import QTextBrowser,QMessageBox,QTextEdit
import os

def typecheck(filelist):        #文件格式
    filetype = ['.mp4','.avi','.txt','.mp3','.aac','pdf']
    
    i = 0
    for t in filetype:
        if t in filelist:
                return(t)
    return(False)

#文本框重定义
class MyTextViewer(QTextBrowser):                        #创建自己的类，继承自QTextBrowser，已激活拖拽行为
        def __init__(self,parent):               #对于与自己建的控件的各种属性
            super(MyTextViewer, self).__init__(parent)         #这条命令意思是引用自身窗口，因此可以用下面的命令来调整尺寸
            self.setAcceptDrops(True)
            self.filenum = 0
            self.allfileslist = []
            self.allframes = 0
            self.filepath = ""
            self.alllines = 0
        
        def textadd(self,nline):            #文本框中加入文件
            #self.setText(str(self.toPlainText()) + nline + "\n")  #此处是加上已经存在于框内的文字，此处的self指的就是自己
            self.append(nline)  #此处是加上已经存在于框内的文字，此处的self指的就是自己

        def dragEnterEvent(self, event):
            self.allpaths = ""  # ==> 默认文本内容
            for i in range(len(event.mimeData().urls())):
                self.filenum +=1
                fn = event.mimeData().urls()[i].toLocalFile()   #获取文件路径
                prefilepath = os.path.split(fn)           #将所在文件位置进行分割，返回值为元组(文件目录，文件)
                self.filepath = prefilepath[0]            #更新位置为当前文件位置
                if fn not in self.allpaths:                     #allpaths是str格式
                    self.allpaths += fn +"\n"        #去重
                    if typecheck(fn) == "pdf":
                        if self.filenum == 1:
                            self.setText( "File" + str(self.filenum) + " : " + fn)
                            self.allfileslist.append(fn)
                        else:
                            self.textadd( "File" + str(self.filenum) + " : " + fn)
                            self.allfileslist.append(fn)                   #将新选择的文件添加进列表 
                    else:
                        print(typecheck(fn))
                        self.textadd( "File" + " : " + fn)
                        QMessageBox.about(None,"Message","Unsupportted file type")
                        self.filenum -= 1           #错误文件不计入文件数中
                    #event.accept()
            #print(self.allfileslist)
            #self.filenum += len(event.mimeData().urls())
            #print(self.toPlainText()) 

        def onlyfilename(self,fname):
            print(fname.rfinf('/'))

        def clearall(self):
            self.filenum = 0
            self.allfileslist = []
            self.allframes = 0
            self.filepath = ""
            self.alllines = 0
            self.setText("")