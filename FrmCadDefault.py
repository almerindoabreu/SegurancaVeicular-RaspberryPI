from __future__ import print_function

import sys

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from PyQt5.Qt import *
import matplotlib.animation as animation

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        #self.x, self.y = self.get_data()
        
        self.data = self.get_data()
        self.create_main_frame()
        self.update()

    def create_main_frame(self):
        self.main_frame = QWidget()
        
        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.canvas.mpl_connect('key_press_event', self.on_key_press)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def get_data(self):
        while True:
            yield np.random.rand(10)
            
    def update(self, data):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        
        #self.axes.plot(self.x, self.y, 'ro')
        self.axes.imshow(self.data, interpolation='nearest')
        #self.axes.plot([1,2,3])
        self.canvas.draw()
        
        line, = self.axes.plot(np.random.rand(10))
        self.axes.set_ylim(0, 1)
        line.set_ydata(data)
        return line,

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.canvas, self.mpl_toolbar)


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
