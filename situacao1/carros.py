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
            print('(Client)Carro enviado (esquerda)')

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
    sentidos_disponiveis = [0, 1]  # 0: esquerda || 1: direita
    qtd_esq = 0
    qtd_dir = 0
    while(True):
        carro = Carro()
        if(len(sentidos_disponiveis) == 0):
            break
        sentido = randint(0, len(sentidos_disponiveis) - 1)
        sentido = sentidos_disponiveis[sentido]
        if(sentido):
            direita.append(carro)
            qtd_dir += 1
            print('(Fila)Carro inserido na fila direita')

            if(qtd_dir >= 50):
                try:
                    sentidos_disponiveis.remove(1)
                except ValueError:
                    pass
        else:
            esquerda.append(carro)
            qtd_esq += 1
            print('(Fila)Carro inserido na fila esquerda')

            if(qtd_esq >= 50):
                try:
                    sentidos_disponiveis.remove(0)
                except ValueError:
                    pass

        print('(Fila)Número de carros gerados:')
        print('(Fila)Esquerda: {}'.format(qtd_esq))
        print('(Fila)Direita: {}'.format(qtd_dir))

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
