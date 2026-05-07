import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, PRIMARY, INFO
from ttkbootstrap.widgets import DateEntry
import tkinter as tk
from datetime import date

class WorkoutForm(tb.Frame):
   def __init__(self, parent, controller):
      self._selected_exercise_id = None
      self._all_exercises: list[tuple[int, str]] = []
      super().__init__(parent, padding=20)
      self._controller = controller
      self._build_ui()

   def _build_ui(self) -> None:
      tb.Label(self,
      text="Zaznamenat sérii",
      font=("Helvetica", 16, "bold"),
      bootstyle=PRIMARY,
      ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
      
      tb.Label(self, text="Datum").grid(row=1, column=0, sticky="w")
      self._date_entry = DateEntry(self, dateformat="%d.%m.%Y", bootstyle=PRIMARY)
      self._date_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
      self._date_entry.entry.delete(0, "end")
      self._date_entry.entry.insert(0, date.today().strftime("%d.%m.%Y"))
      
      tb.Label(self, text="Cvik").grid(row=3, column=0, sticky="w", pady=(0, 20))
      self._exercise_var = tk.StringVar()
      self._exercise_var.trace_add("write", self._on_exercise_type)
      self._exercise_entry = tb.Entry(self, textvariable=self._exercise_var)
      self._exercise_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
      
      self._exercise_listbox = tk.Listbox(self, height=5, selectmode=tk.SINGLE)  
      self._exercise_listbox.grid(row=5, columnspan=2, sticky="ew")
      
      
      
   
   def _on_exercise_type(self, *args) -> None:
      query = self._exercise_var.get()
      self._exercise_listbox.delete(0, tk.END)
      for exercise in self._all_exercises:
         if query.lower() in exercise[1].lower():
            self._exercise_listbox.insert(tk.END, exercise[1])
             
         

   def _on_test_click(self) -> None:
      exercises = self._controller.get_exercises()
      print(f"Načteno {len(exercises)} cviků z databáze:")
      for exercise_id, name in exercises:
         print(f"  {exercise_id}: {name}")