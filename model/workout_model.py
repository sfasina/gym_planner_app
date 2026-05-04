class WorkoutModel:
   def __init__(self, database_manager):
      self.db_manager = database_manager
      if self.get_exercise_count() == 0:
         self.insert_exercises()
         
   def get_exercise_count(self):
      cursor = self.db_manager.connection.cursor()
      cursor.execute("""
                     SELECT COUNT(*)
                     FROM exercises
                  """)
      count = cursor.fetchone()
      return count[0]
   
   def insert_exercises(self):
      cursor = self.db_manager.connection.cursor()
      cursor.execute
      
      ##dodelat tuto funkci na insertovani
      