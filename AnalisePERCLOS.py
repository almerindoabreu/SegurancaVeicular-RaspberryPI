from scipy.spatial import distance
from pygame import mixer
import math
from MensagemFalada import MensagemFalada

class AnalisePERCLOS(object):
    
    #Calculando a Razão de Aspecto
    def razaoDeAspecto(self, shape):
        
        #RAD = RAZÃO DE ASPECTO DIREITA
        distVerticalDir = distance.euclidean((shape[43] + shape[44]) // 2, (shape[47] + shape[46]) // 2) 
        distHorizontalDir = distance.euclidean(shape[42], shape[45])
        rad = distVerticalDir / distHorizontalDir
        
        #RAE = RAZÃO DE ASPECTO ESQUERDA
        distVerticalEsq = distance.euclidean((shape[37] + shape[38]) // 2, (shape[41] + shape[40]) // 2) 
        distHorizontalEsq = distance.euclidean(shape[36], shape[39])
        rae = distVerticalEsq / distHorizontalEsq
       
        ra = (rad + rae) / 2
        return ra
    
    #Calcular desvio padrão
    def desvioPadrao(self, indiceFrameCalibragem, matrizRA):
        variancia, media = 0, 0
        count = 0
        
        #Calculo da média
        for i in range(indiceFrameCalibragem + 1):
            media += matrizRA[0][i]
            count += 1
        media = media / count
    
        #Calculo da variância
        for j in range(indiceFrameCalibragem + 1):
            variancia = variancia + math.pow((matrizRA[0][j] - media), 2)
        variancia = variancia / count
    
        #Raiz quadrada da variância
        devPadrao = math.sqrt(variancia)
        return devPadrao
    
    #Calcular erro padrão
    def erroPadrao(self, x, matrizRA):
        if x > 0:
            erroPad = matrizRA[1][x] / math.sqrt(x)
        else:
            erroPad = 0
        return erroPad
    
    #Calibragem dos valores adquiridos no processo de coleta de dados
    def calibragemAberturaOlhos(self, matrizRA):
        aberturaMin = matrizRA[0].min()
        aberturaMax = matrizRA[0].max()
        for x in range(len(matrizRA[0])):
            if (((matrizRA[0][x] - aberturaMin) * 100) / (aberturaMax - aberturaMin) >= 95):
                matrizRA[0][x] = matrizRA[0][x] - matrizRA[2][x]
                
            if (((matrizRA[0][x] - aberturaMin) * 100) / (aberturaMax - aberturaMin) <= 5):
                matrizRA[0][x] = matrizRA[0][x] + matrizRA[2][x]

        return matrizRA
        
    #Coversor de todos os valores da matriz RA para porcentagem
    def converterTudoEmPorcentagem(self, matrizRA):
        matrizAnalitica = []
        aberturaMin = matrizRA[0].min()
        aberturaMax = matrizRA[0].max()
        for i in range(len(matrizRA[0])):
            #Calcular a porcentagem
            porcentagem = (matrizRA[0][i] - aberturaMin) / (aberturaMax - aberturaMin) * 100
            matrizAnalitica.append(porcentagem)
        return matrizAnalitica
    
    def verificarJanelaPERCLOS(self, janelaBaixoPERCLOS, dadoPERCLOS, nome):
        #Verificar e Alertar
        if (dadoPERCLOS[-1] < self.threshold):
            print("PERCLOS: " + str(dadoPERCLOS[-1]))
            janelaBaixoPERCLOS += 1
            if (janelaBaixoPERCLOS > 5):
                mixer.music.load("Beep\\beep.mp3")
                mixer.music.play()
                if (janelaBaixoPERCLOS > 10):
                    judite = MensagemFalada()
                    judite.scriptAlerta(nome)
        else:
            janelaBaixoPERCLOS = 0
            
        return janelaBaixoPERCLOS