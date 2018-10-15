from threading import Thread
from threading import Condition
from collections import deque
from random import choice
from numpy import mean as media
import time
import socket
import pickle
from carros import Carro
from carros import Caminhao

# constante que limita os carros
LIMITE_VEICULOS = 106


# classe ponte
# 0: esquerda || 1: direita
class Ponte:
    def __init__(self):
        self.veiculos = deque([])
        self.sentido = 0

    def mudar_sentido(self):
        self.sentido = 1 - self.sentido


# variaveis globais
esquerda = deque([])
direita = deque([])
ponte = Ponte()
espera_esq = []
espera_dir = []
relogio_ponte = 0
fim_programa = False
total_veiculos = 0


def escolhe_carro():
    veiculo = None
    tempo = None
    sentido = None
    if(len(ponte.veiculos) > 0):
        if(ponte.sentido == 1 and len(direita) > 0):
            veiculo, tempo = direita.popleft()
            sentido = 1
        elif(ponte.sentido == 0 and len(esquerda) > 0):
            veiculo, tempo = esquerda.popleft()
            sentido = 0
    else:
        disponiveis = []
        if(len(esquerda) > 0):
            disponiveis.append(0)
        elif(len(direita) > 0):
            disponiveis.append(1)

        sentido = choice(disponiveis)
        if(sentido):
            veiculo, tempo = direita.popleft()
        else:
            veiculo, tempo = esquerda.popleft()

    return veiculo, tempo, sentido


# thread que calcula o tempo de utilização da ponte
def tempo_ponte(cv_ponte):
    global relogio_ponte
    print('(Tempo)Medição do tempo iniciada')
    while(True):
        # espera até ter um carro na ponte
        with(cv_ponte):
            while(len(ponte.veiculos) == 0 and not fim_programa):
                cv_ponte.wait()

        # marca o momento que a ponte começa a ser utilizada
        tempo_inicial = time.time()
        print('(Tempo)Ponte sendo utilizada')

        # espera até a ponte deixar de ser utilizada
        with(cv_ponte):
            while(len(ponte.veiculos) >= 1 and not fim_programa):
                cv_ponte.wait()

        # marca o momento que a ponte deixa de ser utilizada
        # e incrementa o tempo total
        tempo_fim = time.time() - tempo_inicial
        relogio_ponte += tempo_fim
        print('(Tempo)Ponte deixou de ser utilizada')

        # condição de parada da thread
        if(fim_programa):
            print('(Tempo)Cálculo de tempo concluído')
            break


# servidor que recebe os veiculos
def recebe_msg(cv_fila):
    print('(Server)Servidor iniciado')
    veiculos_recebidos = 0
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
            try:
                msg = connect.recv(1024)
                msg = pickle.loads(msg)
            except EOFError:
                print('(Server)Mensagem vazia')
                time.sleep(1)
                continue
            tipo = int(msg[0])
            sentido = int(msg[1])
            print('-------------')
            print('msg: {} | tipo: {}, sentido: {}'.format(msg, tipo, sentido))
            print('-------------')
            if(msg):
                break

        print('(Server)Veículo recebido')
        print('(Server)Veículo recebidos: {}'.format(veiculos_recebidos + 1))

        # gera uma tupla com o veiculo e o tempo de chegada dele
        # dependendo do tipo, gera um carro ou um caminhão
        if(tipo):
            veiculo = Caminhao()
        else:
            veiculo = Carro()
        tupla = (veiculo, time.time())

        # dependendo do sentido, adiciona-o na fila correspondente
        if(sentido):
            direita.append(tupla)
            veiculos_recebidos += 1
            print('(Server)Carro inserido na fila direita')
            print('(Server)Carros na fila direita: {}'.format(len(direita)))
        else:
            esquerda.append(tupla)
            print('(Server)Carro inserido na fila esquerda')
            veiculos_recebidos += 1
            print('(Server)Carros na fila esquerda: {}'.format(len(esquerda)))

        # acorda a thread da ponte sempre que chegar um carro
        with(cv_fila):
            cv_fila.notify_all()

        if(veiculos_recebidos >= LIMITE_VEICULOS):
            connect.close()
            print('(Server)Servidor desligado')
            break


# linha de execução da thread da ponte
def t_ponte(cv_ponte, cv_fila):
    global reset
    global total_veiculos
    print('(Ponte)Thread Ponte iniciada')
    qtd_veiculos = 0
    while(True):
        with(cv_fila):
            while(len(direita) == 0 and len(esquerda) == 0):
                print('(Ponte)Esperando haver carro em espera')

        # checa se a ponte possui carros
        if(len(ponte.veiculos) > 0):
            pass
        else:
            pass

        # checa o sentido da ponte e retira o veiculo da fila correspondente
        if(ponte.sentido):
            print('(Ponte)Sentido da ponte: direita')
            veiculo, tempo = direita.popleft()
        else:
            print('(Ponte)Sentido da ponte: esquerda')
            veiculo, tempo = esquerda.popleft()

        # checa se é um caminhão
        if(isinstance(veiculo, Caminhao)):
            print('(Ponte)Veículo é um caminhão')
            print('(Ponte)Esperando ponte esvaziar')
            # espera a ponte esvaziar
            with(cv_ponte):
                while(len(ponte.veiculos) > 0):
                    cv_ponte.notify_all()
                    cv_ponte.wait()

                print('(Ponte)Ponte esvaziou')

        # armazena o tempo de espera na lista correspondente
        espera = time.time() - tempo
        if(ponte.sentido):
            espera_dir.append(espera)
        else:
            espera_esq.append(espera)

        # tupla com veiculo e tempo de chegada
        tupla = (veiculo, time.time())
        ponte.veiculos.append(tupla)
        # notifica que há um carro na ponte
        with(cv_ponte):
            cv_ponte.notify_all()

        qtd_veiculos += 1
        total_veiculos += 1
        print('(Ponte)Qtd veiculos na ponte: {}'.format(len(ponte.veiculos)))
        print('(Ponte)Qtd veiculos no msm sentido: {}'.format(qtd_veiculos))
        print('(Ponte)Total de veiculos: {}'.format(total_veiculos))

        # espera um tempo para adicionar outro veiculo
        # se caminhão: espera caminhão passar
        # se carro: espera 2 segundos
        if(isinstance(veiculo, Caminhao)):
            with(cv_ponte):
                while(len(ponte.veiculos) > 0):
                    print('(Ponte)Esperando caminhão passar')
                    cv_ponte.notify_all()
                    cv_ponte.wait()
        else:
            time.sleep(2)

        # caso 106 veiculos ja tenham passado pela ponte, encerra a thread
        if(total_veiculos >= LIMITE_VEICULOS):
            print('(Ponte)Ponte concluída')
            break


# thread que controla a passagem dos veiculos na ponte
def remove_carros(cv_ponte):
    veiculos_removidos = 0  # contador de veiculos removidos
    while(True):
        # caso a ponte esteja vazia, dorme
        # quando a ponte possuir um veículo, é acordada
        with(cv_ponte):
            while(len(ponte.veiculos) == 0):
                print('(Removedora)Ponte vazia')
                # antes de dormir, notifica que a ponte está vazia
                cv_ponte.notify_all()
                cv_ponte.wait()
            print('(Removedora)Há um veículo na ponte')

        # checa o tempo do primeiro veículo na ponte
        # caso já tenha passado o tempo, o remove
        tempo = ponte.veiculos[0][0].tempo_travessia
        while((time.time() - ponte.veiculos[0][1]) < tempo):
            pass

        # remove um veículo da ponte e notifica
        ponte.veiculos.popleft()
        veiculos_removidos += 1
        with(cv_ponte):
            cv_ponte.notify_all()
        print('(Removedora)Carro removido da ponte')
        # caso já tenha removido 106 veiculos, para
        if(veiculos_removidos >= LIMITE_VEICULOS):
            print('(Removedora)Removedora concluída')
            break


def resultados(total):
    print()
    print('Resultados:')
    print('Veículos passados pela ponte: {}'.format(LIMITE_VEICULOS))
    print('Tempos de espera:')
    print('Esquerda:')
    print('Máximo: {}'.format(max(espera_esq)))
    print('Mínimo: {}'.format(min(espera_esq)))
    print('Média: {}'.format(media(espera_esq)))
    print('------')
    print('Direita:')
    print('Máximo: {}'.format(max(espera_dir)))
    print('Mínimo: {}'.format(min(espera_dir)))
    print('Média: {}'.format(media(espera_dir)))
    print('------')
    print('Tempo utilização da ponte: {}'.format(relogio_ponte))
    print('Tempo total do programa: {}'.format(total))


# código que será executado ao iniciar o programa
def main():
    total = time.time()
    global fim_programa
    print('(Main)Programa iniciado')

    cv_ponte = Condition()
    cv_fila = Condition()

    tempo = Thread(target=tempo_ponte, args=(cv_ponte, ))
    tempo.start()

    recebimento = Thread(target=recebe_msg, args=(cv_fila, ))
    recebimento.start()

    ponte = Thread(target=t_ponte, args=(cv_ponte, cv_fila))
    ponte.start()

    remove = Thread(target=remove_carros, args=(cv_ponte, ))
    remove.start()

    ponte.join()
    remove.join()
    fim_programa = True
    with(cv_ponte):
        cv_ponte.notify_all()
    tempo.join()

    print('(Main)Programa encerrado')
    total = time.time() - total
    resultados(total)


if(__name__ == '__main__'):
    main()
