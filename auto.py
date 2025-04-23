from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QTableWidgetItem
from ui_main import Ui_MainWindow
from motion.core import RobotControl, Waypoint
import sys

class AutoTransfer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.robot = RobotControl()

        self.ui.pushOn.clicked.connect(self.connect_robot)
        self.ui.pushStop.clicked.connect(self.stop_robot)
        self.ui.pushPrem.clicked.connect(self.start_transfer)

        self.log("Модуль Б: автоматический перенос объектов")

    def log(self, msg):
        self.ui.listLog.addItem(msg)

    def connect_robot(self):
        if self.robot.connect():
            self.robot.engage()
            self.log("Робот подключён и моторы активированы")
        else:
            self.log("Ошибка подключения")

    def stop_robot(self):
        self.robot.stop()
        self.robot.disengage()
        self.log("Остановлено и отключено")

    def get_coordinates(self):
        try:
            coords = []
            for row in range(self.ui.tableCoor.rowCount()):
                point = []
                for col in range(6):
                    item = self.ui.tableCoor.item(row, col)
                    point.append(float(item.text()) if item else 0.0)
                coords.append(Waypoint(point, smoothing_factor=0.1))
            return coords
        except Exception as e:
            self.log(f"Ошибка чтения координат: {e}")
            return []

    def start_transfer(self):
        coords = self.get_coordinates()
        if len(coords) < 2:
            self.log("Недостаточно координат (нужно минимум 2 точки)")
            return

        # Захват и перенос первого объекта
        self.robot.moveToPointL([coords[0]], 0)
        self.robot.toolON()
        self.log("Захват первого объекта")
        self.robot.moveToPointL([coords[1]], 1)
        self.robot.toolOFF()
        self.log("Перенос и отпуск первого объекта")

        if len(coords) >= 4:
            # Захват и перенос второго объекта
            self.robot.moveToPointL([coords[2]], 0)
            self.robot.toolON()
            self.log("Захват второго объекта")
            self.robot.moveToPointL([coords[3]], 1)
            self.robot.toolOFF()
            self.log("Перенос и отпуск второго объекта")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoTransfer()
    window.show()
    sys.exit(app.exec_())
