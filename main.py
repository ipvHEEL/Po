import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)


# Подключение к базе данных
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Ваш пользователь MySQL
        database="Exz",
        auth_plugin = "mysql_native_password"
    )


# Выполнение SQL-запроса
def execute_query(query):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = cursor.column_names
        cursor.close()
        connection.close()
        return result, columns
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Ошибка", f"Ошибка при выполнении запроса:\n{e}")
        return [], []


# Основное окно приложения
class PayrollApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Штатное расписание")
        self.setGeometry(100, 100, 800, 600)

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Макет
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Кнопки
        self.btn_show_employees = QPushButton("Показать всех сотрудников с зарплатами")
        self.btn_show_department_salaries = QPushButton("Показать зарплаты по подразделениям")
        self.btn_show_position_details = QPushButton("Детали должности 'Разработчик'")
        self.btn_back = QPushButton("Назад")

        self.btn_show_employees.clicked.connect(self.show_all_employees)
        self.btn_show_department_salaries.clicked.connect(self.show_department_salaries)
        self.btn_show_position_details.clicked.connect(self.show_position_details)
        self.btn_back.clicked.connect(self.clear_table)


        self.layout.addWidget(self.btn_show_employees)
        self.layout.addWidget(self.btn_show_department_salaries)
        self.layout.addWidget(self.btn_show_position_details)
        self.layout.addWidget(self.btn_back)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

    # Очистка таблицы

    def clear_table(self):
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    # Отображение данных в таблице
    def display_results(self, query):
        results, columns = execute_query(query)
        if not results:
            QMessageBox.information(self, "Результат", "Нет данных для отображения.")
            return

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(results))

        for row_index, row in enumerate(results):
            for col_index, value in enumerate(row):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    # Запросы
    def show_all_employees(self):
        query = """
        SELECT p.title, d.name AS department, s.gross_salary, s.net_salary, s.calculation_date
        FROM Positions p
        JOIN Departments d ON p.department_id = d.id
        JOIN Salaries s ON p.id = s.position_id;
        """
        self.display_results(query)

    def show_department_salaries(self):
        query = """
        SELECT d.name AS department, SUM(s.net_salary) AS total_net_salary
        FROM Salaries s
        JOIN Positions p ON s.position_id = p.id
        JOIN Departments d ON p.department_id = d.id
        GROUP BY d.name;
        """
        self.display_results(query)

    def show_position_details(self):
        query = """
        SELECT p.title, d.name AS department, p.salary, p.overtime_bonus, d.hazard_bonus
        FROM Positions p
        JOIN Departments d ON p.department_id = d.id
        WHERE p.title = 'Разработчик';
        """
        self.display_results(query)


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PayrollApp()
    window.show()
    sys.exit(app.exec_())
