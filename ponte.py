from threading import Thread
from threading import Condition
from collections import deque
from numpy import mean as media
import time
import socket
from carros import Carro

# constante que limita os carros
LIMITE_CARROS = 100


# classe ponte
# 0: esquerda || 1: direita
class Ponte:
    def __init__(self):
        self.veiculos = deque([])
        self.sentido = 0

    def mudar_sentido(self):
        self.sentido = 1 - self.sentido


esquerda = deque([])
direita = deque([])
ponte = Ponte()
tempos_espera = []


# servidor que recebe os carros
def recebe_msg(cv_fila):
    print('(Server)Servidor iniciado')
    carros_recebidos = 0
    # inicia e configura o servidor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind(('localhost', 5000))
    servidor.listen(5)

    # recebe a conexão
    connect, cliente = servidor.accept()
    print('(Server)Servidor recebeu conexão')
    while(True):
        # espera até receber uma mensagem
        while(True):
            msg = connect.recv(1024)
            sentido = int(msg.decode())
            if(msg):
                break

        print('(Server)Carro recebido')
        print('(Server)Carros recebidos: {}'.format(carros_recebidos + 1))
        tupla = (Carro(), time.time())
        if(sentido):
            direita.append(tupla)
            carros_recebidos += 1
            print('(Server)Carro inserido na fila direita')
            print('(Server)Carros na fila direita: {}'.format(len(direita)))
        else:
            esquerda.append(tupla)
            print('(Server)Carro inserido na fila esquerda')
            carros_recebidos += 1
            print('(Server)Carros na fila esquerda: {}'.format(len(esquerda)))

        # acorda a thread da ponte sempre que chegar um carro
        with(cv_fila):
            cv_fila.notify_all()

        if(carros_recebidos >= LIMITE_CARROS):
            connect.close()
            print('(Server)Servidor desligado')
            break


# linha de execução da thread da ponte
def t_ponte(cv_ponte, cv_fila):
    print('(Ponte)Thread Ponte iniciada')
    global ponte
    qtd_carros = 0
    total_carros = 0
    while(True):
        if(ponte.sentido):
            direcao = 'direita'
        else:
            direcao = 'esquerda'
        print('(Ponte)Sentido da ponte: {}'.format(direcao))
        # checa o sentido da ponte
        # entra no if caso seja direita, no else caso seja esquerda
        # c
        if(ponte.sentido):
            with(cv_fila):
                # espera haver um carro na fila da direita
                while(len(direita) == 0):
                    print('(Ponte)Esperando carro na fila direita')
                    cv_fila.wait()

            carro, tempo = direita.popleft()  # remove carro da fila
            espera = time.time() - tempo
            tempos_espera.append(espera)
        else:
            with(cv_fila):
                # espera haver um carro na fila da esquerda
                while(len(esquerda) == 0):
                    print('(Ponte)Esperando carro na fila esquerda')
                    cv_fila.wait()

            carro, tempo = esquerda.popleft()  # remove carro da fila
            espera = time.time() - tempo
            tempos_espera.append(espera)

        # --- carro sai da fila nesse momento --- #

        # sempre que chegar um carro, acorda a thread de remover
        with(cv_ponte):
            tuplinha = (carro, time.time())  # tupla com carro e tempo inicial
            ponte.veiculos.append(tuplinha)  # insere tupla na fila

            # --- carro entra na ponte nesse momento --- #

            cv_ponte.notify_all()  # notifica a thread que remove carros

        qtd_carros += 1
        total_carros += 1
        print('(Ponte)Qtd. de carros na ponte: {}'.format(len(ponte.veiculos)))
        print('(Ponte)Qtd. de carros no msm sentido: {}'.format(qtd_carros))
        print('(Ponte)Total de carros: {}'.format(total_carros))
        time.sleep(2)  # espera 2 segundos antes de inserir outro carro

        # caso já tenha passado 5 carros num mesmo sentido,
        # espera a ponte esvaziar e troca o sentido
        if(qtd_carros >= 5):
            with(cv_ponte):
                while(len(ponte.veiculos) > 0):
                    print('(Ponte)Esperando ponte esvaziar')
                    cv_ponte.wait()
            ponte.mudar_sentido()
            print('(Ponte)Ponte mudou de sentido')
            qtd_carros = 0

        # caso 100 carros ja tenham passado pela ponte, encerra a thread
        if(total_carros >= LIMITE_CARROS):
            print('(Ponte)Ponte concluída')
            break


# thread que controla a passagem dos carros na ponte
def remove_carros(cv_ponte):
    carros_removidos = 0  # contador de carros removidos
    while(True):
        # caso a ponte esteja vazia, dorme
        # quando a ponte possuir um carro, é acordada
        with(cv_ponte):
            while(len(ponte.veiculos) == 0):
                print('(Removedora)Ponte vazia')
                # antes de dormir, notifica que a ponte está vazia
                cv_ponte.notify_all()
                cv_ponte.wait()
            print('(Removedora)Há um carro na ponte')

        # checa o tempo do primeiro carro na ponte
        # caso já tenha passado o tempo, o remove
        tempo = ponte.veiculos[0][0].tempo_travessia
        while((time.time() - ponte.veiculos[0][1]) < tempo):
            pass

        # remove um carro da ponte e notifica
        ponte.veiculos.popleft()
        carros_removidos += 1
        with(cv_ponte):
            cv_ponte.notify_all()
        print('(Removedora)Carro removido da ponte')
        # caso já tenha removido 100 carros, para
        if(carros_removidos >= LIMITE_CARROS):
            print('(Removedora)Removedora concluída')
            break


def resultados():
    print()
    print('Resultados:')
    print('Carros passados pela ponte: {}'.format(LIMITE_CARROS))
    print('Tempos de espera:')
    print('Máximo: {}'.format(max(tempos_espera)))
    print('Mínimo: {}'.format(min(tempos_espera)))
    print('Média: {}'.format(media(tempos_espera)))


# código que será executado ao iniciar o programa
def main():
    print('(Main)Programa iniciado')
    cv_ponte = Condition()
    cv_fila = Condition()
    recebimento = Thread(target=recebe_msg, args=(cv_fila, ))
    recebimento.start()
    ponte = Thread(target=t_ponte, args=(cv_ponte, cv_fila))
    ponte.start()
    remove = Thread(target=remove_carros, args=(cv_ponte, ))
    remove.start()
    ponte.join()
    print('(Main)Programa encerrado')
    resultados()


if(__name__ == '__main__'):
    main()
