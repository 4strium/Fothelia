import sys, bluetooth, socket, time, threading, librosa, scipy
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QSlider, QSpinBox, QPushButton, QCheckBox, QFileDialog
from PyQt6.QtGui import QImage, QPixmap, QColor, qRgb, QFont, QPainter, QPen
from PyQt6.QtCore import Qt
import numpy as np
import sounddevice as sd

class MainWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.initializeUI()

  def initializeUI(self):
    self.setFixedSize(1200, 800)
    self.setWindowTitle("LEDstrip Control")

    self.hue = 0
    self.current_val = QColor()
    self.stockage_color = QColor(qRgb(0,0,0))
    self.cold_value = 0
    self.stockage_cold = 0
    self.warm_value = 0
    self.stockage_warm = 0
    self.connexion = False
    self.basicMode = True

    self.waveColor = False

    self.setUpMainWindow()
    self.show()

  def setUpMainWindow(self):
    cb_styles = """
      QCheckBox::indicator { 
      width: 15px; 
      height: 15px; 
      border: 1px solid black;
      border-radius : 5px;
      }
      QCheckBox::indicator:checked { 
      background-color: #2196F3;
      }                   
    """

    instruction0 = QLabel("Connect to your LED strip :", self)
    instruction0.setFont(QFont("Arial",15))
    instruction0.move(200,40)

    self.connexion_button = QPushButton("Connection",self)
    self.connexion_button.setFont(QFont("Arial",15))
    self.connexion_button.resize(150,50)
    self.connexion_button.move(480,24)
    self.connexion_button.clicked.connect(self.Bluetooth_connect)
    self.connexion_button.setCursor(Qt.CursorShape.PointingHandCursor)

    self.bluetooth_message = QLabel("No device connected", self)
    self.bluetooth_message.setFont(QFont("Arial",10))
    self.bluetooth_message.move(650,40)

    styleModes = """
      QPushButton {
        background-color: transparent;
        border: none;
        color: black;
      }
      QPushButton:hover {
        background-color: transparent;
      }
      QPushButton:pressed {
        background-color: transparent;
      }
    """

    self.basic_mode_button = QPushButton("Basic Mode",self)
    self.basic_mode_button.setFont(QFont("Arial",15))
    self.basic_mode_button.resize(150,50)
    self.basic_mode_button.move(400,120)
    self.basic_mode_button.setStyleSheet(styleModes)
    self.basic_mode_button.clicked.connect(self.switchBasic)
    self.basic_mode_button.setCursor(Qt.CursorShape.PointingHandCursor)

    self.disco_mode_button = QPushButton("Disco Mode",self)
    self.disco_mode_button.setFont(QFont("Arial",15))
    self.disco_mode_button.resize(150,50)
    self.disco_mode_button.move(620,120)
    self.disco_mode_button.setStyleSheet(styleModes)
    self.disco_mode_button.clicked.connect(self.switchDisco)
    self.disco_mode_button.setCursor(Qt.CursorShape.PointingHandCursor)

    self.ModeButtons = [self.basic_mode_button,self.disco_mode_button]
    MainWindow.hideWidgets(self.ModeButtons)

    self.rgb_cb = self.create_checkbox("RGB Mode",100,200,cb_styles)
    self.cool_white_cb = self.create_checkbox("Cool White Mode",480,200,cb_styles)
    self.warm_white_cb = self.create_checkbox("Warm White Mode",900,200,cb_styles)

    self.checkboxes = [self.rgb_cb, self.cool_white_cb, self.warm_white_cb]

    MainWindow.hideWidgets(self.checkboxes)

    self.color_display = QImage(100, 100, QImage.Format.Format_RGBX64)
    self.color_display.fill(Qt.GlobalColor.black)

    self.cd_label = QLabel(self)
    self.cd_label.setPixmap(QPixmap.fromImage(self.color_display))
    self.cd_label.setScaledContents(True)
    self.cd_label.move(10,250)
    self.cd_label.resize(330,140)

    self.red_label, self.red_slider, self.red_spinbox = self.create_slidespin_control("Red",10,430)
    self.green_label, self.green_slider, self.green_spinbox = self.create_slidespin_control("Green",10,530)
    self.blue_label, self.blue_slider, self.blue_spinbox = self.create_slidespin_control("Blue",10,630)

    self.red_slider.valueChanged.connect(self.updateRedSpinBox)
    self.red_spinbox.valueChanged.connect(self.updateRedSlider)

    self.green_slider.valueChanged.connect(self.updateGreenSpinBox)
    self.green_spinbox.valueChanged.connect(self.updateGreenSlider)

    self.blue_slider.valueChanged.connect(self.updateBlueSpinBox)
    self.blue_spinbox.valueChanged.connect(self.updateBlueSlider)

    self.cold_label, self.cold_slider, self.cold_spinbox = self.create_slidespin_control("Cold White",410,430)
    self.warm_label, self.warm_slider, self.warm_spinbox = self.create_slidespin_control("Warm White",830,430)

    self.cold_slider.valueChanged.connect(self.updateColdSpinBox)
    self.cold_spinbox.valueChanged.connect(self.updateColdSlider)
    self.warm_slider.valueChanged.connect(self.updateWarmSpinBox)
    self.warm_spinbox.valueChanged.connect(self.updateWarmSlider)
    
    self.color_controls = [
      self.red_label, self.red_slider, self.red_spinbox,
      self.green_label, self.green_slider, self.green_spinbox,
      self.blue_label, self.blue_slider, self.blue_spinbox,
      self.cd_label
    ]

    self.cold_controls = [
      self.cold_label, self.cold_slider, self.cold_spinbox
    ]

    self.warm_controls = [
      self.warm_label, self.warm_slider, self.warm_spinbox
    ]
    
    self.basic_widgets = [self.color_controls,self.cold_controls,self.warm_controls, self.checkboxes]

    MainWindow.hideWidgets(self.color_controls)
    MainWindow.hideWidgets(self.cold_controls)
    MainWindow.hideWidgets(self.warm_controls)

    self.wavecolor_button = QPushButton("Wave Color",self)
    self.wavecolor_button.setFont(QFont("Arial",15))
    self.wavecolor_button.resize(150,50)
    self.wavecolor_button.move(520,280)
    self.wavecolor_button.clicked.connect(self.activWaveColor)
    self.wavecolor_button.setCursor(Qt.CursorShape.PointingHandCursor)

    self.musicsync_button = QPushButton("Music SYNC",self)
    self.musicsync_button.setFont(QFont("Arial",15))
    self.musicsync_button.resize(150,50)
    self.musicsync_button.move(520,380)
    self.musicsync_button.clicked.connect(self.playMusicSync)
    self.musicsync_button.setCursor(Qt.CursorShape.PointingHandCursor)

    self.play_message = QLabel(self)
    self.play_message.setFont(QFont("Arial",10))
    self.play_message.move(550,450)

    self.disco_widgets = [self.wavecolor_button, self.musicsync_button, self.play_message]
    MainWindow.hideWidgets(self.disco_widgets)

  def create_slidespin_control(self,name,x,y):
    label = QLabel(name,self)
    label.setFont(QFont("Helvetica", 14))
    label_width = label.sizeHint().width()
    label.move(x + (255 - label_width)//2, y-30)  # Centrer par rapport à la longueur du slider

    slider = QSlider(Qt.Orientation.Horizontal, self)
    slider.setObjectName(name)
    slider.setMaximum(255)
    slider.resize(255,20)
    slider.move(x,y)
    slider.setCursor(Qt.CursorShape.OpenHandCursor)
    slider.sliderPressed.connect(lambda: slider.setCursor(Qt.CursorShape.ClosedHandCursor))
    slider.sliderReleased.connect(lambda: slider.setCursor(Qt.CursorShape.OpenHandCursor))

    spinbox = QSpinBox(self)
    spinbox.setMaximum(255)
    spinbox.move(x+260,y-5)
    spinbox.setCursor(Qt.CursorShape.PointingHandCursor)

    return label,slider,spinbox
  
  def create_checkbox(self,name,x,y,stylesheet):
    checkbox = QCheckBox(name, self)
    checkbox.setFont(QFont("Arial",15))
    checkbox.move(x,y)
    checkbox.setStyleSheet(stylesheet)
    checkbox.toggled.connect(self.activateMode)
    checkbox.setCursor(Qt.CursorShape.PointingHandCursor)

    return checkbox

  def hideWidgets(lst):
    for widget in lst :
      widget.hide()
  def showWidgets(lst):
    for widget in lst :
      widget.show()

  def switchBasic(self):
    self.updateColorInfo(qRgb(0, 0, 0))
    self.waveColor = False
    MainWindow.hideWidgets(self.disco_widgets)
    MainWindow.showWidgets(self.checkboxes)
    self.basicMode = True
    self.update()

  def switchDisco(self):
    for widget_list in self.basic_widgets :
      MainWindow.hideWidgets(widget_list)
      for checkbox in self.checkboxes:
        checkbox.setChecked(False)
    self.basicMode = False
    self.waveColor = False
    MainWindow.showWidgets(self.disco_widgets)
    self.update()

  def activateMode(self,checked):
    sender = self.sender()
    if checked and sender.text()=="RGB Mode" :
      MainWindow.showWidgets(self.color_controls)
      self.updateColorInfo(self.stockage_color)
      self.cool_white_cb.setChecked(False)
      self.warm_white_cb.setChecked(False)
    elif sender.text()=="RGB Mode" :
      MainWindow.hideWidgets(self.color_controls)
      self.stockage_color = self.current_val
      self.updateColorInfo(qRgb(0, 0, 0))
    elif checked and sender.text()=="Cool White Mode":
      MainWindow.showWidgets(self.cold_controls)
      self.cold_value = self.stockage_cold
      self.rgb_cb.setChecked(False)
      self.warm_white_cb.setChecked(False)
    elif sender.text()=="Cool White Mode":
      MainWindow.hideWidgets(self.cold_controls)
      self.stockage_cold = self.cold_value
      self.cold_value = 0
    elif checked and sender.text()=="Warm White Mode":
      MainWindow.showWidgets(self.warm_controls)
      self.warm_value = self.stockage_warm
      self.rgb_cb.setChecked(False)
      self.cool_white_cb.setChecked(False)
    elif sender.text()=="Warm White Mode":
      MainWindow.hideWidgets(self.warm_controls)
      self.stockage_warm = self.warm_value
      self.warm_value = 0

  def updateRedSpinBox(self, value):
    self.red_spinbox.setValue(value)
    self.redValue(value)
      
  def updateRedSlider(self, value):
    self.red_slider.setValue(value)
    self.redValue(value)

  def updateGreenSpinBox(self, value):
    self.green_spinbox.setValue(value)
    self.greenValue(value)
      
  def updateGreenSlider(self, value):
    self.green_slider.setValue(value)
    self.greenValue(value)

  def updateBlueSpinBox(self, value):
    self.blue_spinbox.setValue(value)
    self.blueValue(value)
      
  def updateBlueSlider(self, value):
    self.blue_slider.setValue(value)
    self.blueValue(value)

  def updateColdSpinBox(self, value):
    self.cold_spinbox.setValue(value)
    self.cold_value = value
      
  def updateColdSlider(self, value):
    self.cold_slider.setValue(value)
    self.cold_value = value

  def updateWarmSpinBox(self, value):
    self.warm_spinbox.setValue(value)
    self.warm_value = value
      
  def updateWarmSlider(self, value):
    self.warm_slider.setValue(value)
    self.warm_value = value

  def redValue(self, value):
    new_color = qRgb(value, self.current_val.green(), self.current_val.blue())
    self.updateColorInfo(new_color)

  def greenValue(self, value):
    new_color = qRgb(self.current_val.red(), value, self.current_val.blue())
    self.updateColorInfo(new_color)

  def blueValue(self, value):
    new_color = qRgb(self.current_val.red(), self.current_val.green(), value)
    self.updateColorInfo(new_color)

  def updateColorInfo(self, color):
    """Update color displayed in image"""
    self.current_val = QColor(color)
    
    if self.basicMode :
      self.color_display.fill(color)
      self.cd_label.setPixmap(QPixmap.fromImage(self.color_display))

  def activWaveColor(self):
    self.waveColor = True

  def playMusicSync(self):
    self.waveColor = False
    fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a file",
            "",
            "*.mp3"
        )
    if fichier:
      self.play_message.setText(f"Audio playing...")
      self.play_message.setStyleSheet("color: green;")
    else:
      self.play_message.setText("File not usable")
      self.play_message.setStyleSheet("color: red;")
    self.play_message.adjustSize()
    self.play_message.show()
    QApplication.processEvents()

    if fichier :
      # Charger l'audio
      y, sr = librosa.load(fichier, sr=None)

      # Appliquer un filtre passe-bas pour garder les basses (< 150 Hz)
      cutoff = 150
      b, a = scipy.signal.butter(6, cutoff, btype='low', fs=sr)
      y_bass = scipy.signal.filtfilt(b, a, y)

      # Définir un hop_length correspondant à 100ms
      hop_duration = 0.1
      hop_length = int(hop_duration * sr)

      # Fenêtre de STFT (plus grande que hop_length pour meilleure résolution fréquentielle)
      frame_length = 2048

      # Calcul de l'enveloppe d'amplitude pour les basses
      amplitude_env = np.abs(librosa.stft(y_bass, n_fft=frame_length, hop_length=hop_length))
      bass_energy = np.mean(amplitude_env, axis=0)

      times = librosa.frames_to_time(np.arange(len(bass_energy)), sr=sr, hop_length=hop_length).tolist()

      # STFT sur le signal complet pour la fréquence dominante
      S = np.abs(librosa.stft(y, n_fft=frame_length, hop_length=hop_length))
      frequencies = librosa.fft_frequencies(sr=sr, n_fft=frame_length)
      dominant_freqs = frequencies[np.argmax(S, axis=0)].tolist()

      def play_audio():
        sd.play(y, sr)
        sd.wait()

      audio_thread = threading.Thread(target=play_audio)
      audio_thread.start()

      for index in range(len(times)):
        self.warm_value = 0
        if bass_energy[index]>0.8 :
          self.updateColorInfo(qRgb(0,0,0))
          self.cold_value = 255
        else :
          self.cold_value = 0
          freq = dominant_freqs[index]
          if 20 <= freq <= 250 :
            # Interpolation linéaire entre rouge (20 Hz) et jaune (250 Hz)
            ratio = (freq - 20) / (250 - 20)
            r = int(255)
            g = int(255 * ratio)
            b = 0
            self.updateColorInfo(qRgb(r, g, b))
          elif 250 < freq <= 4000 :
            # Interpolation linéaire entre vert (250 Hz) et cyan (4000 Hz)
            ratio = (freq - 250) / (4000 - 250)
            r = 0
            g = int(255)
            b = int(255 * ratio)
            self.updateColorInfo(qRgb(r, g, b))
          elif 4000 < freq <= 20000 :
            # Interpolation linéaire entre bleu (4000 Hz) et blanc (20000 Hz)
            ratio = (freq - 4000) / (20000 - 4000)
            r = int(255 * ratio)
            g = int(255 * ratio)
            b = 255
            self.updateColorInfo(qRgb(r, g, b))
        time.sleep(0.1)

      self.play_message.setText("")

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
  
    if self.basicMode and self.connexion:
      pen1 = QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine)
      painter.setPen(pen1)
      painter.drawLine(350, 250, 350, 750)
      painter.drawLine(800, 250, 800, 750)
      pen2 = QPen(QColor("#2196F3"), 4, Qt.PenStyle.SolidLine)
      painter.setPen(pen2)
      painter.drawLine(430, 165, 520, 165)
    elif not self.basicMode and self.connexion:
      pen2 = QPen(QColor("#2196F3"), 4, Qt.PenStyle.SolidLine)
      painter.setPen(pen2)
      painter.drawLine(650, 165, 740, 165)
    self.update()
  

  def updateBluemessage(self,text,color):
    self.bluetooth_message.setText(text)
    self.bluetooth_message.setStyleSheet(f"color: {color};")
    self.bluetooth_message.adjustSize()
    self.bluetooth_message.show()
    QApplication.processEvents()

  def loopData(self):
    while True :
      if self.waveColor:
        self.hue = (self.hue + 5) % 360  # Vitesse du cycle

        # Teinte varie, saturation et valeur restent à 255
        color = QColor.fromHsv(self.hue, 255, 255)

        self.updateColorInfo(qRgb(color.red(), color.green(), color.blue()))

      frame = {}
      frame['R'] = f"{self.current_val.red():03d}"
      frame['G'] = f"{self.current_val.green():03d}"
      frame['B'] = f"{self.current_val.blue():03d}"
      frame['C'] = f"{self.cold_value:03d}"
      frame['W'] = f"{self.warm_value:03d}"

      try :
        self.socket_b.send(bytes("S"+str(frame), 'UTF-16'))
      except ConnectionAbortedError :
        self.updateBluemessage("Device disconnected", 'red')
        self.connexion = False
      time.sleep(0.1)

  def activateManipulation(self):
    MainWindow.showWidgets(self.ModeButtons)

    if self.basicMode :
      MainWindow.showWidgets(self.checkboxes)
    else :
      pass

  def Bluetooth_connect(self):
    target_name = "LEDstrip"
    target_address = None

    self.updateBluemessage("Device search...", 'orange')

    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
    for btaddr, btname, btclass in nearby_devices:
      if target_name == btname:
        target_address = btaddr
        break
    if target_address is not None:
      self.updateBluemessage(f"Compatible device found with MAC address : {target_address}", 'green')
      serverMACAddress = target_address
      port = 1
      self.socket_b = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
      try :
        self.socket_b.connect((serverMACAddress,port))
      except :
        self.updateBluemessage("Unable to connect, check that the device is in working order", 'red')
        return
      
      self.connexion = True
      self.activateManipulation()
      self.loop_thread = threading.Thread(target=self.loopData, daemon=True)
      self.loop_thread.start()
    else:
      self.updateBluemessage("No suitable device found nearby", 'red')

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  sys.exit(app.exec())