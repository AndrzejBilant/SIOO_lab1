import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QRadioButton, QComboBox, QSlider, \
    QPushButton
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy import optimize


class MathFunction:

    def __init__(self, string):
        self.fun = string

    def __call__(self, x):
        y = self.fun
        result = 0
        i = 0
        while i < len(y):
            if y[i] == "sin":
                result += y[i + 1] * math.sin(y[i + 2] * x)
            elif y[i] == "cos":
                result += y[i + 1] * math.cos(y[i + 2] * x)
            elif y[i] == "tg":
                result += y[i + 1] * math.tg(y[i + 2] * x)
            elif y[i] == "ctg":
                result += y[i + 1] * math.ctg(y[i + 2] * x)
            elif y[i] == "**":
                result += pow(y[i + 1] * x, y[i + 2])
            elif y[i] == "^":
                result += pow(y[i + 1], y[i + 2] * x)
            elif y[i] == "C":
                result += y[i + 1]
                i -= 1
            i += 3

        return result

    def __str__(self):
        y = self.fun
        result = ""
        i = 0
        while i < len(y):
            if (y[i + 1]) > 0 and i > 0:
                result += "+"
            if y[i] in ("sin", "cos", "tg", "ctg"):
                result += str(y[i + 1]) + y[i] + "(" + str(y[2]) + "x)"
            elif y[i] == "**":
                result += str(y[i + 1]) + "x^" + str(y[i + 2])
            elif y[i] == "^":
                result += str(y[i + 1]) + "^" + str(y[i + 2]) + "x"
            elif y[i] == "C":
                result += str(y[i + 1])
                i -= 1
            i += 3
        return result


class Main(QWidget):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.funkcje = [MathFunction(("**", -3, 3, "sin", -2, -3, "^", 2, 3, "C", -3, "cos", 1, 1)),
                        MathFunction(("sin", 2, -1)),
                        MathFunction(("pow", 4, 2, "**", - 1, 4))
                        ]  # najpierw rodzaj operacji, później argument przed operacją, później ile razy X, np. sin,2,-1 = 2*sin(-1*x)

        self.cb = QComboBox()
        for i in self.funkcje:
            self.cb.addItem(str(i))

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-100, 100)
        self.sliderValue = QLabel('0')
        self.slider.valueChanged.connect(self.updateLabel)
        self.sliderValue.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.etap = 0
        self.metoda = "brak"
        self.stop = "brak"
        self.funkcja = "brak"
        self.poczatek = 0
        self.koniec = 0
        self.wybor = "Metoda bisekcji"
        self.iteracje = 0
        self.dokladnosc = 0.0

        self.layout = QVBoxLayout()

        self.label = QLabel("Wybierz metodę")
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.label)

        self.b1 = QRadioButton("Metoda bisekcji")
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda: self.radioButtonZmiana(self.b1))
        self.layout.addWidget(self.b1)

        self.b2 = QRadioButton("Metoda złotego podziału")
        self.b2.toggled.connect(lambda: self.radioButtonZmiana(self.b2))

        self.layout.addWidget(self.b2)
        self.setLayout(self.layout)
        self.setWindowTitle("Wybór metody")

        self.next = QPushButton('OK')
        self.next.clicked.connect(self.zmianaEtapu)
        self.layout.addWidget(self.next)

    def radioButtonZmiana(self, b):

        if b.isChecked():
            self.wybor = b.text()

    def zmianaEtapu(self):

        if self.etap == 0:
            self.etap += 1
            self.metoda = self.wybor
            self.label.setText("Wybierz warunek stopu")
            self.b1.setText("Ilość iteracji")
            self.b1.setChecked(True)
            self.b2.setText("Dokładność")
            self.wybor = "Ilość iteracji"

        elif self.etap == 1:
            self.etap += 1
            self.stop = self.wybor
            self.label.setText("Wybierz funkcję testową")
            self.layout.removeWidget(self.b1)
            self.layout.removeWidget(self.b2)
            self.layout.removeWidget(self.next)
            self.b1.deleteLater()
            self.b2.deleteLater()
            self.layout.addWidget(self.cb)
            self.layout.addWidget(self.next)

        elif self.etap == 2:
            self.etap += 1
            self.funkcja = self.funkcje[self.cb.currentIndex()]
            self.label.setText("Wybierz początek przedziału")
            self.layout.removeWidget(self.cb)
            self.layout.removeWidget(self.next)
            self.cb.deleteLater()
            self.layout.addWidget(self.slider)
            self.layout.addWidget(self.sliderValue)
            self.layout.addWidget(self.next)
        elif self.etap == 3:
            self.etap += 1
            self.poczatek = self.slider.value()
            self.label.setText("Wybierz koniec przedziału")
            self.slider.setRange(self.poczatek + 1, self.poczatek + 100)

        elif self.etap == 4:
            self.etap += 1
            self.koniec = self.slider.value()
            if self.stop == "Ilość iteracji":
                self.slider.setRange(1, 50)
                self.label.setText("Wybierz ilość iteracji")
            else:
                self.label.setText("Wybierz dokładność")
                self.slider.setRange(0, 100)
                self.slider.setValue(50)
                self.sliderValue.setText('0.5')
                self.slider.valueChanged.connect(self.updateLabelFloat)

        elif self.etap == 5:

            temp = 0

            while not self.unimodalnosc():
                print("Funkcja nie jest unimodalna, szukany jest nowy przedział")
                self.poczatek += 5
                self.poczatek -= 5
                temp += 1

                if temp == 50:
                    print("Program nie mógł znaleźć przedziału, w którym funkcja jest unimodalna")
                    exit(-1)

            if self.stop == "Ilość iteracji":
                self.iteracje = self.slider.value()
            else:
                self.dokladnosc = self.slider.value() / 100.0

            if self.metoda == "Metoda bisekcji":
                self.bisekcja()
                self.next.setDisabled(True)
            else:
                self.zlotyPodzial()
                self.next.setDisabled(True)

    def updateLabel(self, value):
        self.sliderValue.setText(str(value))

    def updateLabelFloat(self, value):
        self.sliderValue.setText(str(value / 100.0))

    def samesign(self, a, b):
        return a * b > 0

    def unimodalnosc(self):

        krok = self.poczatek

        y1 = self.funkcja(krok)
        y2 = self.funkcja(krok + 1)
        while krok + 2 <= self.koniec:
            y3 = self.funkcja(krok + 2)
            if (y1 >= y2) and (y2 <= y3):
                return True
            else:
                krok += 1
                y1 = y2
                y2 = y3

        return False

    def bisekcja(self):
        low = self.poczatek
        high = self.koniec

        przedzialy = []

        midpoint = (low + high) / 2.0
        yM = self.funkcja(midpoint)

        if self.stop == "Ilość iteracji":
            for i in range(self.iteracje):

                print("Przedział ( " + str(low) + " ; " + str(high) + " )")
                przedzialy.append(low)
                przedzialy.append(high)

                dlugosc = high - low
                x1 = low + dlugosc / 4.0
                x2 = high - dlugosc / 4.0
                y1 = self.funkcja(x1)
                y2 = self.funkcja(x2)

                if y1 < yM:
                    high = midpoint
                    midpoint = x1
                    yM = y1

                elif y2 < yM:
                    low = midpoint
                    midpoint = x2
                    yM = y2
                else:
                    low = x1
                    high = x2

        else:
            while abs(float(low) - float(high)) <= 2 * self.dokladnosc:

                print("Przedział ( " + str(low) + " ; " + str(high) + " )")
                przedzialy.append(low)
                przedzialy.append(high)

                dlugosc = high - low
                x1 = low + dlugosc / 4.0
                x2 = high - dlugosc / 4.0
                y1 = self.funkcja(x1)
                y2 = self.funkcja(x2)

                if y1 < yM:
                    high = midpoint
                    midpoint = x1
                    yM = y1

                elif y2 < yM:
                    low = midpoint
                    midpoint = x2
                    yM = y2
                else:
                    low = x1
                    high = x2

        X = list(range(self.poczatek, self.koniec))
        Y = []
        for i in X:
            Y.append(self.funkcjaa(i))
            # Y.append(self.funkcja(i))

        plt.figure(200)
        plt.plot(X, Y)
        plt.plot(midpoint, self.funkcjaa(midpoint), 'ro')
        # plt.plot(midpoint, self.funkcja(midpoint), 'ro')

        plt.plot([self.poczatek, self.koniec], [0, 0], label="Unimodalnosc")

        plt.xlim([self.poczatek, self.koniec])
        plt.show()

        plt.figure(300)
        temp = 0
        for i in range(0, len(przedzialy), 2):
            x = [przedzialy[i], przedzialy[i + 1]]
            y = [temp, temp]
            plt.plot(x, y, label="Przedział " + str(temp))
            temp += 1
        plt.show()
        print("Zaimplementowana: " + str(midpoint))
        print("Wbudowana: " + str(optimize.bisect(self.funkcja, self.poczatek, self.koniec)))
        return midpoint

    def zlotyPodzial(self):
        epsilon = self.dokladnosc
        phi = (-1 + math.sqrt(5)) / 2
        a = self.poczatek
        b = self.koniec
        c = (b - a) * (-phi) + b
        d = (b - a) * phi + a
        yC = self.funkcja(c)
        yD = self.funkcja(d)
        przedzialy = []

        if self.stop == "Ilość iteracji":

            for i in range(self.iteracje):
                print("Przedział ( " + str(a) + " ; " + str(b) + " )")
                przedzialy.append(a)
                przedzialy.append(b)
                if yC > yD:
                    a = c
                    c = d
                    yC = yD
                    d = (b - a) * phi + a
                    yD = self.funkcja(d)
                else:
                    b = d
                    d = c
                    yD = yC
                    c = (b - a) * (-phi) + b
                    yC = self.funkcja(c)
        else:
            while abs(b - a) <= 2 * epsilon:
                print("Przedział ( " + str(a) + " ; " + str(b) + " )")
                przedzialy.append(a)
                przedzialy.append(b)
                if yC > yD:
                    a = c
                    c = d
                    yC = yD
                    d = (b - a) * phi + a
                    yD = self.funkcja(d)
                else:
                    b = d
                    d = c
                    yD = yC
                    c = (b - a) * (-phi) + b
                    yC = self.funkcja(c)
        x_opt = (b + a) / 2

        X = list(range(self.poczatek, self.koniec))
        Y = []
        for i in X:
            Y.append(self.funkcja(i))
        plt.plot(X, Y)
        plt.plot(x_opt, self.funkcja(x_opt), 'ro')
        plt.xlim([self.poczatek, self.koniec])
        plt.show()

        plt.figure(300)
        temp = 0
        for i in range(0, len(przedzialy), 2):
            x = [przedzialy[i], przedzialy[i + 1]]
            y = [temp, temp]
            plt.plot(x, y, label="Przedział " + str(temp))
            temp += 1
        plt.show()

        print("Zaimplementowana: " + str(x_opt))
        print("Wbudowana: " + str(optimize.golden(self.funkcja, brack=(self.poczatek, self.koniec))))
        return x_opt

    # STARSZA METODA
    # def zlotyPodzial(self):
    #     epsilon = self.dokladnosc
    #     phi = (1 + 5 ** 0.5) / 2  # golden ratio constant
    #     # krok 1
    #     k = 0
    #     a = {"iteration": k, "value": self.poczatek}
    #     b = {"iteration": k, "value": self.koniec}
    #     l = {"iteration": k, "value": (a["value"] + (1 - phi) * (b["value"] - a["value"]))}  # lambda
    #     mi = {"iteration": k, "value": (a["value"] + phi * (b["value"] - a["value"]))}
    #     fu_mi = self.funkcja(mi["value"])  # wartosc funkcji od mi
    #     fu_la = self.funkcja(l["value"])  # wartosc funkcji od lambda

    #     while (b["value"] - a["value"]) >= 2 * epsilon:  # warunek z kroku 2
    #         # todo
    #         if self.funkcja(l["value"]) > self.funkcja(mi["value"]):
    #             # krok 3
    #             a["iteration"] = k + 1
    #             a["value"] = l["value"]  # z linijki a(k+1)=lambda(k)
    #             b["iteration"] = k + 1  # z linijki b(k+1)=b(k)
    #             l["iteration"] = k + 1
    #             l["value"] = mi["value"]  # z linijki lambda(k+1)=mi(k)
    #             fu_la = self.funkcja(mi["value"])
    #             mi["iteration"] = k + 1
    #             mi["value"] = a["value"] + phi * (b["value"] - a["value"])
    #             fu_mi = self.funkcja(mi["value"])
    #         elif self.funkcja(l["value"]) <= self.funkcja(mi["value"]):
    #             # krok 4
    #             a["iteration"] = k + 1
    #             b["iteration"] = k + 1
    #             b["value"] = mi["value"]
    #             mi["iteration"] = k + 1
    #             mi["value"] = l["value"]
    #             fu_mi = fu_la
    #             l["iteration"] = k + 1
    #             l["value"] = a["value"] + (1 - phi) * (b["value"] - a["value"])
    #             fu_la = self.funkcja(l["value"])
    #         k += 1  # krok 5
    #     x_opt = (a["value"] + b["value"]) / 2

    # print(x_opt)
    # print(a["iteration"])
    # print(b["iteration"])


def main():
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
