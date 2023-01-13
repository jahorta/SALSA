import os
path = os.path.dirname(__file__)
os.chdir(path)

if __name__ == '__main__':
    from SALSA.application import Application

    app = Application()
    app.mainloop()
