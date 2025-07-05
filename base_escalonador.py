import random
import copy
import time
from collections import deque
from abc import ABC, abstractmethod

#Atual

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.

class TarefaCAV:
    def __init__(self, nome, duracao, prioridade=1, tempo_chegada=0, deadline=0):
        self.nome = nome
        self.duracao = duracao
        self.prioridade = prioridade
        self.deadline = deadline
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
        
    def resetar_estado_simulacao(self):
        """
        Reinicia o estado das tarefas e métricas para uma nova simulação.
        Deve ser chamado no início de cada método 'escalonar' das subclasses.
        """
        self.tarefas_para_escalonar = copy.deepcopy(self.tarefas_originais)
        self.sobrecarga_total = 0
        self.tempos_de_turnaround = []

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

        self.resetar_estado_simulacao() # Resetar estado no início
        print("--- Escalonamento FIFO ---")
        tempo_atual_simulacao = 0 # Inicializa o relógio da simulação

        for tarefa in self.tarefas_para_escalonar: # Usa a lista de tarefas resetada
            # Registrar sobrecarga antes de iniciar a tarefa (custo de "carregar" a tarefa)
            # self.registrar_sobrecarga() # OPCIONAL: Descomente se quiser simular a sobrecarga antes de cada tarefa

            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa.nome} (Duração: {tarefa.duracao}s)...")
            # time.sleep(tarefa.duracao)  # OPCIONAL: Simula a execução da tarefa (descomente se quiser simular o tempo de execução real)

            tempo_atual_simulacao += tarefa.duracao
            tarefa.tempo_conclusao = tempo_atual_simulacao # Marca o tempo de conclusão
            tarefa.tempo_restante = 0 # Garante que a tarefa está marcada como concluída

            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_conclusao:.2f}s.\n")

        self.calcular_e_exibir_metricas() # Calcula e exibe as métricas no final

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.


class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum, tarefas_iniciais):
        super().__init__(tarefas_iniciais)
        self.quantum = quantum

    def escalonar(self):
        """Escalonamento Round Robin com tarefas de CAVs"""

        self.resetar_estado_simulacao()  # Resetar estado no início
        print(f"--- Escalonamento Round Robin (Quantum: {self.quantum} segundos) ---")
        fila = deque(self.tarefas_para_escalonar)
        tempo_atual_simulacao = 0 # Inicializa o relógio da simulação
        
        while fila:
            tarefa = fila.popleft()

            # Registra sobrecarga cada vez que uma tarefa é executada
            self.registrar_sobrecarga()

            tempo_exec = min(tarefa.tempo_restante, self.quantum)
            tarefa.tempo_restante -= tempo_exec

            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa.nome} (Restante: {tarefa.duracao - tarefa.tempo_restante:.2f}/{tarefa.duracao:.2f}s) por {tempo_exec:.2f}s.")
            # time.sleep(tempo_exec) # OPCIONAL: Simula a execução da tarefa (descomente se quiser simular o tempo de execução real)

            tempo_atual_simulacao += tempo_exec


            if tarefa.tempo_restante > 0:
                fila.append(tarefa)  # Coloca a tarefa de volta na fila se não terminar
                print(f"Tarefa {tarefa.nome} ainda pendente, re-adicionada à fila.\n")
            else:
                tarefa.tempo_conclusao = tempo_atual_simulacao # Marca o tempo de conclusão
                print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_conclusao:.2f}s.\n")

        self.calcular_e_exibir_metricas()

# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.


class EscalonadorPrioridade(EscalonadorCAV):
    def __init__(self, tarefas_iniciais):
        super().__init__(tarefas_iniciais)  # Passa a lista de tarefas para a classe base

    def escalonar(self):
        """Escalonamento por Prioridade (menor número = maior prioridade)"""

        self.resetar_estado_simulacao() # Resetar estado no início
        print("--- Escalonamento por Prioridade ---")

        # Ordena as tarefas pela prioridade (não preemptivo)
        self.tarefas_para_escalonar.sort(key=lambda tarefa: tarefa.prioridade)

        tempo_atual_simulacao = 0 # Inicializa o relógio da simulação
        for tarefa in self.tarefas_para_escalonar: # Usa a lista de tarefas resetada
            self.registrar_sobrecarga()

            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa.nome} (Prioridade: {tarefa.prioridade}, Duração: {tarefa.duracao}s)...")
            # time.sleep(tarefa.duracao) # Opcional: Simula a execução da tarefa (descomente se quiser simular o tempo de execução real)

            tempo_atual_simulacao += tarefa.duracao
            tarefa.tempo_conclusao = tempo_atual_simulacao # Marca o tempo de conclusão
            tarefa.tempo_restante = 0 # Garante que a tarefa está marcada como concluída

            print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_conclusao:.2f}s.\n")

        self.calcular_e_exibir_metricas() # Calcula e exibe as métricas no final


class EscalonadorEDF(EscalonadorCAV):
    def __init__(self, tarefas_iniciais, quantum=1):
        super().__init__(tarefas_iniciais)  # Passa a lista de tarefas para a classe base
        self.quantum = quantum  # Quantum para preempção (padrão: 1 segundo)

    def escalonar(self):
        """Escalonamento EDF (Earliest Deadline First) - Preemptivo"""

        self.resetar_estado_simulacao()  # Resetar estado no início
        print(f"--- Escalonamento EDF (Quantum: {self.quantum} segundos) ---")

        # Lista de tarefas ainda não concluídas
        tarefas_pendentes = [t for t in self.tarefas_para_escalonar if t.tempo_restante > 0]
        tempo_atual_simulacao = 0  # Inicializa o relógio da simulação

        while tarefas_pendentes:
            # Ordena as tarefas pendentes por deadline (menor deadline primeiro)
            tarefas_pendentes.sort(key=lambda tarefa: tarefa.deadline)
            
            # Seleciona a tarefa com o deadline mais próximo
            tarefa_atual = tarefas_pendentes[0]

            # Registra sobrecarga por troca de contexto
            self.registrar_sobrecarga()

            # Calcula o tempo de execução para este ciclo
            tempo_exec = min(tarefa_atual.tempo_restante, self.quantum)
            tarefa_atual.tempo_restante -= tempo_exec

            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa_atual.nome}")
            print(f"    - Deadline: {tarefa_atual.deadline:.2f}s")
            print(f"    - Tempo restante: {tarefa_atual.tempo_restante:.2f}s")
            print(f"    - Executando por: {tempo_exec:.2f}s")
            
            # Simula a execução
            tempo_atual_simulacao += tempo_exec

            # Verifica se a tarefa foi concluída
            if tarefa_atual.tempo_restante <= 0:
                tarefa_atual.tempo_conclusao = tempo_atual_simulacao
                tarefas_pendentes.remove(tarefa_atual)  # Remove da lista de pendentes
                print(f"    - ✅ Tarefa {tarefa_atual.nome} finalizada em {tarefa_atual.tempo_conclusao:.2f}s")
                
                # Verifica se perdeu o deadline
                if tarefa_atual.tempo_conclusao > tarefa_atual.deadline:
                    print(f"    - ⚠️  DEADLINE PERDIDO! (Atraso: {tarefa_atual.tempo_conclusao - tarefa_atual.deadline:.2f}s)")
                else:
                    print(f"    - ✅ Deadline cumprido (Folga: {tarefa_atual.deadline - tarefa_atual.tempo_conclusao:.2f}s)")
            else:
                print(f"    - Tarefa {tarefa_atual.nome} preemptada, retornando à fila")
            
            print()  # Linha em branco para separar os ciclos

        self.calcular_e_exibir_metricas()  # Calcula e exibe as métricas no final


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
        TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), deadline=random.randint(15, 25), prioridade=1),
        TarefaCAV("Planejamento de Rota", random.randint(3, 6), deadline=random.randint(10, 20), prioridade=2),
        TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), deadline=random.randint(8, 15), prioridade=3),
        TarefaCAV("Comunicando com Infraestrutura", random.randint(4, 7), deadline=random.randint(12, 18), prioridade=1)
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
    escalonador_fifo = EscalonadorFIFO(tarefas_iniciais=tarefas)  # Passa a lista de tarefas para o escalonador FIFO

    simulador_fifo = CAV(id=1)
    simulador_fifo.executar_tarefas(escalonador_fifo)

    # Criar um escalonador Round Robin com quantum de 3 segundos
    print("\nSimulando CAV com Round Robin:\n")
    escalonador_rr = EscalonadorRoundRobin(quantum=3, tarefas_iniciais=tarefas)  # Passa a lista de tarefas para o escalonador Round Robin

    simulador_rr = CAV(id=1)
    simulador_rr.executar_tarefas(escalonador_rr)

    # Criar um escalonador por Prioridade
    print("\nSimulando CAV com Escalonamento por Prioridade:\n")
    escalonador_prio = EscalonadorPrioridade(tarefas_iniciais=tarefas) # Passa a lista de tarefas para o escalonador por prioridade

    simulador_prio = CAV(id=1)
    simulador_prio.executar_tarefas(escalonador_prio)

    # Criar um escalonador EDF
    print("\nSimulando CAV com Escalonamento EDF:\n")
    escalonador_edf = EscalonadorEDF(tarefas_iniciais=tarefas, quantum=3)  # Quantum de 2 segundos

    simulador_edf = CAV(id=1)
    simulador_edf.executar_tarefas(escalonador_edf)

