import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY
from tkinter import ttk
from datetime import datetime


class HistoryView(tb.Frame):
   def __init__(self, parent, controller):
      super().__init__(parent, padding=20)
      self._controller = controller
      self._build_ui()
      self.refresh()
   
   # ============================================================
   #  Sestavení UI — jen jednou při startu
   # ============================================================
   
   def _build_ui(self) -> None:
      tb.Label(
         self,
         text="Historie tréninků",
         font=("Helvetica", 16, "bold"),
         bootstyle=PRIMARY,
      ).pack(pady=(0, 20), anchor="w")
      
      self._build_tree()

   def _build_tree(self) -> None:
      # Rozdělím sestavení stromu do menších kroků kvůli čitelnosti.
      self._create_tree_widget()
      self._configure_tree_style()
      self._configure_tree_headings()
      self._configure_tree_columns()
      self._tree.pack(fill="both", expand=True)

   def _create_tree_widget(self) -> None:
      # Základní strom s jedním hierarchickým sloupcem a třemi datovými.
      self._tree = ttk.Treeview(
         self,
         columns=("col1", "col2", "col3"),
         show="tree headings",
      )

   def _configure_tree_style(self) -> None:
      # Vyšší řádky zlepší čitelnost vnořených položek.
      style = ttk.Style()
      style.configure("History.Treeview", rowheight=35)
      self._tree.configure(style="History.Treeview")

   def _configure_tree_headings(self) -> None:
      # Hlavičky popisují data na úrovni datumu, cviku a série.
      self._tree.heading("#0", text="Datum / Cvik / Série", anchor="w")
      self._tree.heading("col1", text="Váha / Objem", anchor="center")
      self._tree.heading("col2", text="Opakování / Sérií", anchor="center")
      self._tree.heading("col3", text="RPE", anchor="center")

   def _configure_tree_columns(self) -> None:
      # Zarovnání a šířky drží tabulku čitelnou i při delších názvech.
      self._tree.column("#0", width=320, minwidth=220, anchor="w")
      self._tree.column("col1", width=170, minwidth=120, anchor="center")
      self._tree.column("col2", width=170, minwidth=140, anchor="center")
      self._tree.column("col3", width=110, minwidth=80, anchor="center")
         
      self._tree.pack(fill="both", expand=True)
   
   def refresh(self) -> None:
      self._clear_tree()
      rows = self._controller.get_history()
      grouped = self._group_data(rows)
      self._fill_tree(grouped)
   
   
   def _clear_tree(self) -> None:
      # Před novým vykreslením odstraním starý obsah.
      for item in self._tree.get_children():
         self._tree.delete(item)
   
   def _group_data(self, rows: list) -> dict:
      # Převod plochého seznamu na strom: datum -> cvik -> série.
      grouped = {}
      
      for row in rows:
         set_id, date_str, name, set_number, weight, reps, rpe = row
         
         # Větev pro datum vytvořím jen při prvním výskytu.
         if date_str not in grouped:
               grouped[date_str] = {}
         
         # Každý cvik pod daným datem má vlastní seznam sérií.
         if name not in grouped[date_str]:
               grouped[date_str][name] = []
         
         # Zachovám pořadí, v jakém série přišly z databáze.
         grouped[date_str][name].append((set_id, set_number, weight, reps, rpe))
      
      return grouped
   
   def _fill_tree(self, grouped: dict) -> None:
      # Vykreslení probíhá od nejvyšší úrovně dolů.
      for date_str, exercises in grouped.items():
         # Nejprve vložím datum, potom cviky, potom jednotlivé série.
         date_item_id = self._insert_date_row(date_str)

         for exercise_name, sets in exercises.items():
            exercise_item_id = self._insert_exercise_row(date_item_id, exercise_name, sets)

            for set_data in sets:
               self._insert_set_row(exercise_item_id, set_data)
   
   def _insert_date_row(self, date_str: str) -> str:
      # Převod formátu z databáze na čitelný zápis pro uživatele.
      date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
      
      return self._tree.insert(
         "",                              # prázdný rodič = top-level
         "end",
            text=date_display,
         values=("", "", ""),
         open=True,
      )
   
   def _insert_exercise_row(self, parent_item_id: str, name: str, sets: list) -> str:
      # Objem je součet váha × opakování přes všechny série cviku.
      total_volume = 0
      for set_id, set_number, weight, reps, rpe in sets:
         total_volume += weight * reps
      
      set_count = len(sets)
      
      return self._tree.insert(parent_item_id, "end", text=name,
         values=(
               f"objem: {total_volume:.0f} kg",
               f"{set_count} sérií",
               "",
         ),
      )
   
   def _insert_set_row(self, parent_item_id: str, set_data: tuple) -> None:
      set_id, set_number, weight, reps, rpe = set_data

      self._tree.insert(parent_item_id, "end", text=f"série {set_number}",
         values=(
               f"{weight} kg",
               f"{reps} rep",
               f"RPE {rpe}",
         ),
      )