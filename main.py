class Veiculo:
    def __init__(self, tempo):
        self.tempo_travessia = tempo


class Carro(Veiculo):
    def __init__(self):
        super().__init__(10)


class Ponte:
    def __init__(self):
        self.veiculos = []
        self.sentido = 0

    def mudar_sentido(self):
        self.sentido = 1 - self.sentido


def main():
    ponte = Ponte()
    print(ponte)


if(__name__ == '__main__'):
    pass
