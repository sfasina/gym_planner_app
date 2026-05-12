import json
import os


class WorkoutModel:
   def __init__(self, database_manager) -> None:
      # Model pracuje přes sdílené databázové připojení z DatabaseManageru.
      self.db_manager = database_manager
      # Při prvním spuštění naplníme prázdnou databázi výchozími cviky z JSONu.
      if self.get_exercise_count() == 0:
         data = self._load_exercises_from_json()
         self._insert_exercises(data)
   
   def _load_exercises_from_json(self) -> list:
      # Data jsou uložená vedle projektu v souboru data/exercises.json.
      # projistotu nastavuji pevnou cestu které nezáleží jestli se spuští z main nebo odjinud
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      JSON_PATH = os.path.join(BASE_DIR, "data", "exercises.json")
      try:
         # Načteme celý JSON jako seznam slovníků s cviky.
         with open(JSON_PATH, "r") as exercise_data:
            # returns: list of dict (exercises) or [] on error
            return json.load(exercise_data)
      
      except FileNotFoundError:
         # Když soubor chybí, vrátíme prázdný seznam a aplikace nespadne.
         print("File not found.")
         # returns: list (empty) on error
         return []
      except json.JSONDecodeError as e:
         # Chybný JSON je lepší ohlásit než tiše ignorovat.
         print(f"Error parsing JSON: {e}")
         # returns: list (empty) on error
         return []
      
   def _get_or_create_muscle(self, cursor, muscle_name) -> int:
      # Nejprve zkusíme najít svalovou skupinu podle názvu.
      cursor.execute("SELECT muscle_group_id FROM muscle_groups WHERE name = ?", (muscle_name,))
      muscle_id = cursor.fetchone()
      if muscle_id is not None:
         # Už existuje, vrátíme její ID.
         # returns: int muscle_group_id
         return muscle_id[0]
      else:
         # Neexistuje, založíme novou skupinu a použijeme nové ID.
         cursor.execute("INSERT INTO muscle_groups (name) VALUES (?)", (muscle_name,))
         # returns: int muscle_group_id
         return cursor.lastrowid
   
   def _insert_exercises(self, data) -> None:
      cursor = self.db_manager.database_connection.cursor()
      
      for exercise in data:
         exercise_name = exercise.get("name")
         # .get(..., []) chrání před chybou, když JSON neobsahuje některý klíč.
         primary_muscles = exercise.get("primary", [])
         secondary_muscles = exercise.get("secondary", [])
         # Nejprve uložíme samotný cvik.
         cursor.execute("INSERT INTO exercises (name) VALUES (?)", (exercise_name,))
         exercise_id = cursor.lastrowid

         # Každý primární sval se propojí s cvikem jako primary.
         for muscle in primary_muscles:
            primary_id = self._get_or_create_muscle(cursor, muscle)
            cursor.execute("INSERT INTO exercise_muscles (exercise_id, muscle_group_id, type) VALUES (?, ?, ?)", (exercise_id, primary_id, "primary"))
         # Stejně tak sekundární svaly, jen s jiným typem vztahu.
         for muscle in secondary_muscles:
            secondary_id = self._get_or_create_muscle(cursor, muscle)
            cursor.execute("INSERT INTO exercise_muscles (exercise_id, muscle_group_id, type) VALUES (?, ?, ?)", (exercise_id, secondary_id, "secondary"))

      self.db_manager.database_connection.commit()
      
      
   def get_exercise_count(self) -> int:
      # Zjistí, jestli databáze už obsahuje nějaké cviky.
      cursor = self.db_manager.database_connection.cursor()
      cursor.execute("""
                     SELECT COUNT(*)
                     FROM exercises
                     """)
      count = cursor.fetchone()
      # returns: int (number of exercises)
      return count[0]   
    
      
   def get_all_exercises(self) -> list:
      # Vrátí seznam cviků pro výběr ve formuláři.
      cursor = self.db_manager.database_connection.cursor()
      cursor.execute("""
         SELECT exercise_id, name
         FROM exercises
         ORDER BY name ASC
      """)
      # returns: list of tuples (exercise_id, name)
      return cursor.fetchall()
    
    
   def get_or_create_training(self, date) -> int:
      # Jedno datum = jeden trénink. Pokud už existuje, znovu ho použijeme.
      cursor = self.db_manager.database_connection.cursor()
      cursor.execute(
         "SELECT training_id FROM trainings WHERE date = ?",
         (date,)
      )
      row = cursor.fetchone()
      if row is not None:
         # returns: int training_id
         return row[0]
      # Jinak vytvoříme nový záznam tréninku pro daný den.
      cursor.execute(
         "INSERT INTO trainings (date) VALUES (?)",
         (date,)
      )
      self.db_manager.database_connection.commit()
      # returns: int training_id
      return cursor.lastrowid
   
   def add_set(self, training_id, exercise_id, weight, reps, rpe, set_number) -> None:
      # Uložení jedné série ke konkrétnímu tréninku a cviku.
      cursor = self.db_manager.database_connection.cursor()
      cursor.execute("""
         INSERT INTO sets (training_id, exercise_id, weight, reps_count, rpe, set_number)
         VALUES (?, ?, ?, ?, ?, ?)
      """, (training_id, exercise_id, weight, reps, rpe, set_number))
      self.db_manager.database_connection.commit()
   
   def get_next_set_number(self, training_id, exercise_id) -> int:
      # Najde další pořadové číslo série pro daný trénink a cvik.
      cursor = self.db_manager.database_connection.cursor()
      cursor.execute("""
         SELECT COALESCE(MAX(set_number), 0) + 1
         FROM sets
         WHERE training_id = ? AND exercise_id = ?
      """, (training_id, exercise_id))
      # returns: int (next set_number)
      return cursor.fetchone()[0]
   
   def get_history(self) -> list:
      # Složený JOIN vrací historii v podobě čitelné pro tabulku ve view.
      cursor = self.db_manager.database_connection.cursor()
      cursor.execute("""
         SELECT s.set_id, t.date, e.name, s.set_number, s.weight, s.reps_count, s.rpe
         FROM sets s
         JOIN trainings t ON s.training_id = t.training_id
         JOIN exercises e ON s.exercise_id = e.exercise_id
         ORDER BY t.date DESC, e.name ASC, s.set_number ASC
      """)
      # returns: list of tuples (set_id, date, name, set_number, weight, reps_count, rpe)
      return cursor.fetchall()

         
         
      
      