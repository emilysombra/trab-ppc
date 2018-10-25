from collections import deque


# classe ponte
# 0: esquerda || 1: direita
class Pont:
    def __init__(self):
        self.vehicules = deque([])
        self.direction = 0

    def mudar_sentido(self):
        self.direction = 1 - self.direction

    def set_direction(self, direction):
        self.direction = direction


# classe veiculo
# super classe de carro e caminhão
class Veiculo:
    def __init__(self, tempo):
        self.tempo_travessia = tempo


# classe carro
class Carro(Veiculo):
    def __init__(self):
        super().__init__(10)


# classe caminhao
class Caminhao(Veiculo):
    def __init__(self):
        super().__init__(20)
