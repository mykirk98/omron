import tkinter as tk

import tkinter as tk

class TriggerButtonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trigger Button")
        
        self.button = tk.Button(root, text="Trigger", command=self.on_button_click)
        self.button.pack()
        self.button.config(width=20, height=3)
        self.root.geometry("300x200")

    def on_button_click(self):
        print("Button clicked")
        # software trigger for camera
        return True

    @classmethod
    def run(cls):
        root = tk.Tk()
        app = cls(root)
        root.mainloop()



if __name__ == "__main__":
    trigger = TriggerButtonApp
    trigger.run()