from threading import Thread
from threading import Condition
from collections import deque
from random import choice
from numpy import mean as media
import time
import socket
import pickle
from aux import Carro
from aux import Caminhao
from aux import Pont
# from aux import Pont

# constante que limita os carros
LIMITE_VEHICULES = 106


# variaveis globais
gauche = deque([])
droite = deque([])
pont = Pont()
attendre_gauche = []
attendre_droite = []
relogio_ponte = 0
fim_programa = False
total_veiculos = 0


# função para tirar um carro da fila
def escolhe_carro():
    vehicule = None
    tempo = None
    direction = None
    if(len(pont.vehicules) > 0):
        if(pont.direction == 1 and len(droite) > 0):
            vehicule, tempo = droite.popleft()
            direction = 1
        elif(pont.direction == 0 and len(gauche) > 0):
            vehicule, tempo = gauche.popleft()
            direction = 0
    else:
        disponiveis = []
        if(len(gauche) > 0):
            disponiveis.append(0)
        elif(len(droite) > 0):
            disponiveis.append(1)

        direction = choice(disponiveis)
        if(direction):
            vehicule, tempo = droite.popleft()
        else:
            vehicule, tempo = gauche.popleft()

    return vehicule, tempo, direction


# thread que calcula o tempo de utilização da ponte
def tempo_ponte(cv_pont):
    global relogio_ponte
    print('(Tempo)Medição do tempo iniciada')
    while(True):
        # espera até ter um carro na ponte
        with(cv_pont):
            while(len(pont.vehicules) == 0 and not fim_programa):
                cv_pont.wait()

        # marca o momento que a ponte começa a ser utilizada
        tempo_inicial = time.time()
        print('(Tempo)Ponte sendo utilizada')

        # espera até a ponte deixar de ser utilizada
        with(cv_pont):
            while(len(pont.vehicules) >= 1 and not fim_programa):
                cv_pont.wait()

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
            direction = int(msg[1])
            print('-------------')
            print('msg=> tipo: {}, sentido: {}'.format(msg, tipo, direction))
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
        if(direction):
            droite.append(tupla)
            veiculos_recebidos += 1
            print('(Server)Carro inserido na fila direita')
            print('(Server)Carros na fila direita: {}'.format(len(droite)))
        else:
            gauche.append(tupla)
            print('(Server)Carro inserido na fila esquerda')
            veiculos_recebidos += 1
            print('(Server)Carros na fila esquerda: {}'.format(len(gauche)))

        # acorda a thread da ponte sempre que chegar um carro
        with(cv_fila):
            cv_fila.notify_all()

        if(veiculos_recebidos >= LIMITE_VEHICULES):
            connect.close()
            print('(Server)Servidor desligado')
            break


# linha de execução da thread da ponte
def t_ponte(cv_pont, cv_fila):
    global reset
    global total_veiculos
    print('(Ponte)Thread Ponte iniciada')
    while(True):
        with(cv_fila):
            while(len(droite) == 0 and len(gauche) == 0):
                print('(Ponte)Esperando haver carro em espera')
                cv_fila.wait()

        # escolhe um carro entre as filas
        # tenta retirar um veículo de uma fila
        veiculo, tempo, direction = escolhe_carro()
        # caso não haja um veiculo, retorna para o começo do while
        if(not veiculo):
            continue

        # veículo sai da fila nesse momento

        # seta o sentido da ponte para o do carro escolhido
        # em seguida, imprime o direction
        pont.set_direction(direction)
        if(pont.direction):
            print('(Ponte)Sentido da ponte: direita')
        else:
            print('(Ponte)Sentido da ponte: esquerda')

        # checa se é um caminhão
        if(isinstance(veiculo, Caminhao)):
            print('(Ponte)Veículo é um caminhão')
            print('(Ponte)Esperando ponte esvaziar')
            # espera a ponte esvaziar
            with(cv_pont):
                while(len(pont.vehicules) > 0):
                    cv_pont.notify_all()
                    cv_pont.wait()

                print('(Ponte)Ponte esvaziou')

        # armazena o tempo de espera na lista correspondente
        espera = time.time() - tempo
        if(pont.direction):
            attendre_droite.append(espera)
        else:
            attendre_gauche.append(espera)

        # tupla com veiculo e tempo de chegada
        tupla = (veiculo, time.time())
        # insere a tupla na ponte
        pont.vehicules.append(tupla)

        # veículo entra na ponte nesse momento

        print('(Ponte)Veículo entrou na ponte')

        # notifica que há um carro na ponte
        with(cv_pont):
            cv_pont.notify_all()

        total_veiculos += 1
        print('(Ponte)Qtd veiculos na ponte: {}'.format(len(pont.vehicules)))
        print('(Ponte)Total de veiculos: {}'.format(total_veiculos))

        # espera um tempo para adicionar outro veiculo
        # se caminhão: espera caminhão passar
        # se carro: espera 2 segundos
        if(isinstance(veiculo, Caminhao)):
            with(cv_pont):
                while(len(pont.vehicules) > 0):
                    print('(Ponte)Esperando caminhão passar')
                    cv_pont.notify_all()
                    cv_pont.wait()
        else:
            time.sleep(2)

        # caso 106 veiculos ja tenham passado pela ponte, encerra a thread
        if(total_veiculos >= LIMITE_VEHICULES):
            print('(Ponte)Ponte concluída')
            break


# thread que controla a passagem dos veiculos na ponte
def remove_carros(cv_pont):
    veiculos_removidos = 0  # contador de veiculos removidos
    while(True):
        # caso a ponte esteja vazia, dorme
        # quando a ponte possuir um veículo, é acordada
        with(cv_pont):
            while(len(pont.vehicules) == 0):
                print('(Removedora)Ponte vazia')
                # antes de dormir, notifica que a ponte está vazia
                cv_pont.notify_all()
                cv_pont.wait()
            print('(Removedora)Há um veículo na ponte')

        # checa o tempo do primeiro veículo na ponte
        # caso já tenha passado o tempo, o remove
        tempo = pont.vehicules[0][0].tempo_travessia
        while((time.time() - pont.vehicules[0][1]) < tempo):
            pass

        # remove um veículo da ponte e notifica
        pont.vehicules.popleft()
        veiculos_removidos += 1
        with(cv_pont):
            cv_pont.notify_all()
        print('(Removedora)Carro removido da ponte')
        # caso já tenha removido 106 veiculos, para
        if(veiculos_removidos >= LIMITE_VEHICULES):
            print('(Removedora)Removedora concluída')
            break


def resultados(total):
    print()
    print('Resultados:')
    print('Veículos passados pela ponte: {}'.format(LIMITE_VEHICULES))
    print('Tempos de espera:')
    print('Esquerda:')
    print('Máximo: {}'.format(max(attendre_gauche)))
    print('Mínimo: {}'.format(min(attendre_gauche)))
    print('Média: {}'.format(media(attendre_gauche)))
    print('------')
    print('Direita:')
    print('Máximo: {}'.format(max(attendre_droite)))
    print('Mínimo: {}'.format(min(attendre_droite)))
    print('Média: {}'.format(media(attendre_droite)))
    print('------')
    print('Tempo utilização da ponte: {}'.format(relogio_ponte))
    print('Tempo total do programa: {}'.format(total))


# código que será executado ao iniciar o programa
def main():
    total = time.time()
    global fim_programa
    print('(Main)Programa iniciado')

    cv_pont = Condition()
    cv_fila = Condition()

    tempo = Thread(target=tempo_ponte, args=(cv_pont, ))
    tempo.start()

    recebimento = Thread(target=recebe_msg, args=(cv_fila, ))
    recebimento.start()

    ponte = Thread(target=t_ponte, args=(cv_pont, cv_fila))
    ponte.start()

    remove = Thread(target=remove_carros, args=(cv_pont, ))
    remove.start()

    ponte.join()
    remove.join()
    fim_programa = True
    with(cv_pont):
        cv_pont.notify_all()
    tempo.join()

    print('(Main)Programa encerrado')
    total = time.time() - total
    resultados(total)


if(__name__ == '__main__'):
    main()
