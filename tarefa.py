class TarefaCAV:
    """Representa uma tarefa a ser executada por um Veículo Autônomo Conectado (CAV)."""
    def __init__(self, nome, duracao, prioridade=1, tempo_chegada=0, deadline=0):
        self.nome = nome
        self.duracao = duracao
        self.prioridade = prioridade
        self.deadline = deadline
        self.tempo_restante = duracao
        self.tempo_chegada = tempo_chegada  # Hora em que a tarefa começa
        self.tempo_inicio_execucao = -1   # Tempo da primeira execução
        self.tempo_final = -1           # Tempo final de conclusão
        self.tempos_execucao = []         # Lista de tuplas (inicio, fim) de cada burst de execução
        self.foi_executada = False        # Flag para controle do tempo_inicio_execucao

    def __str__(self):
        return f"Tarefa {self.nome} (Prioridade {self.prioridade}): {self.duracao} segundos"

    def __repr__(self):
        return f"{self.nome}"

    def executar(self, quantum):
        """Executa a tarefa por um tempo de 'quantum' ou até terminar."""
        tempo_exec = min(self.tempo_restante, quantum)
        self.tempo_restante -= tempo_exec
        return tempo_exec