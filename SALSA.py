
import os

path = os.path.dirname(__file__)
os.chdir(path)

#for changing the taskbar icon
if os.name == 'nt':
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == '__main__':
    from SALSA.application import Application

    app = Application()
    app.mainloop()
