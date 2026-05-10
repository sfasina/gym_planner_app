import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, PRIMARY,  SECONDARY
from ttkbootstrap.widgets import DateEntry
import tkinter as tk
from datetime import date, datetime


class WorkoutForm(tb.Frame):
   def __init__(self, parent, controller):
      super().__init__(parent, padding=20)
      self._selected_exercise_id = None
      self._all_exercises: list[tuple[int, str]] = []
      self._controller = controller
      self._rpe_var = tk.IntVar(value=5)
      self._build_ui()
      self._load_exercise()


   def _build_ui(self) -> None:
      self._configure_grid()
      self._build_title()
      self._build_date_section()
      self._build_exercise_section()
      self._build_weight_reps_section()
      self._build_rpe_section()
      self._build_button_section()
      self._build_status_section()


   def _configure_grid(self) -> None:
      self.columnconfigure(0, weight=1)
      self.columnconfigure(1, weight=1)


   def _build_title(self) -> None:
      tb.Label(
         self,
         text="Zaznamenat sérii",
         font=("Helvetica", 16, "bold"),
         bootstyle=PRIMARY,
      ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))


   def _build_date_section(self) -> None:
      tb.Label(self, text="Datum").grid(row=1, column=0, sticky="w")
      
      self._date_entry = DateEntry(self, dateformat="%d.%m.%Y", bootstyle=PRIMARY)
      self._date_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
      
      # Předvyplnění dnešním datumem
      self._date_entry.entry.delete(0, "end")
      self._date_entry.entry.insert(0, date.today().strftime("%d.%m.%Y"))


   def _build_exercise_section(self) -> None:
      tb.Label(self, text="Cvik").grid(row=3, column=0, sticky="w", pady=(0, 5))
      
      # Entry s live filtrováním
      self._exercise_var = tk.StringVar()
      self._exercise_var.trace_add("write", self._on_exercise_type)
      self._exercise_entry = tb.Entry(self, textvariable=self._exercise_var)
      self._exercise_entry.grid(row=4, column=0, columnspan=2, sticky="ew")
      
      # Listbox s filtrovanými výsledky
      self._exercise_listbox = tk.Listbox(self, height=8, selectmode=tk.SINGLE)
      self._exercise_listbox.grid(row=5, columnspan=2, sticky="ew")
      self._exercise_listbox.bind("<<ListboxSelect>>", self._on_exercise_select)


   def _build_weight_reps_section(self) -> None:
      # Hlavičky
      tb.Label(self, text="Váha (kg)").grid(row=6, column=0, sticky="w", pady=(20, 2), padx=(0, 20))
      tb.Label(self, text="Opakování").grid(row=6, column=1, sticky="w", pady=(20, 2), padx=(20, 0))
      
      # Entry pole
      self._weight_entry = tb.Entry(self)
      self._weight_entry.grid(row=7, column=0, sticky="ew", padx=(0, 20), pady=(0, 20))
      
      self._reps_entry = tb.Entry(self)
      self._reps_entry.grid(row=7, column=1, sticky="ew", padx=(20, 0), pady=(0, 20))


   def _build_rpe_section(self) -> None:
      tb.Label(self, text="RPE: ").grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 2))
      
      # Slider 1-10
      self._rpe_scale = tb.Scale(
         self,
         from_=1,
         to=10,
         orient="horizontal",
         command=self._on_rpe_change,
      )
      self._rpe_scale.grid(row=9, column=0, sticky="ew", padx=(0, 10), pady=(0, 20))
      self._rpe_scale.set(5)
      
      # Label s aktuální hodnotou
      self._rpe_label = tb.Label(
         self,
         textvariable=self._rpe_var,
         font=("Helvetica", 10, "bold"),
      )
      self._rpe_label.grid(row=8, column=0, sticky="ew", padx=(50, 0))


   def _build_button_section(self) -> None:
      tb.Button(
         self,
         text="💾 Uložit sérii",
         bootstyle=SUCCESS,
         command=self._on_save,
      ).grid(row=10, column=0, sticky="ew", padx=(0, 5), pady=(0, 10))
      


   def _build_status_section(self) -> None:
      self._status_var = tk.StringVar(value="")
      self._status_label = tb.Label(self, textvariable=self._status_var)
      self._status_label.grid(row=11, column=0, columnspan=2, sticky="w")

   # hazím pryč argumenty které posílá Tkinter
   # bez *args by to spadlo kvůli nevyžádaným argumentům
   def _on_exercise_type(self, *args) -> None:
      query = self._exercise_var.get()
      self._exercise_listbox.delete(0, tk.END)
      for exercise in self._all_exercises:
         if query.lower() in exercise[1].lower():
            self._exercise_listbox.insert(tk.END, exercise[1])
             
   def _on_exercise_select(self, event):
      selection = self._exercise_listbox.curselection()
      if not selection:
         return
      selection_index = selection[0]
      selection_name = self._exercise_listbox.get(selection_index)
      for exercise_id, name in self._all_exercises:
         if name == selection_name:
            self._selected_exercise_id = exercise_id
            break
      self._exercise_var.set(selection_name)
      

   def _on_rpe_change(self, value) -> None:
      self._rpe_var.set(int(float(value)))
      
      
   def _load_exercise(self):
      self._all_exercises = self._controller.get_exercises()
      self._on_exercise_type()
      
   def _clear_form(self)  -> None:
      self._weight_entry.delete(0, tk.END)
      self._reps_entry.delete(0, tk.END)   
      
   def _on_save(self) -> None:
      # Validace hodnot
      date_str = self._date_entry.entry.get()
      exercise_id = self._selected_exercise_id
      weight_str = self._weight_entry.get()
      reps_str = self._reps_entry.get()
      rpe = self._rpe_var.get()
      
      # Validace cvik 
      if exercise_id is None:
         self._status_var.set("Vyber cvik ze seznamu")
         return
      
      # Validace váha
      weight_str = weight_str.replace(",", ".")
      try:
         weight = float(weight_str)
      except ValueError:
         self._status_var.set("Váha musí být číslo")
         return
      
      # Validace opakování 
      try:
         reps = int(reps_str)
      except ValueError:
         self._status_var.set("Opakování musí být celé číslo")
         return
      
      date_formated = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
      if self._controller.save_set(date_formated, exercise_id, weight, reps, rpe):
         self._status_var.set("Série uložena")
         self._clear_form()
      else:
         self._status_var.set("Nepodařilo se uložit")
         
      print(date_formated, exercise_id, weight, reps, rpe)
