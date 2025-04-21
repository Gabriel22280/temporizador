from machine import Pin, ADC, Timer, TouchPad, PWM
from time import sleep

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
inicio = 55
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
}
melodia = [
    ('C', 0.5),
    ('D', 0.5),
    ('E', 0.5),
    ('F', 0.5),
    ('G', 0.5),
    ('A', 0.5),
    ('B', 0.5),
    ('C5', 0.5)
]

# funciones
def contarTiempo(timer):
    global contador
    contador +=1

def map(x, x_min, x_max, y_min, y_max):
    return int(((x-x_min) * (y_max-y_min) / (x_max-x_min)) + y_min)

def tocarCancion(nota, tiempo):
    buzzer.freq(notas[nota])
    buzzer.duty(512)
    sleep(tiempo)
    buzzer.duty(0)
    sleep(0.05)

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

def buzzerSilencio():
    buzzer.duty(0)

def buzzerSonido():
    for n, t in melodia:
        tocarCancion(n, t)

def colorRGB():
    ledR.duty(250)
    ledG.duty(512)
    ledB.duty(1023)    

def sinColorRGB():
    ledR.duty(0)
    ledG.duty(0)
    ledB.duty(0)

# variables
buzzerSilencio()
sinColorRGB()

while True:
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
        timer.deinit()
        colorRGB()
        buzzerSonido()
    mostrarDisplay(contador)
