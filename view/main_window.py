import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, PRIMARY, INFO

from view.workout_form import WorkoutForm


class MainWindow(tb.Window):
   def __init__(self, controller):
      super().__init__(themename="darkly")
      self._controller = controller
      self.title("Fitness Tracker")
      self.geometry("1500x1020")
      self._build_ui()

   def _build_ui(self) -> None:
      notebook = tb.Notebook(self, bootstyle=SUCCESS)
      notebook.pack(fill="both", expand=True, padx=10, pady=10)

      
      workout_form = WorkoutForm(notebook, controller=self._controller)
      notebook.add(workout_form, text=" TRAINING ")
      

      history_tab = tb.Frame(notebook, padding=20)
      tb.Label(
         history_tab,
         text="Zde bude tabulka s historií tréninků",
         font=("Helvetica", 14),
      ).pack(pady=20)
      notebook.add(history_tab, text=" STATISTIC ")
      notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
      self._notebook = notebook

   def _on_tab_changed(self, event) -> None:
      selected = event.widget.index(event.widget.select())
      print(f"Přepnuto na záložku index {selected}")