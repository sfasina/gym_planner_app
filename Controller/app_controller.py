from model.database_manager import DatabaseManager
from model.workout_model import WorkoutModel

class AppController:
   def __init__(self):
      self._database = DatabaseManager()
      self._model = WorkoutModel(self._database)
      # self._view = MainWindow(controller=self)
      
   def save_set(self, date, exercise_id, weight, reps, rpe):
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
   
   def get_exercises(self):
      return self._model.get_all_exercises()
   
   def add_custom_exercise(self, name):
      return self._model.add_custom_exercise(name)
   
   def get_history(self):
      return self._model.get_history()
      
   def run(self):
      print("Aplikace spuštěna")
      # self._view.mainloop()