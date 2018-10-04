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


class Caminhao(Veiculo):
    def __init__(self):
        super().__init__(20)


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
    veiculos_disponiveis = [0, 1]  # 0: carro || 1: caminhão
    carros_esq = 0
    caminhoes_esq = 0
    carros_dir = 0
    caminhoes_dir = 0
    while(True):
        if(len(sentidos_disponiveis) == 0 or len(veiculos_disponiveis) == 0):
            break

        # gera aleatoriamente um tipo de veiculo
        tipo_veiculo = randint(0, len(veiculos_disponiveis) - 1)
        tipo_veiculo = veiculos_disponiveis[tipo_veiculo]

        # cria um veiculo
        if(tipo_veiculo):
            veiculo = Caminhao()
        else:
            veiculo = Carro()

        # gera aleatoriamente um sentido
        sentido = randint(0, len(sentidos_disponiveis) - 1)
        sentido = sentidos_disponiveis[sentido]

        # insere o veiculo na fila correspondente
        if(sentido):
            # adiciona o veiculo na fila
            direita.append(veiculo)
            # incrementa o contador correspondente
            if(tipo_veiculo):
                caminhoes_dir += 1
            else:
                carros_dir += 1
            print('(Fila)Carro inserido na fila direita')

            if(carros_dir >= 50 and caminhoes_dir >= 3):
                try:
                    sentidos_disponiveis.remove(1)
                except ValueError:
                    pass
        else:
            # adiciona o veiculo na fila
            esquerda.append(veiculo)
            # incrementa o contador correspondente
            if(tipo_veiculo):
                caminhoes_esq += 1
            else:
                carros_esq += 1
            print('(Fila)Carro inserido na fila esquerda')

            if(carros_esq >= 50 and caminhoes_esq >= 3):
                try:
                    sentidos_disponiveis.remove(0)
                except ValueError:
                    pass

        print('(Fila)Número de carros gerados:')
        print('(Fila)Esquerda: {}'.format(carros_esq))
        print('(Fila)Direita: {}'.format(carros_dir))

        # caso tenha gerado 100 carros, impede de gerar carros
        if(carros_esq + carros_dir >= 100):
            try:
                veiculos_disponiveis.remove(0)
            except ValueError:
                pass

        # caso tenha gerado 100 carros, impede de gerar carros
        if(caminhoes_esq + caminhoes_dir >= 6):
            try:
                veiculos_disponiveis.remove(1)
            except ValueError:
                pass

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
