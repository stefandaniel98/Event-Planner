from tkinter import ttk

# Palette for Light Mode
# Contains base colors for background, foreground, buttons, etc.
LIGHT = {
    "bg": "#FFFFFF",
    "fg": "#111111",
    "card": "#F2F3F5",
    "button": "#E5E7EB",
    "border": "#D1D5DB",
    "hover": "#DADDE1",
}
# Palette for Dark Mode
DARK = {
    "bg": "#1E1E1E",
    "fg": "#E5E5E5",
    "card": "#2A2A2A",
    "button": "#3A3A3A",
    "border": "#4B5563",
    "hover": "#9CA3AF",
}

# Main function to apply the theme to the Tkinter root window
def apply_theme(root, theme_name: str = "Light"):
    pal = LIGHT if theme_name == "Light" else DARK

    style = ttk.Style(root)
    style.theme_use("clam")

    
    root.configure(bg=pal["bg"])

    # FRAME and LABELFRAME Styling

    style.configure("TFrame", background=pal["bg"])
    style.configure("TLabelframe", background=pal["bg"], foreground=pal["fg"])
    style.configure("TLabelframe.Label", background=pal["bg"], foreground=pal["fg"])

    # LABEL Styling
    style.configure("TLabel", background=pal["bg"], foreground=pal["fg"])

    # BUTTON Styling
    style.configure(
        "TButton",
        background=pal["button"],
        foreground=pal["fg"],
        padding=8,
        relief="flat",
        borderwidth=2,
        bordercolor=pal["border"],
        focusthickness=0,
        highlightthickness=0,
        font=("Segoe UI", 10),
    )

    # Button behavior for "hover" and "pressed" states
    style.map(
        "TButton",
        background=[("active", pal["hover"]), ("pressed", pal["hover"])],
        bordercolor=[("active", pal["border"]), ("pressed", pal["border"])],
        foreground=[("active", pal["fg"]), ("pressed", pal["fg"])],
    )

    
    # TREEVIEW Styling (ttk table)
    style.configure(
        "Treeview",
        background=pal["card"],
        fieldbackground=pal["card"],
        foreground=pal["fg"],
        rowheight=26,
        bordercolor=pal["border"],
        borderwidth=1,
    )

    # Table Column Header Styling
    style.configure(
        "Treeview.Heading",
        background=pal["button"],
        foreground=pal["fg"],
        relief="raised",
        borderwidth=1,
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "Treeview.Heading",
        background=[("active", pal["hover"]), ("pressed", pal["hover"])],
        foreground=[("active", pal["fg"]), ("pressed", pal["fg"])]
    )

   # MENU BUTTON Styling
    style.configure("TMenubutton", background=pal["button"], foreground=pal["fg"])


    # GLOBAL Styling via option_add
    # This affects legacy Tkinter widgets (Entry, Text, Canvas, etc.)
    root.option_add("*Background", pal["bg"])
    root.option_add("*Foreground", pal["fg"])
    root.option_add("*TEntry*Foreground", pal["fg"])
    root.option_add("*Entry*Background", pal["card"])
    root.option_add("*Entry*Foreground", pal["fg"])
    root.option_add("*Text*Background", pal["card"])
    root.option_add("*Text*Foreground", pal["fg"])
    root.option_add("*Listbox*Background", pal["card"])
    root.option_add("*Listbox*Foreground", pal["fg"])
    root.option_add("*Canvas*Background", pal["bg"])
    root.option_add("*Label*Background", pal["bg"])
    root.option_add("*Label*Foreground", pal["fg"])
    root.option_add("*Button*Background", pal["card"])
    root.option_add("*Button*Foreground", pal["fg"])
    root.option_add("*Toplevel*Background", pal["bg"])

