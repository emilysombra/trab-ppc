from random import randint
from time import time
from threading import Thread

esquerda = []
direita = []


class Veiculo:
    def __init__(self, tempo):
        self.tempo_travessia = tempo


class Carro(Veiculo):
    def __init__(self):
        super().__init__(10)


def t_filas():
    print(esquerda, direita)
    qtd_carros = 0
    while(qtd_carros < 100):
        carro = Carro()
        sentido = randint(0, 1)  # 0: esquerda || 1: direita
        if(sentido):
            direita.append(carro)
        else:
            esquerda.append(carro)
        espera = randint(2, 6)
        time.sleep(espera)


def main():
    filas = Thread(target=t_filas)
    filas.start()


if(__name__ == '__main__'):
    main()
