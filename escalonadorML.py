import pandas as pd
import random
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from tarefa import TarefaCAV
from escalonador import EscalonadorCAV

# --- Escalonador com ML supervisionado ---
class EscalonadorML(EscalonadorCAV):
    def __init__(self, tarefas_iniciais, modelo, quantum=None):
        super().__init__(tarefas_iniciais)
        self.modelo = modelo
        self.quantum = quantum

    def escolher_tarefa(self, tempo_atual, tarefas_disponiveis):
        if not tarefas_disponiveis:
            return None

        entradas = pd.DataFrame([
            {
                "duracao": t.duracao,
                "prioridade": t.prioridade,
                "tempo_chegada": t.tempo_chegada,
                "deadline": t.deadline,
                "tempo_atual": tempo_atual,
                "slack": t.deadline - tempo_atual - t.duracao,
                "espera": tempo_atual - t.tempo_chegada
            }
            for t in tarefas_disponiveis
        ])

        # Obtém as probabilidades da classe "Escolhida"
        probabilidades = self.modelo.predict_proba(entradas)

        # Escolhe a tarefa com maior probabilidade de ser "escolhida"
        escolhida = max(zip(tarefas_disponiveis, probabilidades), key=lambda x: x[1][1])[0]
        
        return escolhida


    def escalonar(self):
        self.resetar_estado_simulacao()
        print("--- Escalonamento com ML supervisionado ---")

        tempo_atual_simulacao = 0
        tarefas_pendentes = list(self.tarefas_para_escalonar)

        while any(t.tempo_restante > 0 for t in tarefas_pendentes):
            # Filtra tarefas disponíveis no tempo atual
            disponiveis = [t for t in tarefas_pendentes if t.tempo_restante > 0 and t.tempo_chegada <= tempo_atual_simulacao]

            if not disponiveis:
                tempo_atual_simulacao += 1
                continue

            # Escolhe a próxima tarefa usando o modelo
            tarefa = self.escolher_tarefa(tempo_atual_simulacao, disponiveis)
            self.registrar_sobrecarga()

            # Define tempo de execução (com quantum, se houver)
            tempo_exec = tarefa.tempo_restante
            if self.quantum is not None:
                tempo_exec = min(self.quantum, tarefa.tempo_restante)

            inicio_exec = tempo_atual_simulacao
            tempo_atual_simulacao += tempo_exec

            # Atualiza estado da tarefa
            tarefa.tempos_execucao.append((inicio_exec, tempo_atual_simulacao))
            tarefa.tempo_restante -= tempo_exec

            if tarefa.tempo_restante == 0:
                tarefa.tempo_final = tempo_atual_simulacao
                print(f"Tempo: {inicio_exec:.2f}s - Executou {tarefa.nome} até {tempo_atual_simulacao:.2f}s. Finalizada.")
                
                # Verifica deadline
                if tarefa.deadline is not None:
                    if tarefa.tempo_final - tarefa.tempo_chegada > tarefa.deadline :
                        print(f"   -> DEADLINE PERDIDO para {tarefa.nome}!")
                        self.deadlines_perdidos += 1
                    else:
                        print(f"   -> Deadline cumprido para {tarefa.nome}.")
            else:
                print(f"Tempo: {inicio_exec:.2f}s - Executou {tarefa.nome} até {tempo_atual_simulacao:.2f}s. (resta {tarefa.tempo_restante:.2f}s)")

# --- Função para gerar dados de treinamento supervisionado ---
def gerar_dataset_supervisionado(n_amostras=1000, n_tarefas_por_amostra=5):
    data = []

    estrategias = [
        ("SJF", lambda tarefas: min(tarefas, key=lambda t: t.duracao)),
        ("Prioridade", lambda tarefas: max(tarefas, key=lambda t: t.prioridade)),
        ("EDF", lambda tarefas: min(tarefas, key=lambda t: t.deadline)),
    ]

    for _ in range(n_amostras):
        tarefas = []
        for i in range(n_tarefas_por_amostra):
            chegada = random.randint(0, 10)
            duracao = random.randint(1, 10)
            deadline = chegada + duracao + random.randint(5, 20)
            prioridade = random.randint(1, 5)

            tarefas.append(TarefaCAV(
                nome=f"T{i}",
                duracao=duracao,
                prioridade=prioridade,
                tempo_chegada=chegada,
                deadline=deadline
            ))

        tempo_atual = min(t.tempo_chegada for t in tarefas)
        candidatas = [t for t in tarefas if t.tempo_chegada <= tempo_atual]

        if not candidatas:
            continue

        nome_estrategia, estrategia = random.choice(estrategias)
        escolhida = estrategia(candidatas)

        for t in tarefas:
            slack = t.deadline - tempo_atual - t.duracao
            espera = tempo_atual - t.tempo_chegada

            data.append({
                "duracao": t.duracao,
                "prioridade": t.prioridade,
                "tempo_chegada": t.tempo_chegada,
                "deadline": t.deadline,
                "tempo_atual": tempo_atual,
                "slack": slack,
                "espera": espera,
                "algoritmo_origem": nome_estrategia,
                "escolhida": int(t.nome == escolhida.nome)
            })

    df = pd.DataFrame(data)
    return df


def treinar_modelo_decision_tree():
    df = gerar_dataset_supervisionado()

    print("\nExemplo de dados de treino:")
    print(df.head(10))

    X = df[["duracao", "prioridade", "tempo_chegada", "deadline", "tempo_atual", "slack", "espera"]]
    y = df["escolhida"]

    modelo = DecisionTreeClassifier(max_depth=6, class_weight='balanced')
    modelo.fit(X, y)

    acc = modelo.score(X, y)
    print(f"\nAcurácia no dataset gerado: {acc:.2f}")

    # plt.figure(figsize=(15, 6))
    # tree.plot_tree(modelo, feature_names=X.columns, class_names=["Não escolhida", "Escolhida"], filled=True)
    # plt.title("Árvore de Decisão do Escalonador ML")
    # plt.show()

    return modelo


# --- Exemplo de execução ---
if __name__ == "__main__":
    modelo = treinar_modelo_decision_tree()

    tarefas = [
        TarefaCAV("A", duracao=4, prioridade=2, tempo_chegada=0, deadline=15),
        TarefaCAV("B", duracao=3, prioridade=1, tempo_chegada=1, deadline=10),
        TarefaCAV("C", duracao=6, prioridade=3, tempo_chegada=2, deadline=20)
    ]

    escalonador = EscalonadorML(tarefas, modelo, quantum=2)
    escalonador.escalonar()