# arquivo: interface.py

import tkinter as tk
from tkinter import messagebox
import random

# Importa as classes e funções dos outros arquivos do projeto
from tarefa import TarefaCAV
from escalonador import (
    EscalonadorFIFO, 
    EscalonadorSJF, 
    EscalonadorRoundRobin, 
    EscalonadorPrioridade, 
    EscalonadorEDF,
    EscalonadorSRTF,
    EscalonadorRoundRobinDinamico
)
# NOVO: Importa o módulo e a classe do escalonador de ML
import escalonadorML
from escalonadorML import EscalonadorML

from visualizacao import visualizar_gantt

class App:
    def __init__(self):
        """Construtor da nossa classe de interface gráfica."""
        self.root = tk.Tk()
        self.root.title("Simulador de Escalonamento de Tarefas CAV")
        self.root.geometry("450x600") # Aumentamos a altura para os novos botões

        # Variáveis de estado da aplicação
        self.tarefas_base = []
        self.modelo_decision_tree = None # NOVO: Para armazenar o modelo treinado
        self.listbox_tarefas = None

        # Cria os componentes da interface
        self._criar_widgets()

        # Inicia com um conjunto de tarefas e treina o modelo
        self.redefinir_tarefas()

    def _criar_widgets(self):
        """Cria e organiza todos os componentes (widgets) na janela."""
        # --- Frame para gerenciamento de tarefas ---
        frame_gerenciamento = tk.Frame(self.root, pady=10)
        frame_gerenciamento.pack(fill=tk.X, padx=10)

        btn_reset = tk.Button(frame_gerenciamento, text="Treinar Modelo e Gerar Novas Tarefas", command=self.redefinir_tarefas)
        btn_reset.pack(fill=tk.X)

        # --- Frame para a lista de tarefas ---
        frame_lista = tk.Frame(self.root, pady=5)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10)

        label_lista = tk.Label(frame_lista, text="Tarefas Atuais na Fila:")
        label_lista.pack()

        self.listbox_tarefas = tk.Listbox(frame_lista, height=10)
        self.listbox_tarefas.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_remover = tk.Button(frame_lista, text="Remover Tarefa Selecionada", command=self.remover_tarefa_selecionada, bg="#ffdddd")
        btn_remover.pack(fill=tk.X)

        # --- Frame para os botões de simulação ---
        frame_simulacao = tk.Frame(self.root, pady=10)
        frame_simulacao.pack(fill=tk.X, padx=10)

        tk.Frame(frame_simulacao, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)
        label_simulacao = tk.Label(frame_simulacao, text="Escolha um algoritmo para simular:")
        label_simulacao.pack()
        
        # ATUALIZADO: Lista de botões agora inclui todos os escalonadores, inclusive o de ML
        botoes_info = [
            ("FIFO", "FIFO"),
            ("SJF", "SJF"),
            ("Round Robin (Q=2)", "RR"),
            ("Prioridade", "PRIO"),
            ("EDF (Q=2)", "EDF"),
            ("SRTF", "SRTF"),
            ("Round Robin Dinâmico", "RR_Dinamico"),
            ("Escalonador ML", "ML") # NOVO
        ]

        for texto, tipo in botoes_info:
            btn = tk.Button(frame_simulacao, text=f"Simular com {texto}", 
                            command=lambda t=tipo: self.executar_simulacao(t))
            btn.pack(pady=2, fill=tk.X, padx=20)

    def atualizar_listbox(self):
        """Limpa e preenche a Listbox com as tarefas atuais."""
        self.listbox_tarefas.delete(0, tk.END)
        for tarefa in self.tarefas_base:
            texto_tarefa = f"{tarefa.nome} (D: {tarefa.duracao}, P: {tarefa.prioridade}, DL: {tarefa.deadline})"
            self.listbox_tarefas.insert(tk.END, texto_tarefa)

    def remover_tarefa_selecionada(self):
        """Remove o item selecionado da Listbox e da lista de tarefas."""
        selecionados = self.listbox_tarefas.curselection()
        if not selecionados:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma tarefa para remover.")
            return
        indice = selecionados[0]
        tarefa_removida = self.tarefas_base.pop(indice)
        print(f"--- Tarefa removida: {tarefa_removida.nome} ---")
        self.listbox_tarefas.delete(indice)

    def _criar_tarefas(self):
        """ATUALIZADO: Usa a sua nova lógica para gerar tarefas mais realistas."""
        nomes_possiveis = [
            "Detecção de Obstáculo", "Planejamento de Rota", "Manutenção de Velocidade",
            "Com. com Infraestrutura", "Monitoramento de Sensores", "Análise de Imagens",
            "Controle de Estabilidade", "Atualização de Mapas", "Ajuste de Trajetória",
            "Gerenciamento de Energia"
        ]
        tarefas = []
        for i in range(10):
            nome = nomes_possiveis[i % len(nomes_possiveis)]
            tempo_chegada = i * 2
            duracao = random.randint(3, 8)
            deadline = tempo_chegada + duracao + random.randint(5, 20)
            prioridade = random.randint(1, 5)
            tarefas.append(TarefaCAV(nome=nome, duracao=duracao, deadline=deadline, prioridade=prioridade, tempo_chegada=tempo_chegada))
        return tarefas

    def redefinir_tarefas(self):
        """ATUALIZADO: Treina o modelo, gera um novo conjunto de tarefas e atualiza a interface."""
        print("--- Treinando modelo de Machine Learning... ---")
        self.modelo_decision_tree = escalonadorML.treinar_modelo_decision_tree()
        print("--- Modelo treinado. Gerando novas tarefas... ---")
        
        self.tarefas_base = self._criar_tarefas()
        self.atualizar_listbox()

    def executar_simulacao(self, tipo_escalonador):
        """ATUALIZADO: Cria o escalonador correto, incluindo o de ML, e inicia a visualização."""
        if not self.tarefas_base:
            messagebox.showerror("Erro", "Não há tarefas na fila para simular!")
            return

        escalonador = None
        titulo = ""

        if tipo_escalonador == "FIFO":
            escalonador = EscalonadorFIFO(self.tarefas_base)
            titulo = "FIFO"
        elif tipo_escalonador == "SJF":
            escalonador = EscalonadorSJF(self.tarefas_base)
            titulo = "Shortest Job First (SJF)"
        elif tipo_escalonador == "RR":
            escalonador = EscalonadorRoundRobin(tarefas_iniciais=self.tarefas_base, quantum=2)
            titulo = "Round Robin (Q=2)"
        elif tipo_escalonador == "PRIO":
            escalonador = EscalonadorPrioridade(tarefas_iniciais=self.tarefas_base,quantum=2)
            titulo = "Prioridade (Q=2)"
        elif tipo_escalonador == "EDF":
            escalonador = EscalonadorEDF(tarefas_iniciais=self.tarefas_base, quantum=2)
            titulo = "Earliest Deadline First (EDF)"
        elif tipo_escalonador == "SRTF":
            escalonador = EscalonadorSRTF(self.tarefas_base)
            titulo = "Shortest Remaining Time First (SRTF)"
        elif tipo_escalonador == "RR_Dinamico":
            escalonador = EscalonadorRoundRobinDinamico(quantum_base=2, tarefas_iniciais=self.tarefas_base)
            titulo = "Round Robin Dinâmico"
        elif tipo_escalonador == "ML": 
            if not self.modelo_decision_tree:
                messagebox.showerror("Erro de Modelo", "O modelo de Machine Learning não foi treinado!")
                return
            escalonador = EscalonadorML(tarefas_iniciais=self.tarefas_base, modelo=self.modelo_decision_tree, quantum=2)
            titulo = "Decision Tree Model"
        
        if escalonador:
            visualizar_gantt(self.root, escalonador, titulo)

    def iniciar(self):
        """Inicia o loop principal do Tkinter."""
        self.root.mainloop()