import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtWidgets, QtCore
from ui_main import Ui_MainWindow
from motion.core import RobotControl


class RobotController:
    """Класс для управления роботом, инкапсулирующий API"""
    def __init__(self):
        self.robot = RobotControl()
        self.is_connected = False
        self.is_engaged = False

    def connect_robot(self):
        """Подключение к роботу"""
        self.is_connected = self.robot.connect()
        return self.is_connected

    def engage_motors(self):
        """Включение моторов"""
        if self.is_connected:
            self.is_engaged = self.robot.engage()
            return self.is_engaged
        return False

    def disconnect_robot(self):
        """Отключение робота"""
        if self.is_connected:
            self.robot.stop()
            self.robot.disengage()
            self.is_connected = False
            self.is_engaged = False
            return True
        return False

    def pause_robot(self):
        """Постановка робота на паузу"""
        if self.is_connected:
            self.robot.pause()
            return True
        return False

    def set_joint_mode(self):
        """Установка режима Joint"""
        if self.is_connected:
            return self.robot.manualJointMode()
        return False

    def set_cart_mode(self):
        """Установка режима Cart"""
        if self.is_connected:
            return self.robot.manualCartMode()
        return False

    def move_motors(self, velocities):
        """Управление моторами"""
        if self.is_connected and self.is_engaged:
            self.robot.setJointVelocity(velocities)
            return True
        return False

    def activate_gripper(self):
        """Активация гриппера"""
        if self.is_connected:
            self.robot.toolON()
            return True
        return False


class ManualControl(QMainWindow):
    """Главный класс интерфейса управления"""
    def __init__(self):
        super().__init__()
        
        # Инициализация UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Инициализация контроллера робота
        self.controller = RobotController()
        
        # Настройка интерфейса
        self.setup_ui()
        self.ui.listLog.addItem("Интерфейс инициализирован")

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Подключение кнопок
        self.ui.pushOn.clicked.connect(self.on_connect)
        self.ui.pushStop.clicked.connect(self.on_stop)
        self.ui.pushPause.clicked.connect(self.on_pause)
        
        self.ui.pushJoint.clicked.connect(self.manual_joint_mode)
        self.ui.pushCart.clicked.connect(self.manual_cart_mode)
        self.ui.pushOnG.clicked.connect(self.gripper_on)
        
        # Настройка слайдеров для моторов
        self.setup_motor_sliders()

    def setup_motor_sliders(self):
        """Настройка слайдеров управления моторами"""
        self.motor_sliders = [
            self.ui.vertical1,
            self.ui.vertical2,
            self.ui.vertical3,
            self.ui.vertical4,
            self.ui.vertical5,
            self.ui.vertical6
        ]
        
        # Установка диапазона значений для слайдеров
        for slider in self.motor_sliders:
            slider.setRange(-100, 100)
            slider.setValue(0)
        
        # Подключение обработчиков изменений
        for i, slider in enumerate(self.motor_sliders):
            slider.valueChanged.connect(lambda val, idx=i: self.move_motor(idx, val))

    def log(self, msg):
        """Логирование сообщений"""
        self.ui.listLog.addItem(msg)
        self.ui.listLog.scrollToBottom()

    def on_connect(self):
        """Обработка подключения к роботу"""
        if self.controller.connect_robot():
            self.log("Подключение успешно")
            if self.controller.engage_motors():
                self.log("Моторы включены")
            else:
                self.log("Ошибка при включении моторов")
        else:
            self.log("Ошибка подключения к роботу")

    def on_pause(self):
        """Обработка паузы"""
        if self.controller.pause_robot():
            self.log("Пауза")
        else:
            self.log("Не удалось поставить на паузу")

    def on_stop(self):
        """Обработка остановки"""
        if self.controller.disconnect_robot():
            self.log("Остановлено и отключено")
        else:
            self.log("Не удалось остановить")

    def manual_joint_mode(self):
        """Активация Joint режима"""
        if self.controller.set_joint_mode():
            self.log("Режим Joint активирован")
        else:
            self.log("Ошибка активации Joint режима")

    def manual_cart_mode(self):
        """Активация Cart режима"""
        if self.controller.set_cart_mode():
            self.log("Режим Cart активирован")
        else:
            self.log("Ошибка активации Cart режима")

    def move_motor(self, motor_index, value):
        """Управление мотором"""
        velocities = [0.0] * 6
        velocities[motor_index] = value / 100.0  # Нормализация значения
        if self.controller.move_motors(velocities):
            self.log(f"Мотор {motor_index+1} => скорость {velocities[motor_index]:.2f}")
        else:
            self.log(f"Не удалось установить скорость мотора {motor_index+1}")

    def gripper_on(self):
        """Активация гриппера"""
        if self.controller.activate_gripper():
            self.log("Гриппер включен")
        else:
            self.log("Не удалось включить гриппер")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = ManualControl()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Произошла ошибка: {e}")