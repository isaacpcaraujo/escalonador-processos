import copy
from collections import deque
from abc import ABC, abstractmethod

# Importa a classe TarefaCAV do arquivo tarefa.py
from tarefa import TarefaCAV

# --- CLASSE ABSTRATA DE ESCALONADOR ---
class EscalonadorCAV(ABC):
    SOBRECARGA_BASE = 0.1

    def __init__(self, tarefas_iniciais):
        self.tarefas_originais = copy.deepcopy(tarefas_iniciais)
        self.tarefas_para_escalonar = []
        self.sobrecarga_total = 0
        self.tempos_de_turnaround = []
        self.deadlines_perdidos = 0  # Adicionado

    def resetar_estado_simulacao(self):
        self.tarefas_para_escalonar = copy.deepcopy(self.tarefas_originais)
        self.sobrecarga_total = 0
        self.tempos_de_turnaround = []
        self.deadlines_perdidos = 0  # Adicionado

    @abstractmethod
    def escalonar(self):
        pass

    def registrar_sobrecarga(self, tempo=None):
        if tempo is None:
            tempo = self.SOBRECARGA_BASE
        self.sobrecarga_total += tempo

    def calcular_e_exibir_metricas(self):
        if not self.tarefas_para_escalonar:
            print("Nenhuma tarefa para calcular métricas.")
            return

        print("\n--- Resultados da Simulação ---")
        for tarefa in self.tarefas_para_escalonar:
            if tarefa.tempo_final != -1:
                turnaround = tarefa.tempo_final - tarefa.tempo_chegada
                self.tempos_de_turnaround.append(turnaround)
                print(f"   - Tarefa '{tarefa.nome}':")
                print(f"     - Chegada: {tarefa.tempo_chegada:.2f}s, Conclusão: {tarefa.tempo_final:.2f}s")
                print(f"     - Tempo de Turnaround: {turnaround:.2f}s")
            else:
                print(f"   - Tarefa '{tarefa.nome}' não foi concluída.")

        if self.tempos_de_turnaround:
            avg_turnaround = sum(self.tempos_de_turnaround) / len(self.tempos_de_turnaround)
            print(f"**Turnaround Médio**: {avg_turnaround:.2f} segundos.")
        else:
            print("**Turnaround Médio**: N/A (Nenhuma tarefa concluída).")

        print(f"**Sobrecarga Total Acumulada**: {self.sobrecarga_total:.2f} segundos.")
        print(f"**Deadlines Perdidos**: {self.deadlines_perdidos}")  # Adicionado
        print("------------------------------\n")

# --- IMPLEMENTAÇÕES DOS ESCALONADORES ---

class EscalonadorFIFO(EscalonadorCAV):
    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento FIFO ---")
        tempo_atual_simulacao = 0
        for tarefa in self.tarefas_para_escalonar:
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa.nome}...")
            inicio_exec = tempo_atual_simulacao
            tempo_atual_simulacao += tarefa.duracao
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            tarefa.tempo_final = tempo_atual_simulacao
            tarefa.tempo_restante = 0
            print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")

class EscalonadorSJF(EscalonadorCAV):
    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento SJF ---")
        self.tarefas_para_escalonar.sort(key=lambda tarefa: tarefa.duracao)
        tempo_atual_simulacao = 0
        for tarefa in self.tarefas_para_escalonar:
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa.nome}...")
            inicio_exec = tempo_atual_simulacao
            tempo_atual_simulacao += tarefa.duracao
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            tarefa.tempo_final = tempo_atual_simulacao
            tarefa.tempo_restante = 0
            print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")

class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum, tarefas_iniciais):
        super().__init__(tarefas_iniciais)
        self.quantum = quantum

    def escalonar(self):
        self.resetar_estado_simulacao()
        print(f"--- Escalonamento Round Robin (Quantum: {self.quantum}s) ---")
        fila = deque(self.tarefas_para_escalonar)
        tempo_atual_simulacao = 0
        while fila:
            tarefa = fila.popleft()
            self.registrar_sobrecarga()
            inicio_exec = tempo_atual_simulacao
            tempo_exec = min(tarefa.tempo_restante, self.quantum)
            tarefa.tempo_restante -= tempo_exec
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa.nome} por {tempo_exec:.2f}s.")
            tempo_atual_simulacao += tempo_exec
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            if tarefa.tempo_restante > 0:
                fila.append(tarefa)
            else:
                tarefa.tempo_final = tempo_atual_simulacao
                print(f"-> Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")

class EscalonadorPrioridade(EscalonadorCAV):
    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento por Prioridade ---")
        self.tarefas_para_escalonar.sort(key=lambda tarefa: tarefa.prioridade)
        tempo_atual_simulacao = 0
        for tarefa in self.tarefas_para_escalonar:
            self.registrar_sobrecarga()
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa.nome}...")
            inicio_exec = tempo_atual_simulacao
            tempo_atual_simulacao += tarefa.duracao
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            tarefa.tempo_final = tempo_atual_simulacao
            tarefa.tempo_restante = 0
            print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")

class EscalonadorEDF(EscalonadorCAV):
    def __init__(self, tarefas_iniciais, quantum=1):
        super().__init__(tarefas_iniciais)
        self.quantum = quantum

    def escalonar(self):
        self.resetar_estado_simulacao()
        print(f"--- Escalonamento EDF (Quantum: {self.quantum}s) ---")
        tarefas_pendentes = list(self.tarefas_para_escalonar)
        tempo_atual_simulacao = 0
        while tarefas_pendentes:
            tarefas_pendentes.sort(key=lambda tarefa: tarefa.deadline)
            tarefa_atual = tarefas_pendentes[0]
            self.registrar_sobrecarga()
            inicio_exec = tempo_atual_simulacao
            tempo_exec = min(tarefa_atual.tempo_restante, self.quantum)
            tarefa_atual.tempo_restante -= tempo_exec
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa_atual.nome} por {tempo_exec:.2f}s.")
            tempo_atual_simulacao += tempo_exec
            tarefa_atual.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            if tarefa_atual.tempo_restante <= 0:
                tarefa_atual.tempo_final = tempo_atual_simulacao
                tarefas_pendentes.remove(tarefa_atual)
                print(f"   -> Tarefa {tarefa_atual.nome} finalizada em {tarefa_atual.tempo_final:.2f}s.")
                if tarefa_atual.tempo_final > tarefa_atual.deadline:
                    print(f"   -> DEADLINE PERDIDO!\n")
                    self.deadlines_perdidos += 1  # Contador incrementado
                else:
                    print(f"   -> Deadline cumprido.\n")
