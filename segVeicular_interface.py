# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'telaSegVeicular.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import cv2
import imutils 
from pygame import mixer
from picamera.array import PiRGBArray
from picamera import PiCamera

import os
from imutils import face_utils
import matplotlib.pyplot as plt
from matplotlib.backends.backend_template import FigureCanvas
from PyQt5.Qt import QWidget, QLabel, QTime, QGridLayout, QLineEdit,\
    QStringListModel, QTimer, QMessageBox, QInputDialog
import pyqtgraph as pg
from gtts import gTTS

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends import qt_compat
from PyQt5.Qt import QMainWindow, QWidget, Qt, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsScene
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import time
import dlib
import math
from scipy.spatial import distance
from matplotlib.pyplot import xlabel, ylabel
from GerarArquivoDeDados import GerarArquivoDeDados
from DesempenhoProcessador import DesempenhoProcessador
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE

class criarGrafico(QWidget):
    
    def __init__(self, parent=None):
        super(criarGrafico, self).__init__(parent)
        self.configurar()
        self.fig = plt.figure(figsize=(13.2, 2))
        self.data = self.get_data()
        
        self.canvas = self.create_main_frame()
        self.on_draw()

    def configurar(self):
        SMALL_SIZE = 8
        MEDIUM_SIZE = 10
        BIGGER_SIZE = 12

        plt.rc('font', size=BIGGER_SIZE)         # controls default text sizes
        plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
                
    def create_main_frame(self):

        self.canvas = FigureCanvas(self.fig)
        #self.canvas.setFocusPolicy(Qt.StrongFocus)
        #self.canvas.setFocus()
        return  self.canvas
        
    def get_data(self):
        return np.arange(50).reshape([10, 5]).copy()
    
    def on_draw(self):
        self.fig.clear()
        
        #x = np.linspace(0, 100)
        #y = 1e3*np.sin(2*np.pi*x/1e-9) # one period, 1k amplitude
        
        ax = self.fig.add_subplot(111, xlabel='Frames', ylabel='PERCLOS', title="Analise PERCLOS")
        #ax.plot(x, y)
        
        ax.get_yticks([1, 2, 3, 4, 5])
        
        # Change only ax2
        self.canvas.draw()
        
class graficoPERCLOS(QThread):
    plotar = pyqtSignal(pg.PlotItem)
    
    def __init__(self, matriz=np.ndarray, parent=None):
        QThread.__init__(self, parent=parent)
        self.RA = matriz
    
    def run(self):
        while True:
            grafico = pg.PlotWidget(title="GRAFICO EM TEMPO REAL - PERCLOS")
            grafico.setLabels(left="PERCLOS", bottom="Frames")
            x = np.arange(50)
            x2 = np.arange(100)
            y2 = (x2*8)/x2
            
            grafico.setXRange(0, 100, padding=0.05)
            grafico.setYRange(0, 10, padding=0.05)
    
            grafico.plot(x2, y2, pen=pg.mkPen('r', style=QtCore.Qt.DashLine))
    
            for i in range(1):
                grafico.plot(x, self.RA[i], pen=pg.mkPen('b'))
            #return self.grafico.getPlotItem()
            self.plotar.emit(grafico.getPlotItem())
            time.sleep(3)
                        
class Thread(QThread):
    #Captura de Imagem
    changePixmap = pyqtSignal(QPixmap)
    #Contador para calcular o FPS
    contadorLoop = pyqtSignal(str)
    
    #Resumo da Calibragem PERCLOS
    valorMaxPERCLOS = pyqtSignal(str)
    valorMinPERCLOS = pyqtSignal(str)
    P80 = pyqtSignal(str)
    
    #Alimentaçao de dados dos Graficos
    plotar = pyqtSignal(pg.PlotItem)
    plotarCalibragem = pyqtSignal(pg.PlotItem)
    
    #Dados para a tela de log
    msgLog = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent=parent)
        
        self.arq_predicao = "shape_predictor_68_face_landmarks.dat"
        self.detector = dlib.get_frontal_face_detector()
        self.predicao = dlib.shape_predictor(self.arq_predicao)
        
    def run(self):
        cap = cv2.VideoCapture(0)
        hora = QTime()
        start_time = time.time()
        cont = 0
        fps = 0
        contImgCalibracao = 0
        self.matrizRA = np.zeros((5, 200))
        p80_porcento = []
        dados_tempo_real = []
        eixox_dados_tempo_real = []
        
        #Script inicial
        mixer.init()
        mixer.music.load("boas-vindas.mp3")
        mixer.music.play()
        time.sleep(18)
        mixer.music.load("auxilio-calibracao.mp3")
        mixer.music.play()
        time.sleep(6)
        mixer.music.load("auxilio-calibracao-olhos-fechados.mp3")
        mixer.music.play()
        time.sleep(10)
        
        #contar
        mixer.music.load("contar-um.mp3")
        mixer.music.play()
        time.sleep(1)
        mixer.music.load("contar-dois.mp3")
        mixer.music.play()
        time.sleep(1)
        mixer.music.load("contar-tres.mp3")
        mixer.music.play()
        time.sleep(1)
        
        camera = PiCamera()
        camera.resolution = (320, 240)
        camera.framerate = 30
        rawCapture = PiRGBArray(camera, size=(320, 240))
        
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            
            frame = frame.array
            if frame is None:
                time.sleep(0.1)
                print('vazio')
                
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            rects = self.detector(gray, 1)

            for rect in rects:
                self.shape = self.predicao(gray, rect)
               
                # Transforma os valores predicados do rosto para um array NumPy
                self.shape = face_utils.shape_to_np(self.shape)
                for (x, y) in self.shape:
                    cv2.circle(rgbImage, (x, y), 4, (0, 0, 255), -1)
                    
                if (contImgCalibracao < 200):
                    if(contImgCalibracao == 99):
                        mixer.music.load("ok-auxilio-calibracao-olhos-abertos.mp3")
                        mixer.music.play()
                        time.sleep(12)
                        mixer.music.load("contar-um.mp3")
                        mixer.music.play()
                        time.sleep(1)
                        mixer.music.load("contar-dois.mp3")
                        mixer.music.play()
                        time.sleep(1)
                        mixer.music.load("contar-tres.mp3")
                        mixer.music.play()
                        time.sleep(1)
                    
                    if (contImgCalibracao == 0):
                        self.msgLog.emit(hora.currentTime().toString() + " - Aquisicao de dados para calibracao")
                    self.matrizRA[0][contImgCalibracao] = self.razaoDeAspecto(self.shape)
                    self.matrizRA[1][contImgCalibracao] = self.desvioPadrao(contImgCalibracao)
                    self.matrizRA[2][contImgCalibracao] = self.erroPadrao(contImgCalibracao)
                    self.matrizRA[4][contImgCalibracao] = 70
                    
                    if (contImgCalibracao < 100):
                        self.matrizRA[3][contImgCalibracao] = 0
                    else:
                        self.matrizRA[3][contImgCalibracao] = 1
                        
                    contImgCalibracao +=1
                    

                    print("Estou coletando dados... ")
                elif (contImgCalibracao == 200):
                    mixer.music.load("ok.mp3")
                    mixer.music.play()
                    x = np.arange(200)
                    x = x.tolist()
                    y = []
                    for i in range(len(self.matrizRA[0])):
                        if (i == 0):
                            self.msgLog.emit("Razao de Aspecto; Desvio Padrao; Erro Padrao")
                        y.append(self.matrizRA[0][i])
                        msg = (str(round(self.matrizRA[0][i], 5)) +"; "+
                               str(round(self.matrizRA[1][i], 5)) +"; "+
                               str(round(self.matrizRA[2][i], 5)) +"; ")
                        self.msgLog.emit(msg)
                    self.msgLog.emit(hora.currentTime().toString() + " - Calibracao")
                    self.calibragemAberturaOlhos()
                    self.matrizAnalitica = self.converterParaPorcentagem()
                    contImgCalibracao +=1
                    
                    grafico = pg.PlotWidget(title="GRAFICO AQUISIÇAO DE DADOS INICIAL PARA CALIBRAGEM")
                    grafico.setLabels(left="PERCLOS", bottom="Frames")
                    grafico.getPlotItem().showGrid(True, True, 0.2)
                    grafico.setXRange(0, 200, padding=0)
                
                    #linhaPERCLOS = grafico.pl
                    grafico.plot(x, y, pen=pg.mkPen('b'))
                        
                    self.plotarCalibragem.emit(grafico.getPlotItem())
                    
                    self.valorMaxPERCLOS.emit(str(round(self.matrizRA[0].max(), 3)))
                    self.valorMinPERCLOS.emit(str(round(self.matrizRA[0].min(), 3)))
                    valorRAdoP80 = ((self.matrizRA[0].max() - self.matrizRA[0].min()) * 0.8) + self.matrizRA[0].min()
                    self.P80.emit(str(round(valorRAdoP80, 3)))
                    
                    arrayDados = self.matrizRA.tolist()
                    print(arrayDados)
                    arquivo = GerarArquivoDeDados()
                    arquivo.gerarCSV(arrayDados)
                    
                    print("Estou calibrando os dados..." + str(contImgCalibracao))
                else:
                    if (contImgCalibracao == 201):
                        self.msgLog.emit(hora.currentTime().toString() + " - Execucao do sistema")
                        eixox_P80 = np.arange(200)
                        eixox_P80 = eixox_P80.tolist()
                        for i in range(200):
                            p80_porcento.append(80)
                    else:
                        eixox_P80.append(len(eixox_P80)+1)
                        p80_porcento.append(80)
                        dados_tempo_real.append((self.razaoDeAspecto(self.shape) - self.matrizRA[0].min()) / (self.matrizRA[0].max() - self.matrizRA[0].min()) * 100)
                        eixox_dados_tempo_real.append(len(eixox_dados_tempo_real)+1)
                        print(str((self.razaoDeAspecto(self.shape) - self.matrizRA[0].min()) / (self.matrizRA[0].max() - self.matrizRA[0].min()) * 100))
                    contImgCalibracao +=1
                    
                        #self.calibracao.emit(self.matrizAnalitica)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
            
            p = convertToQtFormat.scaled(357, 273, Qt.KeepAspectRatio)
            
            cont = cont + 1
            if (contImgCalibracao > 201 ):
                #print("eixox_P80: " + type(eixox_P80))
                #print("p80_porcento: " + type(p80_porcento))
                
                #print("eixox_dados_tempo_real: " + type(eixox_dados_tempo_real))
                #print("dados_tempo_real: " + type(dados_tempo_real))
                
                grafico = pg.PlotWidget(title="GRAFICO EM TEMPO REAL - PERCLOS")
                grafico.setLabels(left="PERCLOS", bottom="Frames")
                grafico.getPlotItem().showGrid(True, True, 0.2)
                grafico.setXRange(0, 1000, padding=0)
                grafico.setYRange(0, 100, padding=0)
                
                #linhaPERCLOS = grafico.pl
                grafico.plot(eixox_P80, p80_porcento, pen=pg.mkPen('r', style=QtCore.Qt.DashLine))
                grafico.plot(eixox_dados_tempo_real, dados_tempo_real, pen=pg.mkPen('b'))
                #print('percentual: ' + str(dados_tempo_real[len(dados_tempo_real)]))  
                #return Declaraself.grafico.getPlotItem()
                self.plotar.emit(grafico.getPlotItem())
                
            if (int(time.time() - start_time) == 1 ):
                print("Estou dentro do Time...")
                fps = cont
                cont = 0
                start_time = time.time()
            rawCapture.truncate(0)         
            #self.changePixmap.emit(p)
            self.contadorLoop.emit(str(fps))
              
    #Calculando a Razao de Aspecto
    def razaoDeAspecto(self, shape):
        
        #RAD = RAZAO DE ASPECTO DIREITA
        distVerticalDir = distance.euclidean((shape[43] + shape[44]) // 2, (shape[47] + shape[46]) // 2) 
        distHorizontalDir = distance.euclidean(shape[42], shape[45])
        rad = distVerticalDir / distHorizontalDir
        
        
        #RAE = RAZAO DE ASPECTO ESQUERDA
        distVerticalEsq = distance.euclidean((shape[37] + shape[38]) // 2, (shape[41] + shape[40]) // 2) 
        distHorizontalEsq = distance.euclidean(shape[36], shape[39])
        rae = distVerticalEsq / distHorizontalEsq
       
        ra = (rad + rae) / 2
        #alturaMedia = (distVerticalDir + distVerticalEsq) / 2
        return ra
        #return alturaMedia
    
    #Calcular desvio padrao
    def desvioPadrao(self, x):
        variancia, media = 0, 0
        count = 0
        
        #Calculo da media
        for i in range(x + 1):
            media += self.matrizRA[0][i]
            count += 1
        media = media / count
    
        #Calculo da variancia
        for j in range(x + 1):
            variancia = variancia + math.pow((self.matrizRA[0][j] - media), 2)
        variancia = variancia / count
    
        #Raiz quadrada da variancia
        devPadrao = math.sqrt(variancia)
        return devPadrao
    
    #Calcular erro padrao
    def erroPadrao(self, x):
        if x > 0:
            erroPad = self.matrizRA[1][x] / math.sqrt(x)
        else:
            erroPad = 0
        return erroPad
    
    def calibragemAberturaOlhos(self):
        valorMaxOlho, valorMinOlho, flagValorMax, flagValorMin = 0, 0, 0, 0
        for x in range(200):
            if valorMaxOlho < self.matrizRA[0][x]:
                valorMaxOlho = self.matrizRA[0][x]
                flagValorMax = x
    
            if (valorMinOlho > self.matrizRA[0][x]) or (valorMinOlho == 0):
                valorMinOlho = self.matrizRA[0][x]
                flagValorMin = x
    
        self.matrizRA[0][flagValorMax] = self.matrizRA[0][flagValorMax] - self.matrizRA[2][flagValorMax]
        self.matrizRA[0][flagValorMin] = self.matrizRA[0][flagValorMin] + self.matrizRA[2][flagValorMin]
        
    #eh necessario ??????
    def converterParaPorcentagem(self):
        matrizAnalitica = []
        aberturaMin = self.matrizRA[0].min()
        aberturaMax = self.matrizRA[0].max()
        for i in range(len(self.matrizRA[0])):
            #Calcular a porcentagem
            porcentagem = (self.matrizRA[0][i] - aberturaMin) / (aberturaMax - aberturaMin) * 100
            matrizAnalitica.append(porcentagem)
        return matrizAnalitica
            
class HoraThread(QThread):
    horario = pyqtSignal(str)
    startTelaDeLog = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent=parent)
        
    def run(self):
        time = QTime()
        hora = time.currentTime().toString()
        #self.startTelaDeLog.emit(hora + " - Inicializaçao do Sistema")
        while True:
            hora = time.currentTime().toString()
            self.horario.emit(hora)
                        
class FaceDetectionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._width = 2
        self.image = QtGui.QImage()
        
    def image_data_slot(self, image_data):

        self.image = self.get_qimage(image_data)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())

        self.update()

    

class BoasVindas(QWidget):
    def __init__(self):
        super(BoasVindas, self).__init__()
        self.horario = QTime()
        
    def getNome(self):
        msg, ok = QInputDialog.getText(self, 'Bem Vindo!', 'Ola, qual eh seu nome?')
        
        if ok:
            script = ("Meu nome eh Judite, e eu irei lhe auxiliar em sua viagem analisando seu estado fisico e mental" +
                      "para evitar qualquer desatenção durante o percurso...")
            #if (self.horario.currentTime() > QTime(5, 59) and self.horario.currentTime() < QTime(12, 0)):
                #tts = gTTS(text='Ola, bom dia ' + msg +"." + script, lang='pt')
                #tts.save("boas-vindas.mp3")
                #return msg
            #elif (self.horario.currentTime() > QTime(11, 59) and self.horario.currentTime() < QTime(18, 0)):
                #tts = gTTS(text='Ola, boa tarde ' + msg + "." + script, lang='pt')
                #tts.save("boas-vindas.mp3")
                #return msg
            #else:
                #tts = gTTS(text='Ola, boa noite ' + msg + "." + script, lang='pt')
                #tts.save("boas-vindas.mp3")
                #return msg

class Ui_MainWindow(QWidget):
    
    def setupUi(self, MainWindow):
        self.showFullScreen()
        self.setHidden(True)
        
        MainWindow.setObjectName("Segurança Veicular")
        MainWindow.setEnabled(True)
        MainWindow.resize(self.size())
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayoutWidgetLog = QtWidgets.QGroupBox(self.centralwidget)
        self.verticalLayoutWidgetLog.setTitle("Tela de Log")
        self.verticalLayoutWidgetLog.setGeometry(QtCore.QRect(920, 10, 435, 289))
        self.verticalLayoutWidgetLog.setObjectName("verticalLayoutLog")
        self.verticalLayoutWidgetLog.setWindowTitle("LOG")
        
        self.verticalLayoutLog = QtWidgets.QVBoxLayout(self.verticalLayoutWidgetLog)
        self.verticalLayoutLog.setContentsMargins(2, 2, 2, 2)
        self.verticalLayoutLog.setObjectName("verticalLayoutLog")
        
        self.txtLog = QtWidgets.QPlainTextEdit(self.verticalLayoutWidgetLog)
        self.txtLog.setWindowTitle("Log")
        self.txtLog.setReadOnly(True)
        self.verticalLayoutLog.addWidget(self.txtLog)
        
        self.verticalLayoutWidgetCamera = QtWidgets.QGroupBox(self.centralwidget)
        self.verticalLayoutWidgetCamera.setTitle("Camera")
        self.verticalLayoutWidgetCamera.setGeometry(QtCore.QRect(550, 10, 361, 289))
        self.verticalLayoutWidgetCamera.setObjectName("verticalLayoutWidgetCamera")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidgetCamera)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.label = QtWidgets.QLabel(self.verticalLayoutWidgetCamera)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        
        self.horizontalLayoutWidget = QtWidgets.QGroupBox(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 304, 1345, 241))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.horizontalLayoutWidget.setLayout(self.horizontalLayout)
        
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        
        self.graficoMicro = pg.PlotWidget(self.horizontalLayoutWidget, title="GRAFICO EM REAL TIME - PERCLOS ANALISE")
        self.graficoMicro.setXRange(0, 1000, padding=0)
        self.graficoMicro.setYRange(0, 100, padding=0)
        self.graficoMicro.getPlotItem().showGrid(True, True, 0.2)
        self.horizontalLayout.addWidget(self.graficoMicro)
        
        self.horizontalLayoutWidget_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 550, 1345, 150))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.graficoMacro = pg.PlotWidget(self.horizontalLayoutWidget, title="GRAFICO AQUISIÇAO DE DADOS INICIAL PARA CALIBRAGEM")
        self.graficoMacro.setLabels(left="PERCLOS", bottom="Frames")    
        self.graficoMacro.setXRange(0, 200, padding=0)
        self.graficoMacro.setYRange(0, 1, padding=0)
        self.graficoMacro.getPlotItem().showGrid(True, True, 0.2)
        self.horizontalLayout_2.addWidget(self.graficoMacro)
        
        self.horizontalLayoutWidget_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 531, 41))
        self.horizontalLayoutWidget_3.setTitle("Estado do Sistema")
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        
        self.layoutParteSuperior = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.layoutParteSuperior.setContentsMargins(2, 2, 2, 2)
        self.layoutParteSuperior.setObjectName("layoutParteSuperior")
        #self.layoutParteSuperior.addWidget(Borda().linha)
        
        ##----------FPS----------##
        self.lbFPS = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        #self.lbFPS.setObjectName("lbFPS")
        self.lbFPS.setText("FPS")
              
        self.lcdFPS = QtWidgets.QLCDNumber(self.horizontalLayoutWidget_3)
        self.lcdFPS.setObjectName("lcdFPS")
        
        ##----------Marcador de Tempo----------##
        self.lbTempo = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        #self.lbTempo.setObjectName("lbTempo")
        self.lbTempo.setText("Tempo")
        
        self.timeEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.timeEdit.setObjectName("timeEdit")
        
        hora = QTime()
        self.timeEdit.setText(hora.currentTime().toString())
        
        ##----------Marcador da Ultima Parada----------##
        self.lbProcessoCPU = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        #self.lbProcessoCPU.setObjectName("lbProcessoCPU")
        self.lbProcessoCPU.setText("CPU: ")
        
        self.txtProcessoCPU = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.txtProcessoCPU.setObjectName("txtProcessoCPU")
       
        ##----------Sinalizador de Alertas----------##
        self.lbEstado = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.lbEstado.setObjectName("lbEstado")
        self.lbEstado.setText("Estado: ")
        self.lbAlerta = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.lbAlerta.setObjectName("lbAlerta")
        pixmap = QPixmap("logo-pronto.png")
        self.lbAlerta.setAlignment(QtCore.Qt.AlignCenter)
        self.lbAlerta.setPixmap(pixmap)
        self.lbAlerta.show()

        
        #Layout da parte superior
        self.layoutParteSuperior.addWidget(self.lbFPS)
        self.layoutParteSuperior.addWidget(self.lcdFPS)
        self.layoutParteSuperior.addWidget(self.lbTempo)
        self.layoutParteSuperior.addWidget(self.timeEdit)
        self.layoutParteSuperior.addWidget(self.lbProcessoCPU)
        self.layoutParteSuperior.addWidget(self.txtProcessoCPU)
        self.layoutParteSuperior.addWidget(self.lbEstado)
        self.layoutParteSuperior.addWidget(self.lbAlerta)
        
        
        #---------- Layout de Análise PERCLOS ----------
        self.layoutPERCLOS = QtWidgets.QGroupBox(self.centralwidget)
        self.layoutPERCLOS.setGeometry(QtCore.QRect(375, 55, 166, 93))
        self.layoutPERCLOS.setObjectName("layoutPERCLOS")
        self.layoutPERCLOS.setTitle("Resumo de Calib. PERCLOS (RA)")
        
        self.formLayout = QtWidgets.QFormLayout(self.layoutPERCLOS)
        self.formLayout.setContentsMargins(2, 2, 2, 2)
        self.formLayout.setObjectName("formLayout")
        
        self.lbValorMaxPERCLOS = QtWidgets.QLabel(self.layoutPERCLOS)
        self.lbValorMaxPERCLOS.setObjectName("lbValorMaxPERCLOS")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbValorMaxPERCLOS)
        
        self.lbValorMinPERCLOS = QtWidgets.QLabel(self.layoutPERCLOS)
        self.lbValorMinPERCLOS.setObjectName("lbValorMinPERCLOS")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lbValorMinPERCLOS)
        
        self.lbP80 = QtWidgets.QLabel(self.layoutPERCLOS)
        self.lbP80.setObjectName("lbP80")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lbP80)
        
        self.txtValorMaxPERCLOS = QtWidgets.QLineEdit(self.layoutPERCLOS)
        self.txtValorMaxPERCLOS.setObjectName("txtValorMaxPERCLOS")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtValorMaxPERCLOS)
        
        self.txtValorMinPERCLOS = QtWidgets.QLineEdit(self.layoutPERCLOS)
        self.txtValorMinPERCLOS.setObjectName("txtValorMinPERCLOS")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtValorMinPERCLOS)
        
        self.txtP80 = QtWidgets.QLineEdit(self.layoutPERCLOS)
        self.txtP80.setObjectName("txtP80")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtP80)
        
        #---------- Layout de Analise Piscadas ----------
        self.layoutPiscada = QtWidgets.QGroupBox(self.centralwidget)
        self.layoutPiscada.setGeometry(QtCore.QRect(10, 55, 351, 120))
        #self.layoutPiscada.setFrameShape(QtWidgets.QFrame.StyledPanel)
        #self.layoutPiscada.setFrameShadow(QtWidgets.QFrame.Raised)
        self.layoutPiscada.setObjectName("layoutPiscada")
        self.layoutPiscada.setTitle("Analise Piscadas")
        
        self.gridLayoutPiscada = QtWidgets.QGridLayout(self.layoutPiscada)
        self.gridLayoutPiscada.setObjectName("gridLayoutPiscada")
        self.gridLayoutPiscada.setContentsMargins(2, 2, 2, 2)
        
        self.lbMinutosAntesPiscada = QtWidgets.QLabel(self.layoutPiscada)
        self.lbMinutosAntesPiscada.setObjectName("lbMinutosAntesPiscada")
        self.gridLayoutPiscada.addWidget(self.lbMinutosAntesPiscada, 0, 3, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.txtMaximaPiscada = QtWidgets.QLineEdit(self.layoutPiscada)
        self.txtMaximaPiscada.setObjectName("txtMaximaPiscada")
        self.gridLayoutPiscada.addWidget(self.txtMaximaPiscada, 1, 1, 1, 1)
        
        self.lbMaximaPiscada = QtWidgets.QLabel(self.layoutPiscada)
        self.lbMaximaPiscada.setObjectName("lbMaximaPiscada")
        self.gridLayoutPiscada.addWidget(self.lbMaximaPiscada, 1, 0, 1, 1)
        
        self.lbMinimaPiscada = QtWidgets.QLabel(self.layoutPiscada)
        self.lbMinimaPiscada.setObjectName("lbMinimaPiscada")
        self.gridLayoutPiscada.addWidget(self.lbMinimaPiscada, 2, 0, 1, 1)
        
        self.txtMinimaPiscada = QtWidgets.QLineEdit(self.layoutPiscada)
        self.txtMinimaPiscada.setObjectName("txtMinimaPiscada")
        self.gridLayoutPiscada.addWidget(self.txtMinimaPiscada, 2, 1, 1, 1)
        
        self.lbReferenciaTempoPiscadaMax = QtWidgets.QLabel(self.layoutPiscada)
        self.lbReferenciaTempoPiscadaMax.setObjectName("lbReferenciaTempoPiscadaMax")
        self.gridLayoutPiscada.addWidget(self.lbReferenciaTempoPiscadaMax, 1, 2, 1, 1)
        
        self.txtReferenciaTempoPiscadaMax = QtWidgets.QLineEdit(self.layoutPiscada)
        self.txtReferenciaTempoPiscadaMax.setObjectName("txtReferenciaTempoPiscadaMax")
        self.gridLayoutPiscada.addWidget(self.txtReferenciaTempoPiscadaMax, 2, 3, 1, 1)
        
        self.txtReferenciaTempoPiscada_2 = QtWidgets.QLineEdit(self.layoutPiscada)
        self.txtReferenciaTempoPiscada_2.setObjectName("txtReferenciaTempoPiscada_2")
        self.gridLayoutPiscada.addWidget(self.txtReferenciaTempoPiscada_2, 1, 3, 1, 1)
        
        self.lbPiscada = QtWidgets.QLabel(self.layoutPiscada)
        self.lbPiscada.setObjectName("lbPiscada")
        self.gridLayoutPiscada.addWidget(self.lbPiscada, 0, 0, 1, 1)
        
        self.lbPorMinutoPiscada = QtWidgets.QLabel(self.layoutPiscada)
        self.lbPorMinutoPiscada.setObjectName("lbPorMinutoPiscada")
        self.gridLayoutPiscada.addWidget(self.lbPorMinutoPiscada, 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.lbReferenciaTempoPiscadaMin = QtWidgets.QLabel(self.layoutPiscada)
        self.lbReferenciaTempoPiscadaMin.setObjectName("lbReferenciaTempoPiscadaMin")
        self.gridLayoutPiscada.addWidget(self.lbReferenciaTempoPiscadaMin, 2, 2, 1, 1)
        
        self.lbMediana = QtWidgets.QLabel(self.layoutPiscada)
        self.lbMediana.setObjectName("lbMediana")
        self.gridLayoutPiscada.addWidget(self.lbMediana, 3, 0, 1, 1)
        
        self.txtMediana = QtWidgets.QLineEdit(self.layoutPiscada)
        self.txtMediana.setObjectName("txtMediana")
        self.gridLayoutPiscada.addWidget(self.txtMediana, 3, 1, 1, 1)
                
        #---------- Layout de Analise Bocejo ----------
        self.layoutBocejo = QtWidgets.QGroupBox(self.centralwidget)
        self.layoutBocejo.setGeometry(QtCore.QRect(10, 179, 351, 120))
        self.layoutBocejo.setObjectName("layoutBocejo")
        self.layoutBocejo.setTitle("Analise Bocejo")
        
        self.gridLayoutBocejo = QtWidgets.QGridLayout(self.layoutBocejo)
        self.gridLayoutBocejo.setObjectName("gridLayoutBocejo")
        
        self.lbMinAntesBocejo = QtWidgets.QLabel(self.layoutBocejo)
        self.lbMinAntesBocejo.setObjectName("lbMinAntesBocejo")
        self.gridLayoutBocejo.addWidget(self.lbMinAntesBocejo, 0, 3, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.txtMaximaBocejo = QtWidgets.QLineEdit(self.layoutBocejo)
        self.txtMaximaBocejo.setObjectName("txtMaximaBocejo")
        self.gridLayoutBocejo.addWidget(self.txtMaximaBocejo, 1, 1, 1, 1)
        
        self.lbMaximaBocejo = QtWidgets.QLabel(self.layoutBocejo)
        self.lbMaximaBocejo.setObjectName("lbMaximaBocejo")
        self.gridLayoutBocejo.addWidget(self.lbMaximaBocejo, 1, 0, 1, 1)
        
        self.lbMinimaBocejo = QtWidgets.QLabel(self.layoutBocejo)
        self.lbMinimaBocejo.setObjectName("lbMinimaBocejo")
        self.gridLayoutBocejo.addWidget(self.lbMinimaBocejo, 2, 0, 1, 1)
        
        self.txtMinimoBocejo = QtWidgets.QLineEdit(self.layoutBocejo)
        self.txtMinimoBocejo.setObjectName("txtMinimoBocejo")
        self.gridLayoutBocejo.addWidget(self.txtMinimoBocejo, 2, 1, 1, 1)
        
        self.lbReferenciaTempoBocejoMax = QtWidgets.QLabel(self.layoutBocejo)
        self.lbReferenciaTempoBocejoMax.setObjectName("lbReferenciaTempoBocejoMax")
        self.gridLayoutBocejo.addWidget(self.lbReferenciaTempoBocejoMax, 1, 2, 1, 1)
        
        self.txtReferenciaTempoBocejoMin = QtWidgets.QLineEdit(self.layoutBocejo)
        self.txtReferenciaTempoBocejoMin.setObjectName("txtReferenciaTempoBocejoMin")
        self.gridLayoutBocejo.addWidget(self.txtReferenciaTempoBocejoMin, 2, 3, 1, 1)
        
        self.txtReferenciaTempoBocejoMax = QtWidgets.QLineEdit(self.layoutBocejo)
        self.txtReferenciaTempoBocejoMax.setObjectName("txtReferenciaTempoBocejoMax")
        self.gridLayoutBocejo.addWidget(self.txtReferenciaTempoBocejoMax, 1, 3, 1, 1)
        
        self.lbBocejo = QtWidgets.QLabel(self.layoutBocejo)
        self.lbBocejo.setObjectName("lbBocejo")
        self.gridLayoutBocejo.addWidget(self.lbBocejo, 0, 0, 1, 1)
        
        self.lbPorMinutoBocejo = QtWidgets.QLabel(self.layoutBocejo)
        self.lbPorMinutoBocejo.setObjectName("lbPorMinutoBocejo")
        self.gridLayoutBocejo.addWidget(self.lbPorMinutoBocejo, 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.lbReferenciaTempoBocejoMin = QtWidgets.QLabel(self.layoutBocejo)
        self.lbReferenciaTempoBocejoMin.setObjectName("lbReferenciaTempoBocejoMin")
        self.gridLayoutBocejo.addWidget(self.lbReferenciaTempoBocejoMin, 2, 2, 1, 1)
        
        self.lbMedianaBocejo = QtWidgets.QLabel(self.layoutBocejo)
        self.lbMedianaBocejo.setObjectName("lbMedianaBocejo")
        self.gridLayoutBocejo.addWidget(self.lbMedianaBocejo, 3, 0, 1, 1)
        
        self.txtMedianaBocejo = QtWidgets.QLineEdit(self.layoutBocejo)
        self.txtMedianaBocejo.setObjectName("txtMedianaBocejo")
        self.gridLayoutBocejo.addWidget(self.txtMedianaBocejo, 3, 1, 1, 1)
        
        #---------- Layout de Analise Estatisticas do PERCLOS ----------
        self.layoutEstatisticaPERCLOS = QtWidgets.QGroupBox(self.centralwidget)
        self.layoutEstatisticaPERCLOS.setGeometry(QtCore.QRect(375, 152, 166, 147))
        self.layoutEstatisticaPERCLOS.setObjectName("layoutEstatisticaPERCLOS")
        self.layoutEstatisticaPERCLOS.setTitle("Estatistica PERCLOS")

        self.gridLayoutPiscada_3 = QtWidgets.QGridLayout(self.layoutEstatisticaPERCLOS)
        self.gridLayoutPiscada_3.setContentsMargins(2, 2, 2, 2)
        self.gridLayoutPiscada_3.setObjectName("gridLayoutPiscada_3")
        
        self.lbBaixoPerclosMedia = QtWidgets.QLabel(self.layoutEstatisticaPERCLOS)
        self.lbBaixoPerclosMedia.setObjectName("lbBaixoPerclosMedia")
        self.gridLayoutPiscada_3.addWidget(self.lbBaixoPerclosMedia, 2, 0, 1, 1)
        
        self.txtBaixoPerclosMedia = QtWidgets.QLineEdit(self.layoutEstatisticaPERCLOS)
        self.txtBaixoPerclosMedia.setObjectName("txtBaixoPerclosMedia")
        self.gridLayoutPiscada_3.addWidget(self.txtBaixoPerclosMedia, 2, 1, 1, 1)
        
        self.txtAltoPerclos = QtWidgets.QLineEdit(self.layoutEstatisticaPERCLOS)
        self.txtAltoPerclos.setObjectName("txtAltoPerclos")
        self.gridLayoutPiscada_3.addWidget(self.txtAltoPerclos, 3, 1, 1, 1)
        
        self.txtBaixoPerclos = QtWidgets.QLineEdit(self.layoutEstatisticaPERCLOS)
        self.txtBaixoPerclos.setObjectName("txtBaixoPerclos")
        self.gridLayoutPiscada_3.addWidget(self.txtBaixoPerclos, 1, 1, 1, 1)
        
        self.lbAltoPerclos = QtWidgets.QLabel(self.layoutEstatisticaPERCLOS)
        self.lbAltoPerclos.setObjectName("lbAltoPerclos")
        self.gridLayoutPiscada_3.addWidget(self.lbAltoPerclos, 3, 0, 1, 1)
        
        self.lbPorMinutoResumoPerclos = QtWidgets.QLabel(self.layoutEstatisticaPERCLOS)
        self.lbPorMinutoResumoPerclos.setObjectName("lbPorMinutoResumoPerclos")
        self.gridLayoutPiscada_3.addWidget(self.lbPorMinutoResumoPerclos, 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        
        self.lbBaixoPerclos = QtWidgets.QLabel(self.layoutEstatisticaPERCLOS)
        self.lbBaixoPerclos.setObjectName("lbBaixoPerclos")
        self.gridLayoutPiscada_3.addWidget(self.lbBaixoPerclos, 1, 0, 1, 1)
        
        self.lbAltoPerclosMedia = QtWidgets.QLabel(self.layoutEstatisticaPERCLOS)
        self.lbAltoPerclosMedia.setObjectName("lbAltoPerclosMedia")
        self.gridLayoutPiscada_3.addWidget(self.lbAltoPerclosMedia, 4, 0, 1, 1)
        
        self.txtAltoPerclosMedia = QtWidgets.QLineEdit(self.layoutEstatisticaPERCLOS)
        self.txtAltoPerclosMedia.setObjectName("txtAltoPerclosMedia")
        self.gridLayoutPiscada_3.addWidget(self.txtAltoPerclosMedia, 4, 1, 1, 1)
        
        boasVindas = BoasVindas()
        self.usuario = boasVindas.getNome()
        
        thHora = HoraThread(self)
        thHora.horario.connect(self.timeEdit.setText)
        thHora.startTelaDeLog.connect(self.txtLog.setPlainText)
        thHora.start()
    
        th = Thread(self)
        th.changePixmap.connect(self.label.setPixmap)
        th.contadorLoop.connect(self.lcdFPS.display)
        th.plotar.connect(self.graficoMicro.setCentralWidget)
        th.plotarCalibragem.connect(self.graficoMacro.setCentralWidget)
        th.valorMaxPERCLOS.connect(self.txtValorMaxPERCLOS.setText)
        th.valorMinPERCLOS.connect(self.txtValorMinPERCLOS.setText)
        th.P80.connect(self.txtP80.setText)
        th.msgLog.connect(self.txtLog.appendPlainText)

        th.start()
        
        thCPU = DesempenhoProcessador(self)
        thCPU.desempenhoCPU.connect(self.txtProcessoCPU.setText)
        thCPU.start()
        #if (th.isFinished()):
        #    print("Ola")
        #    self.graficoDeAnalisePERCLOS = graficoPERCLOS(self, self.matriz)
        #    self.graficoDeAnalisePERCLOS.plotar.connect(self.graficoMicro.setCentralWidget)
        #    self.graficoDeAnalisePERCLOS.start()
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def dados(self, matriz):
        self.matriz = matriz
        
    def setPixMap(self, p):     
        p = QPixmap.fromImage(p)    
        p = p.scaled(320, 240, Qt.KeepAspectRatio)
        self.label.setPixmap(p)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Seguranca Veicular TCC"))
 
        self.lbValorMaxPERCLOS.setText(u"Valor Max.")
        self.lbValorMinPERCLOS.setText("Valor Min.")
        self.lbP80.setText("P80")
        self.lbMinutosAntesPiscada.setText("min. antes")
        self.lbMaximaPiscada.setText("Maxima")
        self.lbMinimaPiscada.setText("Minima")
        self.lbReferenciaTempoPiscadaMax.setText("Ref. Tempo")
        self.lbPiscada.setText("Piscada")
        self.lbPorMinutoPiscada.setText("por min.")
        self.lbReferenciaTempoPiscadaMin.setText("Ref. Tempo")
        self.lbMediana.setText("Mediana")
        self.lbMinAntesBocejo.setText("min. antes")
        self.lbMaximaBocejo.setText("Maxima")
        self.lbMinimaBocejo.setText("Minima")
        self.lbReferenciaTempoBocejoMax.setText("Ref. Tempo")
        self.lbBocejo.setText("Bocejo")
        self.lbPorMinutoBocejo.setText("por min.")
        self.lbReferenciaTempoBocejoMin.setText("Ref. Tempo")
        self.lbMedianaBocejo.setText("Mediana")
        self.lbBaixoPerclosMedia.setText("B. PERCLOS Med.")
        self.lbAltoPerclos.setText("Alto PERCLOS")
        self.lbPorMinutoResumoPerclos.setText("por min.")
        self.lbBaixoPerclos.setText("Baixo PERCLOS")
        self.lbAltoPerclosMedia.setText("A. PERCLOS Med.")

class Borda(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.st = QStringListModel
        self.linha = QLineEdit()
        self.linha.setStyleSheet(self.configurarLinha())
    
    def configurarLinha(self):
        self.st = ("border-right: 10px solid blue;" + 
                    "border-top: 10px solid blue;" + 
                    "border-left: 10px solid blue;" + 
                    "border-bottom: 10px solid blue;")
        return self.st

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    MainWindow.resize(250, 150)
    MainWindow.move(300, 300)
    MainWindow.setWindowTitle('Sistema de Seguranca Veicular')
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

