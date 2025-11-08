import customtkinter as ctk
from lib.views.components.modern_button import ModernButton


class GameModeView:
    """Modern UI for game mode selection"""

    def __init__(self, on_mode_selected):
        self.on_mode_selected = on_mode_selected

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("Game Mode Selection")
        self.window.geometry("600x400")

        # Main frame
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="🎮 2D Board Game",
            font=("Segoe UI", 36, "bold"),
            text_color="#00D9FF"
        )
        title.pack(pady=(0, 20))

        subtitle = ctk.CTkLabel(
            main_frame,
            text="Who will play the game?",
            font=("Segoe UI", 18),
            text_color="#AAAAAA"
        )
        subtitle.pack(pady=(0, 50))

        # Button frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        # Player button
        player_btn = ModernButton(
            btn_frame,
            text="👤 Player",
            width=200,
            fg_color="#00D9FF",
            hover_color="#00B8E6",
            command=lambda: self.select_mode(True)
        )
        player_btn.pack(side="left", padx=15)

        # Computer button
        computer_btn = ModernButton(
            btn_frame,
            text="🤖 Computer",
            width=200,
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            command=lambda: self.select_mode(False)
        )
        computer_btn.pack(side="left", padx=15)

    def select_mode(self, is_player: bool):
        """Handle mode selection"""
        self.window.destroy()
        self.on_mode_selected(is_player)

    def run(self):
        """Start the window"""
        self.window.mainloop()
