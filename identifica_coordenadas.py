#esse arquivo é pra identificar as coordenadas de um ponto para usar no pyautogui
import pyautogui
import time
# # Movimente o mouse até o botão desejado e anote as coordenadas que serão impressas
print("Mova o mouse para o botão desejado.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"Posição atual do mouse: ({x}, {y})", end="\r")
except KeyboardInterrupt:
    print("\nCoordenação capturada. Código encerrado.")
    