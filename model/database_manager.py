from multiprocessing.dummy import connection
import sqlite3 

class DatabaseManager:
   def __init__(self, db_path):
      self.database_connection = sqlite3.connect(db_path)
      self.database_connection.execute("PRAGMA foreign_keys = ON")
      self.create_table()
   
   def create_table(self):
      cursor = self.database_connection.cursor()
      
      cursor.execute("""
         CREATE TABLE IF NOT EXISTS exercises( 
            exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            custom INTEGER DEFAULT 0
            )
         """)
      
      cursor.execute("""
         CREATE TABLE IF NOT EXISTS trainings (
            training_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL
            )
         """)
      
      cursor.execute(""" 
         CREATE TABLE IF NOT EXISTS muscle_groups (
            muscle_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL                    
         )
         """)
      
      cursor.execute(""" 
         CREATE TABLE IF NOT EXISTS exercise_muscles (
            type TEXT NOT NULL CHECK(type IN ('primary', 'secondary')),
            exercise_id INTEGER,
            muscle_group_id INTEGER,
            PRIMARY KEY (exercise_id, muscle_group_id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id),
            FOREIGN KEY (muscle_group_id) REFERENCES muscle_groups(muscle_group_id)                   
            )
         """)
      
      cursor.execute("""
         CREATE TABLE IF NOT EXISTS sets( 
            set_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reps_count INTEGER,
            rpe FLOAT,
            weight FLOAT,
            set_number INTEGER,
            exercise_id INTEGER,
            training_id INTEGER,
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id),
            FOREIGN KEY (training_id) REFERENCES trainings(training_id)
            )
         """)
      
      self.database_connection.commit()
      