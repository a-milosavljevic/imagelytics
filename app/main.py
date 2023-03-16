import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQml import QQmlContext
from PySide6.QtGui import QIcon
from myapp import MyApp


def display_warnings(warnings):
    for warning in warnings:
        print(warning)


basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'rs.ac.ni.elfak.aiaquami.imagelytics'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == "__main__":
    app = QApplication()
    icon_file = os.path.join(basedir, 'app.ico')
    app.setWindowIcon(QIcon(icon_file))
    app.setOrganizationDomain('elfak.ni.ac.rs')
    app.setOrganizationName('University of Nis, Faculty of Electronic Engineering')
    app.setApplicationName('Imagelytics')

    engine = QQmlApplicationEngine()
    context = engine.rootContext()

    qtApp = MyApp(app)
    context.setContextProperty("qtApp", qtApp)

    #engine.connect(engine.warnings, qtApp.display_warnings)
    #engine.connect(display_warnings)
    engine.warnings.connect(display_warnings)
    qml_file = os.path.join(basedir, 'app.qml')
    engine.load(qml_file)

    retVal = app.exec()
    qtApp.cancel_processing()
    sys.exit(retVal)
