from machine import Pin, ADC, Timer, TouchPad, PWM
import machine
from time import sleep
import time
import network
import ntptime

# configurar display
seg7 = [18,19,4,17,16,21,5]
for i in range(0,7):
    Pin(seg7[i], Pin.OUT)

display = [[0,0,0,0,0,0,1],
           [1,0,0,1,1,1,1],
           [0,0,1,0,0,1,0],
           [0,0,0,0,1,1,0],
           [1,0,0,1,1,0,0],
           [0,1,0,0,1,0,0],
           [1,1,0,0,0,0,0],
           [0,0,0,1,1,1,1],
           [0,0,0,0,0,0,0],
           [0,0,0,1,1,0,0]]

# configurar temporizador/contador
inicio = 40
contador = inicio

timer = Timer(1)

# configurar touchpad
TpStart = TouchPad(Pin(14))
TpStop = TouchPad(Pin(27))
TpReset = TouchPad(Pin(32))
TpHora = TouchPad(Pin(13))
TpServo = TouchPad(Pin(12))

# configurar PWM
buzzer = PWM(Pin(2))
buzzer.freq(1)
an1 = PWM(Pin(23))
an1.freq(1000)
an2 = PWM(Pin(22))
an2.freq(1000)
ledR = PWM(Pin(33))
ledR.freq(500)
ledG = PWM(Pin(25))
ledG.freq(500)
ledB = PWM(Pin(26))
ledB.freq(500)
servo = PWM(Pin(15))
servo.freq(50)

# Configurar ADC
pot = ADC(Pin(34))
pot.atten(ADC.ATTN_11DB)

# musica
notas = {
    'C': 261,
    'D': 294,
    'E': 329,
    'F': 349,
    'G': 392,
    'A': 440,
    'B': 493,
    'C5': 523,
    'D5': 587,
    'E5': 659,
    'F5': 698,
    'G5': 783,
    'A5': 880,
    'B5': 987
}
melodia = [
    ('C', 0.6),
    ('B5', 0.6),
    ('D', 0.6),
    ('F', 0.3),
    ('A', 0.3),
    ('C5', 0.3),
    ('E5', 0.3),
    ('F5', 0.3),
    ('A5', 0.9)
]

# funciones
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Conectado:', wlan.ifconfig())

def sync_time():
    ntptime.settime()
    timezone_offset = -5 * 3600
    local_time = time.localtime(time.time() + timezone_offset)
    return local_time

def contarTiempo(timer):
    global contador
    contador +=1

def tocarCancion(nota, tiempo):
    buzzer.freq(notas[nota])
    buzzer.duty(1000)
    sleep(tiempo)
    buzzer.duty(0)
    sleep(0.01)

def mostrarDisplay(contador):
    display2 = contador%10
    display1 = int(contador/10)
    valorPot = map(pot.read(), 0, 4095, 0, 1023) 
    for i in range(0,7):
        Pin(seg7[i], value = display[display1][i])
        an1.duty(valorPot)
        an2.duty(0)
    sleep(0.01)
    for i in range(0,7):
        Pin(seg7[i], value = display[display2][i])
        an1.duty(0)
        an2.duty(valorPot)
    sleep(0.01)

# funciones de buzzer
def buzzerSilencio():
    buzzer.duty(0)

def buzzerSonido():
    for n, t in melodia:
        tocarCancion(n, t)

# funciones de led RGB
def colorRGB():
    ledR.duty(800)
    ledG.duty(512)
    ledB.duty(1023)    

def sinColorRGB():
    ledR.duty(0)
    ledG.duty(0)
    ledB.duty(0)

#funciones de servomotor
def map(x, x_min, x_max, y_min, y_max):
    return int(((x-x_min) * (y_max-y_min) / (x_max-x_min)) + y_min)

def moverServo(posicion):
    servo.duty(map(posicion, 0 , 180, 20, 120))

# variables
buzzerSilencio()
sinColorRGB()
modo = 0
posicion = 0
posicion1 = 20
posicion2 = 84
punto = 0
aux = False
moverServo(posicion)
connect_wifi('iPhone', 'Aley2201')
horaActual = sync_time()
# tiempo actual
horaActual = time.localtime()

while True:
    if modo == 0:
        eStart = TpStart.read()
        if eStart < 150:
            timer.init(period=1000, mode=Timer.PERIODIC, callback=contarTiempo)
            buzzerSilencio()
            sinColorRGB()
        eStop = TpStop.read()
        if eStop < 150:
            timer.deinit()
        eReset = TpReset.read()
        if eReset < 150:
            timer.deinit()
            contador = inicio
            buzzerSilencio()
            sinColorRGB()
        if contador >= 60:
            contador = 0
            mostrarDisplay(contador)
            timer.deinit()
            colorRGB()
            buzzerSonido()
        mostrarDisplay(contador)
    else:
        eStart = TpStart.read()
        if eStart < 150:
            modo = 0
            sleep(1)
    
    eHora = TpHora.read()
    if eHora < 150:
        if modo != 1:
            modo = 1
            sleep(1)
    if modo == 1:
        horaActual = time.localtime()
        mostrarDisplay(horaActual[4])

    if modo == 2:
        an1.duty(0)
        an2.duty(0)
        eServo = TpServo.read()
        if eServo < 150:
            if punto != 1:
                moverServo(posicion1)
                punto = 1
            else:
                moverServo(posicion2)
                punto = 2
    else:
        eServo = TpServo.read()
        if eServo < 150 and aux == False:
            modo = 2
            punto = 0
            aux = True
            sleep(0.5)
        else:
            if eServo >= 150:
                aux = False