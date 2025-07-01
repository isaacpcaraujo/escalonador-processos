import random
import copy
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
    # Definimos SOBRECARGA_BASE como um atributo de classe
    # para consistência entre os escalonadores.
    SOBRECARGA_BASE = 0.1  # Exemplo: 0.1 segundos por troca de contexto

    def __init__(self, tarefas_iniciais):
        self.tarefas_originais = copy.deepcopy(tarefas_iniciais)
        self.tarefas_para_escalonar = []
        self.sobrecarga_total = 0  # Sobrecarga total acumulada
        self.tempos_de_turnaround = [] # Armazenamento dos tempos de turnaround
        self.tempos_de_espera = [] # Armazenamento dos tempos de espera
        self.tempos_de_resposta = [] # Armazenamento dos tempos de resposta
        
    def _resetar_estado_simulacao(self):
        """
        Reinicia o estado das tarefas e métricas para uma nova simulação.
        Deve ser chamado no início de cada método 'escalonar' das subclasses.
        """
        self.tarefas_para_escalonar = copy.deepcopy(self.tarefas_originais)
        self.sobrecarga_total = 0
        self.tempos_de_turnaround = []

    def adicionar_tarefa(self, tarefa):
        """Adiciona uma tarefa (ação do CAV) à lista de tarefas"""
        self.tarefas.append(tarefa)

    @abstractmethod
    def escalonar(self):
        """Método que será implementado pelos alunos para o algoritmo de escalonamento"""
        pass

    def registrar_sobrecarga(self, tempo=None):
        """
        Adiciona tempo de sobrecarga ao total. Se 'tempo' não for fornecido,
        usa a SOBRECARGA_BASE padrão.
        """
        if tempo is None:
            tempo = self.SOBRECARGA_BASE

        self.sobrecarga_total += tempo
        
    def calcular_e_exibir_metricas(self):
        """
        Calcula e exibe o tempo de turnaround médio e a sobrecarga total
        para a simulação.
        """
        if not self.tarefas_para_escalonar:
            print("Nenhuma tarefa para calcular métricas.")
            return

        print("\n--- Resultados da Simulação ---")
        for tarefa in self.tarefas_para_escalonar:
            if tarefa.tempo_conclusao != -1: # Calcula apenas para tarefas que foram concluídas
                turnaround = tarefa.tempo_conclusao - tarefa.tempo_chegada
                self.tempos_de_turnaround.append(turnaround)
                print(f"  - Tarefa '{tarefa.nome}':")
                print(f"    - Chegada: {tarefa.tempo_chegada:.2f}s, Conclusão: {tarefa.tempo_conclusao:.2f}s")
                print(f"    - Tempo de Turnaround: {turnaround:.2f}s")
            else:
                print(f"  - Tarefa '{tarefa.nome}' não foi concluída.")


        if self.tempos_de_turnaround:
            avg_turnaround = sum(self.tempos_de_turnaround) / len(self.tempos_de_turnaround)
            print(f"**Turnaround Médio**: {avg_turnaround:.2f} segundos.")
        else:
            print("**Turnaround Médio**: N/A (Nenhuma tarefa concluída).")

        print(f"**Sobrecarga Total Acumulada**: {self.sobrecarga_total:.2f} segundos.")
        print("------------------------------\n")


# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).


class EscalonadorFIFO(EscalonadorCAV):

    def __init__(self, tarefas_iniciais):
        super().__init__(tarefas_iniciais) # passa a lista de tarefas para a classe base.

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
