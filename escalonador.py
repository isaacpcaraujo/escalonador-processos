import copy
from collections import deque
from abc import ABC, abstractmethod
import csv
import os

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

    def salvar_metricas_csv(self, nome_arquivo="metricas_escalonamento.csv"):
        if not self.tarefas_para_escalonar:
            print("Nenhuma tarefa para salvar métricas.")
            return

        caminho_completo = os.path.join(os.getcwd(), nome_arquivo)

        with open(caminho_completo, mode='w', newline='') as arquivo_csv:
            writer = csv.writer(arquivo_csv)
            
            # Cabeçalho
            writer.writerow([
                "Nome da Tarefa", "Tempo de Chegada", "Tempo de Conclusão",
                "Tempo de Turnaround", "Prioridade", "Deadline", "Deadline Perdido?"
            ])

            for tarefa in self.tarefas_para_escalonar:
                if tarefa.tempo_final != -1:
                    turnaround = tarefa.tempo_final - tarefa.tempo_chegada
                    deadline_perdido = (
                        "Sim" if tarefa.deadline is not None and tarefa.tempo_final > tarefa.deadline else "Não"
                    )
                    writer.writerow([
                        tarefa.nome,
                        f"{tarefa.tempo_chegada:.2f}",
                        f"{tarefa.tempo_final:.2f}",
                        f"{turnaround:.2f}",
                        f"{tarefa.prioridade}",
                        f"{tarefa.deadline:.2f}" if tarefa.deadline is not None else "N/A",
                        deadline_perdido
                    ])
                else:
                    writer.writerow([
                        tarefa.nome,
                        f"{tarefa.tempo_chegada:.2f}",
                        "Não concluída",
                        "N/A",
                        f"{tarefa.prioridade}",
                        f"{tarefa.deadline:.2f}" if tarefa.deadline is not None else "N/A",
                        "Sim"  # Considera deadline perdido se nem foi concluída
                    ])
            
            # Linha em branco
            writer.writerow([])

            # Métricas agregadas
            avg_turnaround = (
                sum(self.tempos_de_turnaround) / len(self.tempos_de_turnaround)
                if self.tempos_de_turnaround else 0
            )

            writer.writerow(["Métricas Finais"])
            writer.writerow(["Turnaround Médio (s)", f"{avg_turnaround:.2f}"])
            writer.writerow(["Sobrecarga Total (s)", f"{self.sobrecarga_total:.2f}"])
            writer.writerow(["Total de Deadlines Perdidos", self.deadlines_perdidos])

        print(f"\n Métricas salvas em: {caminho_completo}")

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
        print(self.tarefas_para_escalonar)    

class EscalonadorSJF(EscalonadorCAV):
    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento SJF ---")
        self.tarefas_para_escalonar.sort(key=lambda tarefa: tarefa.duracao)
        tempo_atual_simulacao = 0
        fila = [tarefa for tarefa in self.tarefas_para_escalonar if tarefa.tempo_chegada <= tempo_atual_simulacao]
        fila.sort(key=lambda t: t.duracao)
        for _ in range(len(self.tarefas_para_escalonar)):
            tarefa = fila[0]
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando tarefa {tarefa.nome}...")
            inicio_exec = tempo_atual_simulacao
            tempo_atual_simulacao += tarefa.duracao
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            tarefa.tempo_final = tempo_atual_simulacao
            tarefa.tempo_restante = 0
            tarefa.foi_executada = True
            print(f"Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")
            fila = [tarefa for tarefa in self.tarefas_para_escalonar if tarefa.tempo_chegada <= tempo_atual_simulacao and not tarefa.foi_executada]
            fila.sort(key=lambda t: t.duracao)

class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum, tarefas_iniciais):
        super().__init__(tarefas_iniciais)
        self.quantum = quantum

    def escalonar(self):
        self.resetar_estado_simulacao()
        print(f"--- Escalonamento Round Robin (Quantum: {self.quantum}s) ---")
        tempo_atual_simulacao = 0
        fila = [tarefa for tarefa in self.tarefas_para_escalonar if tarefa.tempo_chegada <= tempo_atual_simulacao and not tarefa.foi_executada]
        while fila:
            tarefa = fila.pop(0)
            inicio_exec = tempo_atual_simulacao
            tempo_exec = min(tarefa.tempo_restante, self.quantum)
            tarefa.tempo_restante -= tempo_exec
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa.nome} por {tempo_exec:.2f}s.")
            tempo_atual_simulacao += tempo_exec
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            for t in self.tarefas_para_escalonar:
                if not t in fila and inicio_exec <= t.tempo_chegada <= tempo_atual_simulacao and t != tarefa:
                    fila.append(t)
            if tarefa.tempo_restante > 0 and not tarefa in fila:
                fila.append(tarefa)
                self.registrar_sobrecarga()
            else:
                tarefa.tempo_final = tempo_atual_simulacao
                tarefa.foi_executada = True
                print(f"-> Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")

class EscalonadorPrioridade(EscalonadorCAV):
    def __init__(self, tarefas_iniciais,quantum):
        super().__init__(tarefas_iniciais)
        self.quantum = quantum

    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento por Prioridade ---")
        tempo_atual_simulacao = 0
        fila = [tarefa for tarefa in self.tarefas_para_escalonar if tarefa.tempo_chegada <= tempo_atual_simulacao and not tarefa.foi_executada]
        while fila:
            tarefa = fila.pop(0)
            inicio_exec = tempo_atual_simulacao
            tempo_exec = min(tarefa.tempo_restante, self.quantum)
            tarefa.tempo_restante -= tempo_exec
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa.nome} por {tempo_exec:.2f}s.")
            tempo_atual_simulacao += tempo_exec
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            for t in self.tarefas_para_escalonar:
                if not t in fila and inicio_exec <= t.tempo_chegada <= tempo_atual_simulacao and t != tarefa:
                    fila.append(t)
                    fila.sort(key=lambda t: t.prioridade)
            if tarefa.tempo_restante > 0 and not tarefa in fila:
                fila.append(tarefa)
                fila.sort(key=lambda t: t.prioridade)
                self.registrar_sobrecarga()

            else:
                tarefa.tempo_final = tempo_atual_simulacao
                tarefa.foi_executada = True
                print(f"-> Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")

class EscalonadorEDF(EscalonadorCAV):
    def __init__(self, tarefas_iniciais, quantum=1):
        super().__init__(tarefas_iniciais)
        self.quantum = quantum

    def escalonar(self):
        self.resetar_estado_simulacao()
        print(f"--- Escalonamento EDF (Quantum: {self.quantum}s) ---")
        tempo_atual_simulacao = 0
        tarefas_pendentes = [tarefa for tarefa in self.tarefas_para_escalonar if tarefa.tempo_chegada <= tempo_atual_simulacao and not tarefa.foi_executada]
        while tarefas_pendentes:
            tarefa_atual = tarefas_pendentes.pop(0)
            inicio_exec = tempo_atual_simulacao
            tempo_exec = min(tarefa_atual.tempo_restante, self.quantum)
            tarefa_atual.tempo_restante -= tempo_exec
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa_atual.nome} por {tempo_exec:.2f}s.")
            tempo_atual_simulacao += tempo_exec
            tarefa_atual.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            for t in self.tarefas_para_escalonar:
                if not t in tarefas_pendentes and inicio_exec <= t.tempo_chegada <= tempo_atual_simulacao and t != tarefa_atual:
                    tarefas_pendentes.append(t)
                    tarefas_pendentes.sort(key=lambda t: t.deadline - tempo_exec)
            if tarefa_atual.tempo_restante > 0 and not tarefa_atual in tarefas_pendentes:
                tarefas_pendentes.append(tarefa_atual)
                tarefas_pendentes.sort(key=lambda t: t.deadline - tempo_exec)
                self.registrar_sobrecarga()
            else:
                tarefa_atual.tempo_final = tempo_atual_simulacao
                print(f"   -> Tarefa {tarefa_atual.nome} finalizada em {tarefa_atual.tempo_final:.2f}s.")
                if tarefa_atual.tempo_final - tarefa_atual.tempo_chegada > tarefa_atual.deadline:
                    print(f"   -> DEADLINE PERDIDO!\n")
                    self.deadlines_perdidos += 1  # Contador incrementado
                else:
                    print(f"   -> Deadline cumprido.\n")

class EscalonadorSRTF(EscalonadorCAV):
    """
    Escalonador Shortest Remaining Time First (SRTF) - Preemptivo.
    A cada instante, seleciona a tarefa com o menor tempo restante para executar.
    """
    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento SRTF (Shortest Remaining Time First) ---")

        tempo_atual_simulacao = 0
        tarefas_concluidas = 0
        total_tarefas = len(self.tarefas_para_escalonar)
        tarefa_em_execucao = None

        while tarefas_concluidas < total_tarefas:
            # Filtra tarefas que já chegaram e ainda não foram concluídas
            fila_prontos = [t for t in self.tarefas_para_escalonar if t.tempo_chegada <= tempo_atual_simulacao and t.tempo_restante > 0]

            if not fila_prontos:
                # Se não há tarefas prontas, avança o tempo para a próxima chegada
                tempo_atual_simulacao += 1
                continue

            # Ordena a fila de prontos pelo menor tempo restante
            fila_prontos.sort(key=lambda t: t.tempo_restante)
            proxima_tarefa = fila_prontos[0]

            # Lógica de preempção e troca de contexto
            if tarefa_em_execucao != proxima_tarefa:
                self.registrar_sobrecarga()
                tarefa_em_execucao = proxima_tarefa
                print(f"Tempo: {tempo_atual_simulacao:.2f}s - Assumindo tarefa {tarefa_em_execucao.nome} (Restante: {tarefa_em_execucao.tempo_restante:.2f}s)")

            # Executa a tarefa por uma unidade de tempo
            inicio_burst = tempo_atual_simulacao
            tarefa_em_execucao.tempo_restante -= 1
            tempo_atual_simulacao += 1
            
            # Registra o burst de execução (mesmo que seja de 1s)
            # Para o Gantt, podemos otimizar depois, mas vamos registrar tudo por enquanto
            if not tarefa_em_execucao.tempos_execucao or tarefa_em_execucao.tempos_execucao[-1][1] != inicio_burst:
                tarefa_em_execucao.tempos_execucao.append([inicio_burst, tempo_atual_simulacao])
            else: # Estende o burst anterior
                tarefa_em_execucao.tempos_execucao[-1][1] = tempo_atual_simulacao


            # Verifica se a tarefa terminou
            if tarefa_em_execucao.tempo_restante <= 0:
                tarefa_em_execucao.tempo_final = tempo_atual_simulacao
                tarefas_concluidas += 1
                tarefa_em_execucao = None # Limpa a tarefa em execução
                print(f"-> Tarefa {proxima_tarefa.nome} finalizada em {proxima_tarefa.tempo_final:.2f}s.\n")
                if proxima_tarefa.tempo_final - proxima_tarefa.tempo_chegada > proxima_tarefa.deadline:
                    self.deadlines_perdidos += 1

class EscalonadorRoundRobinDinamico(EscalonadorCAV):
    """
    Escalonador Round Robin com Quantum Dinâmico baseado na prioridade.
    Tarefas de maior prioridade (menor número) recebem um quantum maior.
    """
    def __init__(self, quantum_base, tarefas_iniciais):
        super().__init__(tarefas_iniciais)
        self.quantum_base = quantum_base

    def escalonar(self):
        self.resetar_estado_simulacao()
        print(f"--- Escalonamento Round Robin com Quantum Dinâmico (Base: {self.quantum_base}s) ---")
        
        if not self.tarefas_para_escalonar:
            return

        # Encontra a prioridade máxima (menor número) para o cálculo
        prioridade_max = max(t.prioridade for t in self.tarefas_para_escalonar)
        
        tempo_atual_simulacao = 0
        fila = [tarefa for tarefa in self.tarefas_para_escalonar if tarefa.tempo_chegada <= tempo_atual_simulacao and not tarefa.foi_executada]
        while fila:
            tarefa = fila.pop(0)
            quantum_dinamico = self.quantum_base + (prioridade_max - tarefa.prioridade)
            inicio_exec = tempo_atual_simulacao
            tempo_exec = min(tarefa.tempo_restante, quantum_dinamico)
            tarefa.tempo_restante -= tempo_exec
            print(f"Tempo: {tempo_atual_simulacao:.2f}s - Executando {tarefa.nome} por {tempo_exec:.2f}s.")
            tempo_atual_simulacao += tempo_exec
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            for t in self.tarefas_para_escalonar:
                if not t in fila and inicio_exec <= t.tempo_chegada <= tempo_atual_simulacao and t != tarefa:
                    fila.append(t)
            if tarefa.tempo_restante > 0 and not tarefa in fila:
                fila.append(tarefa)
                self.registrar_sobrecarga()
            else:
                tarefa.tempo_final = tempo_atual_simulacao
                tarefa.foi_executada = True
                print(f"-> Tarefa {tarefa.nome} finalizada em {tarefa.tempo_final:.2f}s.\n")