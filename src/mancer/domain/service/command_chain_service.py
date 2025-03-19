from typing import List, Optional, Any, Dict
from ..model.command_result import CommandResult
from ..model.command_context import CommandContext
from ..model.data_format import DataFormat
from ..model.execution_history import ExecutionHistory
from ..interface.command_interface import CommandInterface

class CommandChain:
    """Klasa reprezentująca łańcuch komend"""
    
    def __init__(self, first_command: CommandInterface):
        self.commands = [first_command]
        self.is_pipeline = [False]  # Pierwszy element jest zawsze False
        self.preferred_formats = [getattr(first_command, 'preferred_data_format', DataFormat.LIST)]
        self.history = ExecutionHistory()
    
    def then(self, next_command: CommandInterface) -> 'CommandChain':
        """Dodaje kolejną komendę do łańcucha (sekwencyjnie)"""
        self.commands.append(next_command)
        self.is_pipeline.append(False)
        self.preferred_formats.append(getattr(next_command, 'preferred_data_format', DataFormat.LIST))
        return self
    
    def pipe(self, next_command: CommandInterface) -> 'CommandChain':
        """Dodaje komendę jako potok (stdout -> stdin)"""
        self.commands.append(next_command)
        self.is_pipeline.append(True)
        self.preferred_formats.append(getattr(next_command, 'preferred_data_format', DataFormat.LIST))
        return self
    
    def with_data_format(self, format_type: DataFormat) -> 'CommandChain':
        """Ustawia preferowany format danych dla wynikowego CommandResult"""
        # Ustawia preferowany format dla ostatniej komendy w łańcuchu
        if self.commands and hasattr(self.commands[-1], 'preferred_data_format'):
            self.commands[-1].preferred_data_format = format_type
            self.preferred_formats[-1] = format_type
        return self
    
    def get_history(self) -> ExecutionHistory:
        """Zwraca historię wykonania łańcucha komend"""
        return self.history
    
    def execute(self, context: CommandContext) -> CommandResult:
        """Wykonuje cały łańcuch komend"""
        if not self.commands:
            raise ValueError("Łańcuch komend jest pusty")
        
        result = None
        current_context = context
        
        for i, command in enumerate(self.commands):
            # Pierwszy element nie ma poprzedniego wyniku
            if i == 0:
                result = command.execute(current_context)
            else:
                # Jeśli potok, przekazujemy wynik jako wejście
                if self.is_pipeline[i]:
                    # Jeśli formaty danych się różnią, dokonaj konwersji
                    prev_format = self.preferred_formats[i-1]
                    curr_format = self.preferred_formats[i]
                    
                    if result and prev_format != curr_format and hasattr(result, 'to_format'):
                        # Konwertuj wynik do preferowanego formatu bieżącej komendy
                        result = result.to_format(curr_format)
                    
                    result = command.execute(current_context, result)
                else:
                    # Jeśli sekwencja, używamy bieżącego kontekstu
                    result = command.execute(current_context)
            
            # Aktualizujemy kontekst po każdej komendzie
            if result and result.is_success():
                current_context.add_to_history(command.build_command())
                
                # Dodajemy krok do historii wykonania łańcucha
                if hasattr(result, 'get_history') and result.get_history():
                    # Kopiujemy historię z wyniku do historii łańcucha
                    for step in result.get_history():
                        self.history.add_step(step)
                
                # Zakładamy, że cd aktualizuje current_directory w kontekście
                if command.__class__.__name__ == "CdCommand" and result.is_success():
                    # Nie trzeba robić nic więcej, bo komenda cd sama aktualizuje kontekst
                    pass
        
        # Dodajemy historię wykonania do metadanych wynikowego CommandResult
        if result and hasattr(result, 'metadata'):
            if result.metadata is None:
                result.metadata = {}
            result.metadata['execution_history'] = self.history.to_dict()
            
            # Dodajemy także informację o całym łańcuchu
            result.metadata['command_chain'] = {
                'commands': [cmd.build_command() for cmd in self.commands],
                'pipeline_steps': self.is_pipeline,
                'total_commands': len(self.commands)
            }
        
        return result
