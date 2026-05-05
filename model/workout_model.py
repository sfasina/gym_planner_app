import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "data", "exercises.json")

class WorkoutModel:
   def __init__(self, database_manager):
      self.db_manager = database_manager
      if self.get_exercise_count() == 0:
         data = self._load_exercises_from_json()
         self._insert_exercises(data)
         
   def get_exercise_count(self):
      cursor = self.db_manager.connection.cursor()
      cursor.execute("""
                     SELECT COUNT(*)
                     FROM exercises
                     """)
      count = cursor.fetchone()
      return count[0]
   
   def _load_exercises_from_json(self):
      try:
         with open(JSON_PATH, "r") as exercise_data:
            return json.load(exercise_data)
      
      except FileNotFoundError:
        print("File not found.")
        return []
      except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []
      
   def _get_or_create_muscle(self, cursor, muscle_name):
      cursor.execute("SELECT muscle_group_id FROM muscle_groups WHERE name = ?", (muscle_name,))
      muscle_id = cursor.fetchone()
      if muscle_id is not None:
         return muscle_id[0]
      else:
         cursor.execute("INSERT INTO muscle_groups (name) VALUES (?)", (muscle_name,))
         return cursor.lastrowid
   
   def _insert_exercises(self, data):
      cursor = self.db_manager.connection.cursor()
      
      for exercise in data:
         exercise_name = exercise.get("name")
         #the brackets are used to avoid errors if the keys are not present in the JSON data
         primary_muscles = exercise.get("primary", [])
         secondary_muscles = exercise.get("secondary", [])
         cursor.execute("INSERT INTO exercises (name) VALUES (?)", (exercise_name,))
         exercise_id = cursor.lastrowid

         for muscle in primary_muscles:
            primary_id = self._get_or_create_muscle(cursor, muscle)
            cursor.execute("INSERT INTO exercise_muscles (exercise_id, muscle_group_id, type) VALUES (?, ?, ?)", (exercise_id, primary_id, "primary"))
         for muscle in secondary_muscles:
            secondary_id = self._get_or_create_muscle(cursor, muscle)
            cursor.execute("INSERT INTO exercise_muscles (exercise_id, muscle_group_id, type) VALUES (?, ?, ?)", (exercise_id, secondary_id, "secondary"))
      self.db_manager.connection.commit()
      
   def get_all_exercises(self):
      cursor = self.db_manager.connection.cursor()
      cursor.execute("""
         SELECT exercise_id, name
         FROM exercises
         ORDER BY name ASC
      """)
      return cursor.fetchall()
    
   def add_custom_exercise(self, name):
      cursor = self.db_manager.connection.cursor()
      cursor.execute(
         "INSERT INTO exercises (name, custom) VALUES (?, 1)",
         (name,)
      )
      self.db_manager.connection.commit()
      return cursor.lastrowid
    
   def get_or_create_training(self, date):
      cursor = self.db_manager.connection.cursor()
      cursor.execute(
         "SELECT training_id FROM trainings WHERE date = ?",
         (date,)
      )
      row = cursor.fetchone()
      if row is not None:
         return row[0]
      cursor.execute(
         "INSERT INTO trainings (date) VALUES (?)",
         (date,)
      )
      self.db_manager.connection.commit()
      return cursor.lastrowid
   
   def add_set(self, training_id, exercise_id, weight, reps, rpe, set_number):
      cursor = self.db_manager.connection.cursor()
      cursor.execute("""
         INSERT INTO sets (training_id, exercise_id, weight, reps_count, rpe, set_number)
         VALUES (?, ?, ?, ?, ?, ?)
      """, (training_id, exercise_id, weight, reps, rpe, set_number))
      self.db_manager.connection.commit()
   
   def get_next_set_number(self, training_id, exercise_id):
      cursor = self.db_manager.connection.cursor()
      cursor.execute("""
         SELECT COALESCE(MAX(set_number), 0) + 1
         FROM sets
         WHERE training_id = ? AND exercise_id = ?
      """, (training_id, exercise_id))
      return cursor.fetchone()[0]
   
   def get_history(self):
      cursor = self.db_manager.connection.cursor()
      cursor.execute("""
         SELECT s.set_id, t.date, e.name, s.set_number, s.weight, s.reps_count, s.rpe
         FROM sets s
         JOIN trainings t ON s.training_id = t.training_id
         JOIN exercises e ON s.exercise_id = e.exercise_id
         ORDER BY t.date DESC, e.name ASC, s.set_number ASC
      """)
      return cursor.fetchall()

         
         
      
      