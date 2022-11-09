import os
path = os.path.dirname(__file__)
os.chdir(path)
from SALSA.application import Application

if __name__ == '__main__':

    app = Application()
    app.mainloop()
