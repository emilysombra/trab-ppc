from threading import Thread


# 0: esquerda || 1: direita
class Ponte:
    def __init__(self):
        self.veiculos = []
        self.sentido = 0

    def mudar_sentido(self):
        self.sentido = 1 - self.sentido


def t_ponte():
    ponte = Ponte()
    print(ponte)


# código que será executado ao iniciar o programa
def main():
    ponte = Thread(target=t_ponte)
    ponte.start()


if(__name__ == '__main__'):
    main()
