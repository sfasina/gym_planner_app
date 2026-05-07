import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, PRIMARY, INFO

class HistoryView(tb.Frame):
   def __init__(self, parent, contorller):
      super().__init__(parent, padding=20)
      self.controller = contorller
      self._build_ui()
      
   def _build_ui(self):
      
      
      