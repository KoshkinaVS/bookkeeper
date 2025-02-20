from dataclasses import dataclass
import sys
from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets

"""
Создать виджеты:
для отображения списка расходов с возможностью редактирования
для отображения бюджета на день/неделю/месяц с возможностью редактирования
для добавления нового расхода
для просмотра и редактирования списка категорий

Собрать виджеты в главное окно
"""

cats = '''продукты
мясо
сырое мясо
мясные продукты
сладости
книги
одежда
'''.splitlines()

@dataclass()
class ExpenseItem:
    summa: float
    cat: str
    data: str
    comment: str


def widget_with_label(text, widget):
    hl = QtWidgets.QHBoxLayout()
    hl.addWidget(QtWidgets.QLabel(text))
    hl.addWidget(widget)
    return hl

def widget_with_h(w1, w2):
    hl = QtWidgets.QHBoxLayout()
    hl.addWidget(w1)
    hl.addWidget(w2)
    return hl

class TableView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split())

        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.expenses_table.verticalHeader().hide()

        self.layout.addWidget(self.expenses_table)


    def set_data(self, data: list[list[str]]):
        for i, row in enumerate(data):
            for j, x in enumerate(row): self.expenses_table.setItem(
                    i, j, QtWidgets.QTableWidgetItem(x)
                        )


class ExpenseInput(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        # обязательно наследуемся от родительского класса!!
        super().__init__(*args, **kwargs)

        # создаем раскладку
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # сумма траты - одна строка
        self.summa = QtWidgets.QLineEdit()
        self.summa.setPlaceholderText('00.00')

        validator = QtGui.QRegularExpressionValidator(r'[0-9].+')
        self.summa.setValidator(validator)

        self.layout.addLayout(widget_with_label(
        text='Сумма', widget=self.summa))

        self.cats_list = cats

        self.cat = QtWidgets.QComboBox()
        self.cat.addItems(self.cats_list)

        self.date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        self.comment = ''

        self.layout.addLayout(widget_with_label(
        text='Категория', widget=self.cat))


    def is_filled(self):
        return bool(self.summa.text() and self.cat.currentText())

    def get_data(self):
        return [self.date or datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                float(self.summa.text() or 0), self.cat.currentText(), self.comment]
        # return [datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), float(self.summa.text() or 0), self.cat.currentText(), '']


class ExpensesListWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.lines = []
        self.new_expense_widget = ExpenseInput()
        self.layout.addWidget(self.new_expense_widget)


    def add_line(self, w):
        self.lines.append(w)
        # self.new_expense_widget = ExpenseInput()
        # self.layout.addWidget(w)


    # def changeEvent(self, event):
    #     # event.accept()
    #     if all(line.is_filled() for line in self.lines):
    #         self.add_line()

    def get_data(self):
        return [line.get_data() for line in self.lines if line.is_filled()]

class BudgetListWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.lines = []
        self.add_line('День')
        self.add_line('Неделя')
        self.add_line('Месяц')


    def add_line(self, name):
        w = Budget(name)
        self.lines.append(w)
        self.layout.addWidget(w)

    def changeEvent(self, event):
        # event.accept()
        if all(line.is_filled() for line in self.lines):
            self.add_line()

    def get_data(self):
        return [line.get_data() for line in self.lines if line.is_filled()]

class Budget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        # сделать if для разных периодов

        # тут просто отображение чиселки
        self.summa = QtWidgets.QLineEdit()
        # self.summa.setPlaceholderText('0.00')
        # self.summa.setValidator(QtGui.QDoubleValidator(0., 1_000_000_000, 2))
        # self.layout.addWidget(self.summa)

        # тут просто отображение чиселки
        self.budget = QtWidgets.QLineEdit()
        # self.budget.setPlaceholderText('Категория')
        # self.layout.addWidget(self.budget)

    # def is_filled(self):
    #     return bool(self.summa.text() and self.cat.text())
    #
    # def get_data(self):
    #     return ExpenseItem(float(self.summa.text() or 0), self.cat.text())

class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_counter = 0

        self.setWindowTitle("The Bookkeeper App")

        self.cats = cats

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.table_expenses = TableView()
        self.layout.addWidget(self.table_expenses)

        self.expenses_widget = ExpensesListWidget()
        self.layout.addWidget(self.expenses_widget)

        # self.budget_widget = BudgetListWidget()
        # self.layout.addWidget(self.budget_widget)

        # self.new_expense_widget = ExpenseInput()
        # self.layout.addWidget(self.new_expense_widget)

        self.btn_cat = QtWidgets.QPushButton('Редактировать категорию')
        self.layout.addWidget(self.btn_cat)
        self.btn_cat.clicked.connect(self.update_cat)


        self.btn = QtWidgets.QPushButton('Добавить')
        self.layout.addWidget(self.btn)
        self.btn.clicked.connect(self.save)

    def update_cat(self):

        dlg = QtWidgets.QInputDialog()
        # dlg.resize(1000, 200)
        text, ok = dlg.getText(self, "Редактирование категории",
                                          "Имя категории:", QtWidgets.QLineEdit.Normal,
                                          'продукты')
        if ok and text:
            cats.append(text)
            self.expenses_widget.new_expense_widget.cat.addItem(text)
            self.expenses_widget.new_expense_widget.cats_list.append(text)


    def save(self):
        self.expenses_widget.lines.append(self.expenses_widget.new_expense_widget)
        self.table_expenses.set_data(self.expenses_widget.get_data())
        print(self.expenses_widget.get_data())
        self.table_counter += 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
