import customtkinter as ctk

class ModernButton(ctk.CTkButton):
    """Custom styled button for the game"""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("font", ("Segoe UI", 14, "bold"))
        kwargs.setdefault("height", 45)
        super().__init__(master, **kwargs)
