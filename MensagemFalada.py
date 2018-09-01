'''
Created on 16 de jun de 2018

@author: almer
'''
from pygame import mixer
import time
from gtts import gTTS

class MensagemFalada(object):
    '''
    classdocs
    '''
    def __init__(self):
        mixer.init(24100)
        
    def scriptInicial(self):
        mixer.music.load("Mensagens Faladas\\boas-vindas.mp3")
        mixer.music.play()
        time.sleep(16)
        mixer.music.load("Mensagens Faladas\\auxilio-calibracao.mp3")
        mixer.music.play()
        time.sleep(4)
        mixer.music.load("Mensagens Faladas\\auxilio-calibracao-olhos-fechados.mp3")
        mixer.music.play()
        time.sleep(8)
    
    def scriptContagem(self):
        mixer.music.load("Mensagens Faladas\\contar-um.mp3")
        mixer.music.play()
        time.sleep(1)
        mixer.music.load("Mensagens Faladas\\contar-dois.mp3")
        mixer.music.play()
        time.sleep(1)
        mixer.music.load("Mensagens Faladas\\contar-tres.mp3")
        mixer.music.play()
        time.sleep(1)
        
    def scriptRegulagemOlhosAbertos(self):
        mixer.music.load("Mensagens Faladas\\ok-auxilio-calibracao-olhos-abertos.mp3")
        mixer.music.play()
        time.sleep(10)
    
    def scriptFimCalibragem(self):
        tts = gTTS(text='Pronto, calibração finalizada.', lang='pt')
        tts.save("Mensagens Faladas\\ok.mp3")
        mixer.music.load("Mensagens Faladas\\ok.mp3")
        mixer.music.play()
        
    def scriptIniciarExecucao(self, nome=""):
        tts = gTTS(text='Olá, ' + nome + '. Vamos iniciar a nossa viagem? Qualquer alerta eu irei te falar.', lang='pt')
        tts.save("Mensagens Faladas\\iniciar viagem.mp3")
        mixer.music.load("Mensagens Faladas\\iniciar viagem.mp3")
        mixer.music.play()
        tts = gTTS(text='' + nome + '. Acho melhor realizarmos uma pausa para descanço.', lang='pt')
        tts.save("Mensagens Faladas\\alerta.mp3")
    
    def scriptAlerta(self):
        mixer.music.load("Mensagens Faladas\\alerta.mp3")
        mixer.music.play()
        time.sleep(6)
