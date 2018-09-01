# -*- coding: utf-8 -*-
'''
Created on 16 de jun de 2018

@author: almer
'''
from PyQt5.Qt import QTime, QThread, pyqtSignal, QPixmap
import pyqtgraph as pg
import dlib, time, cv2
import numpy as np
import playsound
from imutils import face_utils
import imutils
from scipy.spatial import distance

from PyQt5 import QtCore
from PyQt5.QtGui import QImage
from MensagemFalada import MensagemFalada
from AnalisePERCLOS import AnalisePERCLOS
from ArquivoCalibracao import ArquivoCalibracao

class ExecucaoPERCLOS(QThread):
    #Capitura de Imagem
    changePixmap = pyqtSignal(QPixmap)
    #Contador para calcular o FPS
    contadorLoop = pyqtSignal(str)
    
    #Alimentação de dados dos Gr�ficos
    plotarExecucao = pyqtSignal(pg.PlotItem)
    
    #Dados para a tela de log
    msgLog = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent=parent)
        self.threshold = 70
        
        self.arq_predicao = "shape_predictor_68_face_landmarks.dat"
        self.detector = dlib.get_frontal_face_detector()
        self.predicao = dlib.shape_predictor(self.arq_predicao)
        self.judite = MensagemFalada()
        self.analisePERCLOS = AnalisePERCLOS()
        arquivoCalibracao = ArquivoCalibracao()
        self.valorMaximo, self.valorMinimo, self.nome = arquivoCalibracao.abrirArquivoCalibracao()
        
        
    def __del__(self):
        self.wait()
        
    def run(self):
        #Habilitando a captura de v�deo
        cap = cv2.VideoCapture(0)
        self.hora = QTime()
        start_time = time.time()
        
        cont, fps, janelaBaixoPERCLOS = 0, 0, 0
        self.judite.scriptIniciarExecucao(self.nome)
        
        #Eixos do gráfico
        eixoX_graficoDeExecucao, eixoY_graficoDeExecucao, threshold_porcento = [], [], []

        while True:
            _, frame = cap.read()
            frameRedimencionado = imutils.resize(frame, width=357, height=273)
            rgbImage = cv2.cvtColor(frameRedimencionado, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frameRedimencionado, cv2.COLOR_BGR2GRAY)
            # detectar o rosto
            
            retangulos = self.detector(gray, 0)
            
            #Verificar se há reconhecimento de pelo menos um rosto
            if len(retangulos) > 0:
                self.shape = self.verificarMaiorRetangulo(gray, retangulos)
                
                #Pintar os landmark points do rosto
                for (x, y) in self.shape:
                    cv2.circle(rgbImage, (x, y), 4, (0, 0, 255), -1)
                
                threshold_porcento.append(self.threshold)
                
                eixoY_graficoDeExecucao.append((self.analisePERCLOS.razaoDeAspecto(self.shape) - self.valorMinimo) / (self.valorMaximo - self.valorMinimo) * 100)
                eixoX_graficoDeExecucao.append(len(eixoX_graficoDeExecucao)+1)
                
                grafico = self.plotarGraficoDeExecucao(eixoX_graficoDeExecucao, eixoY_graficoDeExecucao, threshold_porcento)
                
                self.plotarExecucao.emit(grafico.getPlotItem())
                
                # Verificar e Alertar
                if (eixoY_graficoDeExecucao[-1] < self.threshold):
                    print("PERCLOS: " + str(eixoY_graficoDeExecucao[-1]))
                    janelaBaixoPERCLOS += 1
                    if (janelaBaixoPERCLOS > 15):
                        
                        self.alerta("Beep\\beep.mp3")
                        
                        if (janelaBaixoPERCLOS > 15 and janelaBaixoPERCLOS % 25 == 0):
                            self.judite.scriptAlerta()
                            
                else:
                    janelaBaixoPERCLOS = 0
                    
            height, width, channel = rgbImage.shape
            bytesPerLine = 3 * width
            convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
            imagemDeExecucao = QPixmap.fromImage(convertToQtFormat)
                
            cont = cont + 1
                    
            if (cont > 9 ):
                tempo =  time.time() - start_time
                fps = int(cont/tempo)
                #reiniciar variáveis
                start_time = time.time()
                cont = 0
                        
            self.changePixmap.emit(imagemDeExecucao)
            self.contadorLoop.emit(str(fps))

    def verificarMaiorRetangulo(self, imagemGray, retangulos):
        maiorRetangulo = 0
        
        for retangulo in retangulos:
            shape = self.predicao(imagemGray, retangulo)
            shape = face_utils.shape_to_np(shape)
            
            #Calcular a distancia do rosto pertinente ao retangulo em an�lise
            distHorizontalRosto = distance.euclidean((shape[0] + shape[1]) // 2, (shape[16] + shape[17]) // 2) 
            distVerticalRosto = distance.euclidean((shape[19] + shape[24]) // 2, (shape[7] + shape[8] + shape[9]) // 3)
            
            if ((distHorizontalRosto * distVerticalRosto) > maiorRetangulo):
                maiorRetangulo = distHorizontalRosto * distVerticalRosto
                shapeMaior = shape
        return shapeMaior
    
    def plotarGraficoDeExecucao(self, xExecucao, yExcucao, yThreshold):
        grafico = pg.PlotWidget(title="GRÁFICO EM TEMPO REAL - PERCLOS")
        grafico.setLabels(left="PERCLOS", bottom="Frames")
        grafico.getPlotItem().showGrid(True, True, 0.2)
        grafico.setXRange(0, 1000, padding=0)
        grafico.setYRange(0, 100, padding=0)
                
        grafico.plot(xExecucao, yThreshold, pen=pg.mkPen('r', style=QtCore.Qt.DashLine))
        grafico.plot(xExecucao, yExcucao, pen=pg.mkPen('b'))
                    
        return grafico
    
    def alerta(self, path):
        # play an alarm sound
        playsound.playsound(path)