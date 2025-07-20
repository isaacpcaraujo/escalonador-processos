import tkinter as tk
import random
import escalonadorML

# Importa as classes e funções dos outros arquivos do projeto
from tarefa import TarefaCAV
from escalonador import (
    EscalonadorFIFO, 
    EscalonadorSJF, 
    EscalonadorRoundRobin, 
    EscalonadorPrioridade, 
    EscalonadorEDF
)
from escalonadorML import (
    EscalonadorML
)
from visualizacao import visualizar_gantt

class App:
    def __init__(self):
        """Construtor da nossa classe de interface gráfica."""
        # Cria a janela raiz (principal)
        self.root = tk.Tk()
        self.root.title("Simulador de Escalonamento de Tarefas CAV")
        self.root.geometry("400x320")

        # Variáveis de estado da aplicação
        self.tarefas_base = []
        self.escalonador_fifo = None
        self.escalonador_sjf = None
        self.escalonador_rr = None
        self.escalonador_prio = None
        self.escalonador_edf = None
        self.escalonador_ml = None
        self.modelo_decision_tree = None

        # Cria os componentes da interface
        self._criar_widgets()

        # Inicia com um conjunto de tarefas aleatórias
        self.redefinir_tarefas()

    def _criar_widgets(self):
        """Cria e organiza todos os componentes (widgets) na janela."""
        label = tk.Label(self.root, text="Escolha um algoritmo para simular:", pady=10)
        label.pack()

        # Botão para gerar novas tarefas
        #btn_reset = tk.Button(self.root, text="Gerar Novas Tarefas", command=self.redefinir_tarefas)
        #btn_reset.pack(pady=5)
        
        # Linha separadora
        tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=10)

        # Botões para cada simulador
        btn_fifo = tk.Button(self.root, text="Simular com FIFO", command=lambda: visualizar_gantt(self.root, self.escalonador_fifo, "FIFO"))
        btn_fifo.pack(pady=2, fill=tk.X, padx=20)

        btn_sjf = tk.Button(self.root, text="Simular com SJF", command=lambda: visualizar_gantt(self.root, self.escalonador_sjf, "Shortest Job First (SJF)"))
        btn_sjf.pack(pady=2, fill=tk.X, padx=20)

        btn_rr = tk.Button(self.root, text="Simular com Round Robin (Q=3)", command=lambda: visualizar_gantt(self.root, self.escalonador_rr, "Round Robin"))
        btn_rr.pack(pady=2, fill=tk.X, padx=20)

        btn_prio = tk.Button(self.root, text="Simular com Prioridade", command=lambda: visualizar_gantt(self.root, self.escalonador_prio, "Prioridade"))
        btn_prio.pack(pady=2, fill=tk.X, padx=20)
        
        btn_edf = tk.Button(self.root, text="Simular com EDF (Q=2)", command=lambda: visualizar_gantt(self.root, self.escalonador_edf, "Earliest Deadline First (EDF)"))
        btn_edf.pack(pady=2, fill=tk.X, padx=20)

        btn_edf = tk.Button(self.root, text="Simular com Escalonador ML (Q=2)", command=lambda: visualizar_gantt(self.root, self.escalonador_ml, "Decision Tree Model"))
        btn_edf.pack(pady=2, fill=tk.X, padx=20)
    
    def _criar_tarefas(self):
        """Método privado para gerar uma lista de tarefas aleatórias."""
        return [
            TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), deadline=random.randint(15, 25), prioridade=1),
            TarefaCAV("Planejamento de Rota", random.randint(3, 6), deadline=random.randint(10, 20), prioridade=2),
            TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), deadline=random.randint(8, 15), prioridade=3),
            TarefaCAV("Com. com Infraestrutura", random.randint(4, 7), deadline=random.randint(12, 18), prioridade=1)
        ]

    def redefinir_tarefas(self):
        """Gera um novo conjunto de tarefas e recria as instâncias dos escalonadores."""
        print("--- Novas tarefas geradas! ---")
        self.tarefas_base = self._criar_tarefas()
        
        self.modelo_decision_tree = escalonadorML.treinar_modelo_decision_tree()

        # Recria as instâncias dos escalonadores com as novas tarefas
        self.escalonador_fifo = EscalonadorFIFO(tarefas_iniciais=self.tarefas_base)
        self.escalonador_sjf = EscalonadorSJF(tarefas_iniciais=self.tarefas_base)
        self.escalonador_rr = EscalonadorRoundRobin(quantum=2, tarefas_iniciais=self.tarefas_base)
        self.escalonador_prio = EscalonadorPrioridade(tarefas_iniciais=self.tarefas_base)
        self.escalonador_edf = EscalonadorEDF(tarefas_iniciais=self.tarefas_base, quantum=2)
        self.escalonador_ml = EscalonadorML(tarefas_iniciais=self.tarefas_base, modelo=self.modelo_decision_tree, quantum=2)

    def iniciar(self):
        """Inicia o loop principal do Tkinter."""
        self.root.mainloop()