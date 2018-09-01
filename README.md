## DISPOSITIVO DE SEGURANÇA VEICULAR COM LEITURA DE EXPRESSÃO FACIAL PARA PREVENÇÃO DE ACIDENTES POR SONO AO VOLANTE

Esse protótipo de segurança veicular foi um trabalho de conclusão de curso que foi engrenado em pesquisa acadêmica pela Faculdade Salesiana Maria Auxiliadora. Tendo como participantes: Almerindo Abreu, Raphael Marques e como Orientador, o DSc Irineu Neto.

[Pesquisa Acadêmica - Faculdade Salesiana Maria Auxiliadora](http://www.fsma.edu.br/site/projetos/prototipacao-de-um-sistema-de-seguranca-veicular-para-alertas-contra-o-sono-e-cansaco-via-reconhecimento-de-imagens/)


### Objetivo do Projeto

O referido projeto visa elaborar um protótipo computacional capaz de gerar alertas contra o sono e cansaço ao volante, baseado em análise de imagens e técnicas de análise de dados. O sono é definido como um estado funcional, com comportamentos corporais característicos que afetam a mobilidade, caracterizado por baixo reflexo, muitas vezes associado ao cansaço e stress. Então, há reações singulares de expressões faciais ditas universais e determinantes para expressar o sono, o cansaço e o stress, que podem ser aplicadas em sistemas para a prevenção de acidentes automobilísticos.

### Regras de Desenvolvimento do Protótipo

Para o referente código, foi utilizado linguagem Python no dispositivo Raspberry PI 3 Model B+ com módulo de câmera de aquisição com infravermelho.

![Dagrama de Blocos do Protótipo com o Kinect Sensor](http://oi63.tinypic.com/2u455w5.jpg)

O projeto é similar ao [Dispositivo de Segurança Veicular](https://github.com/almerindoabreu/SegurancaVeicular), que foi criado para utilização em computador com webcam, porém este, além das bibliotecas do código utilizado para o computador tradicional, tem a biblioteca PiCamera que é utilizado para controlar o módulo de câmera utilizado.

Instalação da biblioteca PiCamera no distro [Raspbian](http://www.raspbian.org/)  pode ser realizado com os comandos abaixo (para melhor auxilio na biblioteca, pode ser consultado a [documentação](https://picamera.readthedocs.io/en/release-1.12/install.html)):

    $ sudo apt-get update
    $ sudo apt-get install python-picamera python3-picamera


A utilização e o desenvolvimento de testes do Raspberry PI 3 foi realizado em máquina virtual diretamente de um notebook, estando etão a virtualização via VNC (Virtual Network Computing) pelo software [VNC Viwer].(https://www.realvnc.com/pt/connect/download/viewer/)

Para melhor entendimento, e acompanhar o procedimento para realizar essa virtualização, pode ser seguido o seguinte [**vídeo (Como Usar sem Monitor - RaspberryPi Primeiros Passos - Vídeo #5)**](https://www.youtube.com/watch?v=LTTwwPtYQms&t=371s).

Outras bibliotecas utilizadas.

|Biblioteca   |Instalação                            |Site / Documentação|
|----------------|-------------------------------|-----------------------------|
|PyQt 5.9|pip install pyqt5          |[Link](http://pyqt.sourceforge.net/Docs/PyQt5/)            |
|PyQTGraph 0.10.0          |pip install pyqtgraph            |[Link](http://www.pyqtgraph.org/)            |
|gTTS 1.2.2|pip install gtts|[Link](http://pyqt.sourceforge.net/Docs/PyQt5/)|
| PyGame 1.9.3 | pip install pygame | [Link](https://www.pygame.org/docs/)|
| DLIB 19.8.1 | pip install dlib | [Link](http://dlib.net/)|
| OpenCV 2.4.9 | pip install opencv2 | [Link](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html)|
| Imutils 0.4.5 | pip install imutils | [Link](https://github.com/jrosebr1/imutils)|
| psutil 5.4.0 | pip install psutil | [Link](https://psutil.readthedocs.io/en/latest/)|
| NumPy | pip install numpy | [Link](http://www.numpy.org/)|
