import pandas as pd
import random
from sklearn.tree import DecisionTreeClassifier
from tarefa import TarefaCAV
from escalonador import EscalonadorCAV

# --- Escalonador com ML supervisionado ---
class EscalonadorML(EscalonadorCAV):
    def __init__(self, tarefas_iniciais, modelo):
        super().__init__(tarefas_iniciais)
        self.modelo = modelo

    def escolher_tarefa(self, tempo_atual, tarefas_disponiveis):
        if not tarefas_disponiveis:
            return None

        entradas = pd.DataFrame([
            [t.duracao, t.prioridade, t.tempo_chegada, t.deadline, tempo_atual]
            for t in tarefas_disponiveis
        ], columns=["duracao", "prioridade", "tempo_chegada", "deadline", "tempo_atual"])

        probabilidades = self.modelo.predict_proba(entradas)
        escolhida = max(zip(tarefas_disponiveis, probabilidades), key=lambda x: x[1][1])[0]
        return escolhida


    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento com ML supervisionado ---")

        tempo_atual_simulacao = 0
        tarefas_pendentes = list(self.tarefas_para_escalonar)

        while any(t.tempo_restante > 0 for t in tarefas_pendentes):
            disponiveis = [t for t in tarefas_pendentes if t.tempo_restante > 0 and t.tempo_chegada <= tempo_atual_simulacao]

            if not disponiveis:
                tempo_atual_simulacao += 1
                continue

            tarefa = self.escolher_tarefa(tempo_atual_simulacao, disponiveis)
            self.registrar_sobrecarga()

            inicio_exec = tempo_atual_simulacao
            tempo_exec = tarefa.tempo_restante  # Executa até o fim
            tempo_atual_simulacao += tempo_exec

            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            tarefa.tempo_final = tempo_atual_simulacao
            tarefa.tempo_restante = 0

            print(f"Tempo: {inicio_exec:.2f}s - Executou {tarefa.nome} até {tempo_atual_simulacao:.2f}s.")

        self.calcular_e_exibir_metricas()
        self.v


# --- Função para gerar dados de treinamento supervisionado ---
def gerar_dataset_supervisionado(n_amostras=500):
    data = []
    for _ in range(n_amostras):
        tarefas = []
        for i in range(3):
            tarefas.append(TarefaCAV(
                nome=f"T{i}",
                duracao=random.randint(1, 10),
                prioridade=random.randint(1, 5),
                tempo_chegada=random.randint(0, 10),
                deadline=random.randint(10, 30)
            ))

        tempo_atual = min(t.tempo_chegada for t in tarefas)
        candidatas = [t for t in tarefas if t.tempo_chegada <= tempo_atual]
        if not candidatas:
            continue

        # Algoritmo de referência: SJF
        escolhida = min(candidatas, key=lambda t: t.duracao)

        for t in tarefas:
            data.append({
                "duracao": t.duracao,
                "prioridade": t.prioridade,
                "tempo_chegada": t.tempo_chegada,
                "deadline": t.deadline,
                "tempo_atual": tempo_atual,
                "escolhida": int(t.nome == escolhida.nome)
            })

    df = pd.DataFrame(data)
    return df


# --- Treinamento do modelo ---
def treinar_modelo_decision_tree():
    df = gerar_dataset_supervisionado()
    X = df[["duracao", "prioridade", "tempo_chegada", "deadline", "tempo_atual"]]
    y = df["escolhida"]
    modelo = DecisionTreeClassifier()
    modelo.fit(X, y)
    return modelo


# --- Exemplo de execução ---
if __name__ == "__main__":
    modelo = treinar_modelo_decision_tree()

    tarefas = [
        TarefaCAV("A", duracao=4, prioridade=2, tempo_chegada=0, deadline=15),
        TarefaCAV("B", duracao=3, prioridade=1, tempo_chegada=1, deadline=10),
        TarefaCAV("C", duracao=6, prioridade=3, tempo_chegada=2, deadline=20)
    ]

    escalonador = EscalonadorML(tarefas, modelo)
    escalonador.escalonar()