from model.database_manager import DatabaseManager
from model.workout_model import WorkoutModel
from view.main_window import MainWindow

class AppController:
   def __init__(self) -> None:
      # Vytvoří databázi, model a hlavní okno aplikace.
      self._database = DatabaseManager()
      self._model = WorkoutModel(self._database)
      self._view = MainWindow(controller=self)
      
   def save_set(self, date: str, exercise_id: int | None, weight: float, reps: int, rpe: int) -> bool:
      # Zkontroluje vstupy a když jsou v pořádku, uloží sérii do databáze.
      if not date:
         return False
      if exercise_id is None:
         return False
      if weight < 0:
         return False
      if reps < 1:
         return False
      if rpe < 1 or rpe > 10:
         return False
   
      training_id = self._model.get_or_create_training(date)
      set_number = self._model.get_next_set_number(training_id, exercise_id)
      self._model.add_set(training_id, exercise_id, weight, reps, rpe, set_number)
      return True
   
   def get_exercises(self) -> list:
      # Vrátí všechny cviky pro výběr ve formuláři.
      return self._model.get_all_exercises()
   
   def get_history(self) -> list:
      # Vrátí historii tréninků pro view.
      return self._model.get_history()
      
   def run(self) -> None:
      # Spustí hlavní smyčku aplikace.
      self._view.mainloop()