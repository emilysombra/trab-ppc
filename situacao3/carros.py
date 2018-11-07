from random import (randint, choice)
import time
from threading import Thread
from collections import deque
import socket
import pickle

esquerda = deque([])
direita = deque([])


def enviar_msg():
    print('(Client)Cliente iniciado')
    carros_enviados = 0
    caminhoes_enviados = 0
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = ('localhost', 5000)
    cliente.connect(destino)

    while(True):
        print('(Client)Qtd de carros enviados: {}'.format(carros_enviados))
        s = '(Client)Qtd de caminhoes enviados: {}'.format(caminhoes_enviados)
        print(s)
        # espera haver um carro
        while(len(esquerda) == 0 and len(direita) == 0):
            pass

        if(len(esquerda) > 0):
            tipo = esquerda.popleft()  # 0: carro || 1: caminhão
            if(tipo):
                caminhoes_enviados += 1
            else:
                carros_enviados += 1

            tipo = str(tipo)
            tupla = (tipo, '0')
            tupla = pickle.dumps(tupla)
            cliente.send(tupla)
            print('(Client)Carro enviado (esquerda)')

        if(len(direita) > 0):
            tipo = direita.popleft()  # 0: carro || 1: caminhão
            if(tipo):
                caminhoes_enviados += 1
            else:
                carros_enviados += 1

            tipo = str(tipo)
            tupla = (tipo, '1')
            tupla = pickle.dumps(tupla)
            cliente.send(tupla)
            print('(Client)Carro enviado (direita)')
        if(carros_enviados >= 100 and caminhoes_enviados >= 6):
            cliente.close()
            break


def t_filas():
    print('(Fila)Thread que insere carros nas filas iniciada')
    # 0: carro - esquerda || 1: carro - direita
    # 2: caminhao - esquerda || 3: caminhao - direita
    combinacoes_disponiveis = [0, 1, 2, 3]
    carros_esq = 0
    caminhoes_esq = 0
    carros_dir = 0
    caminhoes_dir = 0
    while(True):
        if(len(combinacoes_disponiveis) == 0):
            break

        # gera uma combinacao de veiculo e sentido
        combinacao = choice(combinacoes_disponiveis)
        # insere na fila correspondente
        if(combinacao == 0):
            tipo_veiculo = 0
            esquerda.append(tipo_veiculo)
            carros_esq += 1
            print('(Fila)Carro inserido na fila esquerda')
            if(carros_esq >= 50):
                combinacoes_disponiveis.remove(0)
        elif(combinacao == 1):
            tipo_veiculo = 0
            direita.append(tipo_veiculo)
            carros_dir += 1
            print('(Fila)Carro inserido na fila direita')
            if(carros_dir >= 50):
                combinacoes_disponiveis.remove(1)
        elif(combinacao == 2):
            tipo_veiculo = 1
            esquerda.append(tipo_veiculo)
            caminhoes_esq += 1
            print('(Fila)Caminhão inserido na fila esquerda')
            if(caminhoes_esq >= 3):
                combinacoes_disponiveis.remove(2)
        else:
            tipo_veiculo = 1
            direita.append(tipo_veiculo)
            caminhoes_dir += 1
            print('(Fila)Caminhão inserido na fila direita')
            if(caminhoes_dir >= 3):
                combinacoes_disponiveis.remove(3)

        print('(Fila)Número de carros gerados:')
        print('(Fila)Esquerda: {}'.format(carros_esq))
        print('(Fila)Direita: {}'.format(carros_dir))
        print('(Fila)Número de caminhoes gerados:')
        print('(Fila)Esquerda: {}'.format(caminhoes_esq))
        print('(Fila)Direita: {}'.format(caminhoes_dir))

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
