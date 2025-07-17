import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

from escalonador import EscalonadorCAV

def visualizar_gantt(parent_window, escalonador: EscalonadorCAV, titulo: str):
    """
    Executa um escalonador, exibe os resultados e desenha o gráfico de Gantt.
    """
    # Executa a simulação para popular os dados
    escalonador.escalonar()
    escalonador.calcular_e_exibir_metricas()

    # Prepara a janela de visualização
    janela_gantt = tk.Toplevel(parent_window)
    janela_gantt.title(titulo)
    janela_gantt.geometry("900x500")

    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Prepara os dados para o gráfico
    nomes_tarefas = sorted(list(set(t.nome for t in escalonador.tarefas_para_escalonar)), reverse=True)
    colors = cm.viridis(np.linspace(0, 1, len(nomes_tarefas)))
    color_map = {nome: color for nome, color in zip(nomes_tarefas, colors)}

    max_time = 0

    # Desenha as barras no gráfico
    for tarefa in escalonador.tarefas_para_escalonar:
        for inicio, fim in tarefa.tempos_execucao:
            duracao = fim - inicio
            ax.barh(tarefa.nome, duracao, left=inicio, color=color_map[tarefa.nome], edgecolor='black', height=0.6)
        if tarefa.tempo_final > max_time:
            max_time = tarefa.tempo_final

    # Configura a aparência do gráfico
    ax.set_yticks(np.arange(len(nomes_tarefas)))
    ax.set_yticklabels(nomes_tarefas)
    ax.set_xlabel("Tempo de Simulação (segundos)")
    ax.set_ylabel("Tarefas")
    ax.set_title(f"Diagrama de Gantt - {titulo}")
    ax.set_xlim(0, max_time * 1.05 if max_time > 0 else 10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, axis='x')

    # 6. Adiciona o gráfico à janela Tkinter
    canvas = FigureCanvasTkAgg(fig, master=janela_gantt)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)