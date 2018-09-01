# -*- coding: utf-8 -*-
'''
Created on 16 de jun de 2018

@author: almer
'''
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QWidget, QTime, QInputDialog
from gtts import gTTS
import numpy as np
import pyqtgraph as pg
from DesempenhoProcessador import DesempenhoProcessador
from Horario import Horario
from ExecucaoPERCLOS import ExecucaoPERCLOS
from CalibrarPERCLOS import CalibrarPERCLOS

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
        self.verticalLayoutWidgetCamera.setTitle("Câmera")
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
        
        self.graficoMicro = pg.PlotWidget(self.horizontalLayoutWidget, title="GRÁFICO EM REAL TIME - PERCLOS ANÁLISE")
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
        
        self.graficoMacro = pg.PlotWidget(self.horizontalLayoutWidget, title="GRÁFICO AQUISIÇÃO DE DADOS INICIAL PARA CALIBRAGEM")
        self.graficoMacro.setLabels(left="PERCLOS", bottom="Frames")    
        self.graficoMacro.setXRange(0, 20, padding=0)
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
        
        ##----------FPS----------##
        self.lbFPS = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        #self.lbFPS.setObjectName("lbFPS")
        self.lbFPS.setText("FPS")
              
        self.lcdFPS = QtWidgets.QLCDNumber(self.horizontalLayoutWidget_3)
        self.lcdFPS.setObjectName("lcdFPS")
        
        ##----------Marcador de Tempo----------##
        self.lbTempo = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
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
       
        ##---------- Botões de Execução ----------##
        self.btCalibrar = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.btCalibrar.setObjectName("btCalibrar")
        self.btCalibrar.setText("Calibrar")
        self.btExecutar = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.btExecutar.setObjectName("btExecutar")
        self.btExecutar.setText("Executar")

        #Layout da parte superior
        self.layoutParteSuperior.addWidget(self.lbFPS)
        self.layoutParteSuperior.addWidget(self.lcdFPS)
        self.layoutParteSuperior.addWidget(self.lbTempo)
        self.layoutParteSuperior.addWidget(self.timeEdit)
        self.layoutParteSuperior.addWidget(self.lbProcessoCPU)
        self.layoutParteSuperior.addWidget(self.txtProcessoCPU)
        self.layoutParteSuperior.addWidget(self.btCalibrar)
        self.layoutParteSuperior.addWidget(self.btExecutar)
        
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
        
        #---------- Layout de Análise Piscadas ----------
        self.layoutPiscada = QtWidgets.QGroupBox(self.centralwidget)
        self.layoutPiscada.setGeometry(QtCore.QRect(10, 55, 351, 120))
        #self.layoutPiscada.setFrameShape(QtWidgets.QFrame.StyledPanel)
        #self.layoutPiscada.setFrameShadow(QtWidgets.QFrame.Raised)
        self.layoutPiscada.setObjectName("layoutPiscada")
        self.layoutPiscada.setTitle("Análise Piscadas")
        
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
                
        #---------- Layout de Análise Bocejo ----------
        self.layoutBocejo = QtWidgets.QGroupBox(self.centralwidget)
        self.layoutBocejo.setGeometry(QtCore.QRect(10, 179, 351, 120))
        self.layoutBocejo.setObjectName("layoutBocejo")
        self.layoutBocejo.setTitle("Análise Bocejo")
        
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
        
        #---------- Layout de Análise Estatisticas do PERCLOS ----------
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
        
        thCPU = DesempenhoProcessador(self)
        thCPU.desempenhoCPU.connect(self.txtProcessoCPU.setText)
        thCPU.start()
        
        thHora = Horario(self)
        thHora.horarioEmTempoReal.connect(self.timeEdit.setText)
        thHora.startTelaDeLog.connect(self.txtLog.setPlainText)
        thHora.start()
        
        self.btCalibrar.clicked.connect(self.executarCalibracao)
        self.btExecutar.clicked.connect(self.executarExecucao)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def executarCalibracao(self):
        boasVindas = BoasVindas()
        self.usuario = boasVindas.getNome()
        
        self.calibracao = CalibrarPERCLOS(self, self.usuario)
        self.calibracao.changePixmap.connect(self.label.setPixmap)
        self.calibracao.contadorLoop.connect(self.lcdFPS.display)
        self.calibracao.plotarCalibragem.connect(self.graficoMacro.setCentralWidget)
        self.calibracao.valorMaxPERCLOS.connect(self.txtValorMaxPERCLOS.setText)
        self.calibracao.valorMinPERCLOS.connect(self.txtValorMinPERCLOS.setText)
        self.calibracao.PThreshold.connect(self.txtP80.setText)
        self.calibracao.msgLog.connect(self.txtLog.appendPlainText)
        
        self.calibracao.start()
        
    def executarExecucao(self):
        self.execucao = ExecucaoPERCLOS(self)
        self.execucao.changePixmap.connect(self.label.setPixmap)
        self.execucao.contadorLoop.connect(self.lcdFPS.display)
        self.execucao.plotarExecucao.connect(self.graficoMicro.setCentralWidget)
        self.execucao.msgLog.connect(self.txtLog.appendPlainText)

        self.execucao.start()
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Segurança Veicular TCC"))
 
        self.lbValorMaxPERCLOS.setText(u"Valor Máx.")
        self.lbValorMinPERCLOS.setText("Valor Mín.")
        self.lbP80.setText("P80")
        self.lbMinutosAntesPiscada.setText("min. antes")
        self.lbMaximaPiscada.setText("Máxima")
        self.lbMinimaPiscada.setText("Mínima")
        self.lbReferenciaTempoPiscadaMax.setText("Ref. Tempo")
        self.lbPiscada.setText("Piscada")
        self.lbPorMinutoPiscada.setText("por min.")
        self.lbReferenciaTempoPiscadaMin.setText("Ref. Tempo")
        self.lbMediana.setText("Mediana")
        self.lbMinAntesBocejo.setText("min. antes")
        self.lbMaximaBocejo.setText("Máxima")
        self.lbMinimaBocejo.setText("Mínima")
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
        
class BoasVindas(QWidget):
    def __init__(self):
        super(BoasVindas, self).__init__()
        self.horario = QTime()
        
    def getNome(self):
        msg, ok = QInputDialog.getText(self, 'Bem Vindo!', 'Olá, qual é seu nome?')
        
        if ok:
            script = ("Meu nome é Judite, e eu irei lhe auxiliar em sua viagem analisando seu estado físico e mental" +
                      "para evitar qualquer desatenção durante o percurso...")
            if (self.horario.currentTime() > QTime(5, 59) and self.horario.currentTime() < QTime(12, 0)):
                tts = gTTS(text='Olá, bom dia ' + msg +"." + script, lang='pt')
                tts.save("Mensagens Faladas\\boas-vindas.mp3")
                return msg
            elif (self.horario.currentTime() > QTime(11, 59) and self.horario.currentTime() < QTime(18, 0)):
                tts = gTTS(text='Olá, boa tarde ' + msg + "." + script, lang='pt')
                tts.save("Mensagens Faladas\\boas-vindas.mp3")
                return msg
            else:
                tts = gTTS(text='Olá, boa noite ' + msg + "." + script, lang='pt')
                tts.save("Mensagens Faladas\\boas-vindas.mp3")
                return msg
