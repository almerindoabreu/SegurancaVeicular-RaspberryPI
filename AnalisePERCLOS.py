from PyQt5.Qt import *
import dlib, time, cv2
import pyqtgraph as pg
import numpy as np
from imutils import face_utils
from scipy.spatial import distance
import math

class AnalisePERCLOS(QThread):
    changePixmap = pyqtSignal(QPixmap)
    contadorLoop = pyqtSignal([str])
    #calibracao = pyqtSignal(list)
    plotar = pyqtSignal(pg.PlotItem)

    def __init__(self, parent=None):
        QThread.__init__(self, parent=parent)
        
        self.arq_predicao = "shape_predictor_68_face_landmarks.dat"
        self.detector = dlib.get_frontal_face_detector()
        self.predicao = dlib.shape_predictor(self.arq_predicao)
        
    def run(self):
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        cont = 0
        fps = 0
        contImgCalibracao = 0
        self.matrizRA = np.zeros((3, 2))
        b = True
        while b:
            ret, frame = cap.read()
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            rects = self.detector(gray, 1)
            
            for rect in rects:
                self.shape = self.predicao(gray, rect)
               
                # Transforma os valores predicados do rosto para um array NumPy
                self.shape = face_utils.shape_to_np(self.shape)
                for (x, y) in self.shape:
                    cv2.circle(rgbImage, (x, y), 4, (0, 0, 255), -1)
                    
                if (contImgCalibracao < 2):
                    #self.(self.shape)
                    
                    self.matrizRA[0][contImgCalibracao] = self.razaoDeAspecto(self.shape)
                    self.matrizRA[1][contImgCalibracao] = self.desvioPadrao(contImgCalibracao)
                    self.matrizRA[2][contImgCalibracao] = self.erroPadrao(contImgCalibracao)
                    
                    contImgCalibracao +=1
                    print("Estou coletando dados... " + str(contImgCalibracao))
                elif (contImgCalibracao == 2):
                    self.calibragemAberturaOlhos()
                    self.matrizAnalitica = self.converterParaPorcentagem()
                    contImgCalibracao +=1
                    print("Estou calibrando os dados...")
                else:
                    #b = False
                    oi = 1
                    #print("Estou executando os dados..." )
                    #self.calibracao.emit(self.matrizAnalitica)
            
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
            p = convertToQtFormat.scaled(340, 260, Qt.KeepAspectRatio)
            cont = cont + 1
            contImgCalibracao = contImgCalibracao+1
            if (contImgCalibracao > 50 ):
                self.RA = self.matrizAnalitica
                
                grafico = pg.PlotWidget(title="GRAFICO EM TEMPO REAL - PERCLOS")
                grafico.setLabels(left="PERCLOS", bottom="Frames")
                x = np.arange(2)
                x2 = np.arange(100)
                y2 = (x2*8)/x2
                
                grafico.setXRange(0, 100, padding=0.05)
                grafico.setYRange(0, 10, padding=0.05)
                
                #linhaPERCLOS = grafico.pl
                grafico.plot(x2, y2, pen=pg.mkPen('r', style=Qt.DashLine))
        
                for i in range(1):
                    print("Estou dentro do contImg > 2")
                    print(self.matrizAnalitica)
                    print(self.matrizAnalitica[1])
                    grafico.plot(x, self.RA[i], pen=pg.mkPen('b'))
                    
                #return self.grafico.getPlotItem()
                self.plotar.emit(grafico.getPlotItem())
                time.sleep(3)
                
                if (int(time.time() - start_time) == 1 ):
                    print("Estou dentro do Time...")
                    fps = cont
                    cont = 0
                    start_time = time.time()
                    
                self.changePixmap.emit(p)
                self.contadorLoop.emit(str(fps))
            
    #Calculando a RazAo de Aspecto
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
        print(ra)
        return ra
    
    #Calcular desvio padrAo
    def desvioPadrao(self, x):
        variancia, media = 0, 0
        count = 0
        
        #Calculo da mEdia
        for i in range(x + 1):
            media += self.matrizRA[0][i]
            count += 1
        media = media / count
    
        #Calculo da variAncia
        for j in range(x + 1):
            variancia = variancia + math.pow((self.matrizRA[0][j] - media), 2)
        variancia = variancia / count
    
        #Raiz quadrada da variAncia
        devPadrao = math.sqrt(variancia)
        return devPadrao
    
    #Calcular erro padrAo
    def erroPadrao(self, x):
        if x > 0:
            erroPad = self.matrizRA[1][x] / math.sqrt(x)
        else:
            erroPad = 0
        return erroPad
    
    def calibragemAberturaOlhos(self):
        valorMaxOlho, valorMinOlho, flagValorMax, flagValorMin = 0, 0, 0, 0
        for x in range(2):
            if valorMaxOlho < self.matrizRA[0][x]:
                valorMaxOlho = self.matrizRA[0][x]
                flagValorMax = x
    
            if (valorMinOlho > self.matrizRA[0][x]) or (valorMinOlho == 0):
                valorMinOlho = self.matrizRA[0][x]
                flagValorMin = x
    
        self.matrizRA[0][flagValorMax] = self.matrizRA[0][flagValorMax] - self.matrizRA[2][flagValorMax]
        self.matrizRA[0][flagValorMin] = self.matrizRA[0][flagValorMin] + self.matrizRA[2][flagValorMin]
        
    def converterParaPorcentagem(self):
        matrizAnalitica = []
        print(self.matrizRA)
        aberturaMin = self.matrizRA[0].min()
        aberturaMax = self.matrizRA[0].max()
        print(len(self.matrizRA[0]))
        for i in range(len(self.matrizRA[0])):
            #Calcular a porcentagem
            porcentagem = (self.matrizRA[0][i] - aberturaMin) / (aberturaMax - aberturaMin) * 100
            print(porcentagem)
            matrizAnalitica.append(porcentagem)
        print(matrizAnalitica)
        return matrizAnalitica