from random import randint
import time
from threading import Thread
from collections import deque
import socket

esquerda = deque([])
direita = deque([])


class Veiculo:
    def __init__(self, tempo):
        self.tempo_travessia = tempo


class Carro(Veiculo):
    def __init__(self):
        super().__init__(10)


def enviar_msg():
    print('(Client)Cliente iniciado')
    carros_enviados = 0
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = ('localhost', 5000)
    cliente.connect(destino)

    while(True):
        print('(Client)Qtd de carros enviados: {}'.format(carros_enviados))
        # espera haver um carro
        while(len(esquerda) == 0 and len(direita) == 0):
            pass

        if(len(esquerda) > 0):
            esquerda.popleft()
            sentido = '0'
            cliente.send(sentido.encode())
            carros_enviados += 1
            print('Carro enviado (esquerda)')

        if(len(direita) > 0):
            direita.popleft()
            sentido = '1'
            cliente.send(sentido.encode())
            carros_enviados += 1
            print('(Client)Carro enviado (direita)')
        if(carros_enviados >= 100):
            cliente.close()
            break


def t_filas():
    print('(Fila)Thread que insere carros nas filas iniciada')
    for i in range(100):
        carro = Carro()
        # 1: direita || 0: esquerda
        if(i % 2):
            direita.append(carro)
            print('(Fila)Carro inserido na fila direita')
        else:
            esquerda.append(carro)
            print('(Fila)Carro inserido na fila esquerda')

        print('(Fila)Número de carros gerados: {}'.format(i + 1))

        # espera 2-6 segundos para gerar outro carro
        espera = randint(2, 6)
        time.sleep(espera)


def main():
    envio = Thread(target=enviar_msg)
    envio.start()
    filas = Thread(target=t_filas)
    filas.start()


if(__name__ == '__main__'):
    main()
