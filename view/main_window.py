import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS

from view.workout_form import WorkoutForm
from view.history_view import HistoryView


class MainWindow(tb.Window):
   def __init__(self, controller):
      super().__init__(themename="darkly")
      self._controller = controller
      self.title("Fitness Tracker")
      self.geometry("1520x1100")
      self._build_ui()

   def _build_ui(self) -> None:
      # Hlavní okno rozdělené do dvou záložek.
      notebook = tb.Notebook(self, bootstyle=SUCCESS)
      notebook.pack(fill="both", expand=True, padx=10, pady=10)

      # Formulář pro zadání nového tréninku.
      workout_form = WorkoutForm(notebook, controller=self._controller)
      notebook.add(workout_form, text=" TRAINING ")
      
      # Přehled historie a statistik.
      self._history_tab = HistoryView(notebook, controller=self._controller)
      notebook.add(self._history_tab, text=" STATISTIKA ")

      notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed) 
      self._notebook = notebook

   def _on_tab_changed(self, event) -> None:
      # Po přepnutí na historii načteme aktuální data.
      selected = event.widget.index(event.widget.select())
      if selected == 1:
         self._history_tab.refresh()