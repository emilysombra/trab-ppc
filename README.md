Apresentação
Esse é um clássico problema de programação concorrente, também conhecido como One-Lane Bridge Problem. 

Uma ponte sobre um rio tem apenas uma faixa para a passagem dos veículos. Assim, a qualquer momento, a ponte pode ser atravessada apenas por um ou mais veículos no mesmo sentido (mas não de sentidos opostos).

O trabalho consiste em propor um algoritmo concorrente para resolver o problema da ponte de uma faixa sem deadlock ou starvation.
Proposta do Problema
1) Somente carros com sinalizador
Considere que n=100 carros irão cruzar a ponte, 50 em cada sentido. O tempo de chegada de cada carro Ta é aleatório, variando entre 2 segundos e 6 segundos. O tempo de travessia de cada carro pela ponte Tc é de 10 segundos. Considerar um espeço Ts =2 seg entre os veículos no mesmo sentido.. Quando P=5 carros cruzarem a ponte, deverá trocar o sentido do tráfego, caso haja veículos para cruzar no sentido inverso. 

Dados n = 100, Ta = 2 a 6 seg, Tc = 10 seg, Ts =2 seg,  P=5.
2) Carros e caminhões com sinalizador
Agora, nosso problema inclui caminhões que são mais lentos e por questão de segurança, devem cruzar a ponte sozinhos. Considere agora que n=100 carros e m=6 caminhões irão cruzar a ponte, 50 carros e 3 caminhões em cada sentido. O tempo de chegada de cada carro ou caminhão Ta é aleatório, variando entre 2 segundos e 6 segundos. O tempo de travessia de cada carro pela ponte Tc é de 10 segundos e o tempo de travessia de cada caminhão Tt é de 20 segundos, considerar um espeço Ts =2 seg entre os veículos no mesmo sentido. Por questão de segurança, um caminhão deverá cruzar a ponte sozinho (espera o carro da frente terminar a travessia). 

Considere n = 100, m=6, Ta = 2 a 6 seg, Tc = 10 seg,  Tt = 20 seg, Ts =2 seg, P=5.
3) Carros e caminhões sem sinalizador
Neste caso, não existe um sinalizador na ponte indicando o sentido do fluxo, apenas carros e caminhões no qual o motorista decide se vai esperar ou atravessar. A lógica é que quando um veículo chegar na ponte, se houver outro veículo atravessando no mesmo sentido, ele pode cruzar, respeitando as regras. Se houver veículo no sentido contrário, aguarda este terminar a travessia para tentar atravessar. Crie um mecanismo que permita a travessia da ponte sem causar acidentes e sem ter deadlocks ou starvation.Não deve haver um sinalizador para indicar o sentido, apenas indicar se há veículo na ponte e qual o sentido.

Dados n = 100, m=6, Ta = 2 a 6 seg, Tc = 10 seg, Tt = 20 seg, Ts =2 seg.
Implementação
O trabalho prático consiste em escrever um programa em C, C++, Java ou Python para simular a situação

Utilizar as seguintes classes: 
Carros.
Caminhões.
Sinalizadores (ente que permite ou impede a passagem do veículo nas cabeceiras da ponte). 

Ao final da execução deve ser calculado:
Quantidade de veículos (carros e caminhões) que cruzaram.
Tempo mínimo, máximo e médio de espera dos veículos na fila.
Tempo de utilização da ponte (tempo utilizado/tempo total).
Avaliação
A avaliação consiste em uma apresentação oral e um trabalho escrito.
Apresentação Oral
Os alunos deverão fazer uma apresentação oral do trabalho realizado em data a ser marcada. Na apresentação deverá mostrar a análise do problema, as formas de resolução, as decisões de implementação e a apresentação da execução do programa. Considera-se a execução correta se o programa cumprir o determinado sem a ocorrência de deadlocks ou starvation.

O calendário de apresentação será definido futuramente.
Trabalho Escrito
Os alunos deverão entregar um relatório escrito com os seguintes tópicos:
Formulação do problema
Descrição dos algoritmos
Descrição da Implementação (diagrama de classes)
Resultados