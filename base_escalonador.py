import random
import time
from collections import deque
from abc import ABC, abstractmethod

#Atual

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.

class TarefaCAV:
    def __init__(self, nome, duracao, prioridade=1, tempo_chegada=0):
        self.nome = nome
        self.duracao = duracao
        self.prioridade = prioridade
        self.tempo_restante = duracao
        self.tempo_chegada = tempo_chegada # Hora em que a tarefa começa
        self.tempo_inicio_execucao = -1   # Tempo da primeira execução
        self.tempo_final = -1         # Tempo final de conclusão
        self.tempos_execucao = []         # Lista de tuplas (inicio, fim) de cada burst de execução
        self.foi_executada = False       # Flag para controle do tempo_inicio_execucao

    def __str__(self):
        return f"Tarefa {self.nome} (Prioridade {self.prioridade}): {self.duracao} segundos"

    def executar(self, quantum):
        """Executa a tarefa por um tempo de 'quantum' ou até terminar"""
        tempo_exec = min(self.tempo_restante, quantum)
        self.tempo_restante -= tempo_exec
        return tempo_exec

# Cada processo tem um nome, um tempo total de execução (tempo_execucao),
# e um tempo restante (tempo_restante), que é decrementado conforme o processo vai sendo executado.
# O método executar(quantum) executa o processo por uma quantidade limitada de tempo (quantum) ou até ele terminar.


# Classe abstrata de Escalonador
class EscalonadorCAV(ABC):
    SOBRECARGA_BASE = 0.1  # Exemplo: 0.1 segundos por troca de contexto

    def __init__(self):
        self.tarefas = []
        self.sobrecarga_total = 0  # Sobrecarga total acumulada
        self.turnaround_total = 0  # Contador de turnos para escalonamento 

    def adicionar_tarefa(self, tarefa):
        """Adiciona uma tarefa (ação do CAV) à lista de tarefas"""
        self.tarefas.append(tarefa)

    @abstractmethod
    def escalonar(self):
        """Método que será implementado pelos alunos para o algoritmo de escalonamento"""
        pass

    def registrar_sobrecarga(self, tempo):
        """Adiciona tempo de sobrecarga ao total"""
        self.sobrecarga_total += tempo
        
    def exibir_sobrecarga(self):
        """Exibe a sobrecarga total acumulada"""
        print(f"Sobrecarga total acumulada: {self.sobrecarga_total} segundos.\n")

    def registrar_turnaround(self, tempo_chegada, tempo_final):
        """Registra o turnaround time de uma tarefa"""
        # Turnaround time = tempo_final - tempo_chegada
        turnaround = (tempo_final - tempo_chegada)/len(self.tarefas)
        self.turnaround_total += turnaround
        print(f"Turnaround time para a tarefa: {turnaround} segundos.")

    def exibir_turnaround(self):
        """Exibe o turnaround total acumulado"""
        print(f"Turnaround total acumulado: {self.turnaround_total} segundos.\n")

# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).


class EscalonadorFIFO(EscalonadorCAV):
    def escalonar(self):
        """Escalonamento FIFO para veículos autônomos"""
        tempo_inicial = 0
        for tarefa in self.tarefas:
            tarefa.tempo_inicio = tempo_inicial
            tempo_inicial += tarefa.duracao
            tarefa.tempo_final = tempo_inicial
            print(f"Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos.")
            time.sleep(tarefa.duracao)  # Simula a execução da tarefa

            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            #self.registrar_sobrecarga(0.5)  # 0.5 segundos de sobrecarga por tarefa (simulando troca de contexto)
            self.registrar_turnaround(tarefa.tempo_inicio, tarefa.tempo_final)
            print(f"Tarefa {tarefa.nome} finalizada.\n")

        self.exibir_sobrecarga()
        self.exibir_turnaround()

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.


class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        """Escalonamento Round Robin com tarefas de CAVs"""
        fila = deque(self.tarefas)
        tempo_inicial = 0
        while fila:
            tarefa = fila.popleft()
            if tarefa.tempo_restante > 0:
                tarefa.tempo_inicio = tempo_inicial
                tempo_exec = min(tarefa.tempo_restante, self.quantum)
                tarefa.tempo_restante -= tempo_exec
                tempo_inicial += tempo_exec
                print(f"Executando tarefa {tarefa.nome} por {tempo_exec} segundos.")
                time.sleep(tempo_exec)  # Simula a execução da tarefa

                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                self.registrar_sobrecarga(self.SOBRECARGA_BASE)  # 0.1 segundos de sobrecarga por tarefa
                if tarefa.tempo_restante > 0:
                    fila.append(tarefa)  # Coloca a tarefa de volta na fila se não terminar
                tarefa.tempo_final = tempo_inicial
                self.registrar_turnaround(tarefa.tempo_inicio, tarefa.tempo_final)
                print(f"Tarefa {tarefa.nome} finalizada ou ainda pendente.\n")

        self.exibir_sobrecarga()
        self.exibir_turnaround()

# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.


class EscalonadorPrioridade(EscalonadorCAV):
    def escalonar(self):
        """Escalonamento por Prioridade (menor número = maior prioridade)"""
        print("Escalonamento por Prioridade:")
        # Ordena as tarefas pela prioridade
        self.tarefas.sort(key=lambda tarefa: tarefa.prioridade)
        tempo_inicial = 0
        for tarefa in self.tarefas:
            tarefa.tempo_inicio = tempo_inicial
            tempo_inicial += tarefa.duracao
            tarefa.tempo_final = tempo_inicial
            print(f"Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos com prioridade {tarefa.prioridade}.")
            time.sleep(tarefa.duracao)

            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            self.registrar_sobrecarga(self.SOBRECARGA_BASE)  # 0.1 segundos de sobrecarga por tarefa
            self.registrar_turnaround(tarefa.tempo_inicio, tarefa.tempo_final)
            print(f"Tarefa {tarefa.nome} finalizada.\n")

        self.exibir_sobrecarga()
        self.exibir_turnaround()


class CAV:
    def __init__(self, id):
        self.id = id  # Identificador único para cada CAV
        self.tarefas = []  # Lista de tarefas atribuídas a esse CAV

    def adicionar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)

    def executar_tarefas(self, escalonador):
        print(f"CAV {self.id} começando a execução de tarefas...\n")
        escalonador.escalonar()
        print(f"CAV {self.id} terminou todas as suas tarefas.\n")


# Função para criar algumas tarefas fictícias
def criar_tarefas():
    tarefas = [
        TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), prioridade=1),
        TarefaCAV("Planejamento de Rota", random.randint(3, 6), prioridade=2),
        TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), prioridade=3),
        TarefaCAV("Comunicando com Infraestrutura", random.randint(4, 7), prioridade=1)
    ]
    return tarefas


# Exemplo de uso
if __name__ == "__main__":
    # Criar algumas tarefas fictícias
    tarefas = criar_tarefas()

    # Criar um CAV
    cav = CAV(id=1)
    for t in tarefas:
        cav.adicionar_tarefa(t)

    # Criar um escalonador FIFO
    print("Simulando CAV com FIFO:\n")
    escalonador_fifo = EscalonadorFIFO()
    for t in tarefas:
        escalonador_fifo.adicionar_tarefa(t)

    simulador_fifo = CAV(id=1)
    simulador_fifo.executar_tarefas(escalonador_fifo)

    # Criar um escalonador Round Robin com quantum de 3 segundos
    print("\nSimulando CAV com Round Robin:\n")
    escalonador_rr = EscalonadorRoundRobin(quantum=3)
    for t in tarefas:
        escalonador_rr.adicionar_tarefa(t)

    simulador_rr = CAV(id=1)
    simulador_rr.executar_tarefas(escalonador_rr)

    # Criar um escalonador por Prioridade
    print("\nSimulando CAV com Escalonamento por Prioridade:\n")
    escalonador_prio = EscalonadorPrioridade()
    for t in tarefas:
        escalonador_prio.adicionar_tarefa(t)

    simulador_prio = CAV(id=1)
    simulador_prio.executar_tarefas(escalonador_prio)
