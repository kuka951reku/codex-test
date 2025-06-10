import tkinter as tk
from tkinter import messagebox

from worldview import Worldview


class WorldviewGUI:
    """Simple GUI to map worldview concepts and causal links."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Worldview Mapper")
        self.wv = Worldview()

        # Add concept widgets
        add_frame = tk.Frame(root)
        add_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(add_frame, text="Concept name:").grid(row=0, column=0, sticky="e")
        self.name_entry = tk.Entry(add_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky="w")

        tk.Label(add_frame, text="Description:").grid(row=1, column=0, sticky="e")
        self.desc_entry = tk.Entry(add_frame, width=30)
        self.desc_entry.grid(row=1, column=1, sticky="w")

        tk.Button(add_frame, text="Add Concept", command=self.add_concept).grid(
            row=2, column=0, columnspan=2, pady=5
        )

        # Link widgets
        link_frame = tk.Frame(root)
        link_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(link_frame, text="Cause:").grid(row=0, column=0, sticky="e")
        self.cause_var = tk.StringVar()
        self.cause_menu = tk.OptionMenu(link_frame, self.cause_var, "")
        self.cause_menu.grid(row=0, column=1, sticky="w")

        tk.Label(link_frame, text="Effect:").grid(row=1, column=0, sticky="e")
        self.effect_var = tk.StringVar()
        self.effect_menu = tk.OptionMenu(link_frame, self.effect_var, "")
        self.effect_menu.grid(row=1, column=1, sticky="w")

        tk.Button(link_frame, text="Add Link", command=self.add_link).grid(
            row=2, column=0, columnspan=2, pady=5
        )

        # Display area
        self.text = tk.Text(root, width=50, height=15)
        self.text.pack(padx=10, pady=10)

        self.update_menus()
        self.show_worldview()

    def update_menus(self) -> None:
        for menu in (self.cause_menu["menu"], self.effect_menu["menu"]):
            menu.delete(0, "end")
        for concept in sorted(self.wv.concepts):
            self.cause_menu["menu"].add_command(
                label=concept, command=lambda c=concept: self.cause_var.set(c)
            )
            self.effect_menu["menu"].add_command(
                label=concept, command=lambda c=concept: self.effect_var.set(c)
            )
        self.cause_var.set("")
        self.effect_var.set("")

    def add_concept(self) -> None:
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Concept name required")
            return
        self.wv.add_concept(name, desc)
        self.wv.save()
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.update_menus()
        self.show_worldview()

    def add_link(self) -> None:
        cause = self.cause_var.get()
        effect = self.effect_var.get()
        if not cause or not effect:
            messagebox.showerror("Error", "Cause and effect required")
            return
        try:
            self.wv.link(cause, effect)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
        else:
            self.wv.save()
            self.show_worldview()

    def show_worldview(self) -> None:
        self.text.delete("1.0", tk.END)
        if not self.wv.concepts:
            self.text.insert(tk.END, "Worldview is empty")
            return
        roots = set(self.wv.concepts) - {
            e for effects in self.wv.causations.values() for e in effects
        }
        for root in sorted(roots):
            self._print_tree(root, set(), 0)

    def _print_tree(self, node: str, visited: set[str], indent: int) -> None:
        self.text.insert(tk.END, "  " * indent + node + "\n")
        if node in visited:
            self.text.insert(tk.END, "  " * (indent + 1) + "(cycle)\n")
            return
        visited.add(node)
        for child in self.wv.causations.get(node, []):
            self._print_tree(child, visited, indent + 1)
        visited.remove(node)


def main() -> None:
    root = tk.Tk()
    WorldviewGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
