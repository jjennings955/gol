import numpy as np
import Tkinter as Tk
import scipy.signal
import scipy.ndimage
from PIL import ImageTk
from PIL import Image

class GOLGui(Tk.Frame):
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', 1920)
        self.height = kwargs.pop('height', 800)
        Tk.Frame.__init__(self, *args, **kwargs)
        self.canvas = Tk.Canvas(self, width=self.width, height=self.height)
        self.photo = None
        self.images = None
        self.old = None
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.pack(fill=Tk.BOTH, expand=1)

    def draw(self, state=None):
        if not self.photo:
            self.image = Image.fromarray(255.0 * state)
            self.image = self.image.resize((self.width, self.height), Image.NONE)
            self.photo = ImageTk.PhotoImage(image=self.image)
        else:
            self.image = Image.fromarray(255.0 * state)
            self.image = self.image.resize((self.width, self.height), Image.NONE)
            self.photo.paste(self.image)

        if self.old:
            self.canvas.delete(self.old)

        self.old = self.canvas.create_image(0, 0, image=self.photo, anchor=Tk.NW)

    def loop(self, cb=None):
        cb()
        self.after(50, lambda : self.loop(cb=cb))

class GOL:
    def __init__(self, initial_state=None, live=None, dead=None):
        self.state = initial_state
        self.neighbors = np.array([[1, 1, 1],
                                  [1, 0, 1],
                                  [1, 1, 1]])
        self.live = live
        self.dead = dead
        self.observers = []

    def update_state(self):
        net = scipy.ndimage.convolve(self.state, self.neighbors, mode='wrap')
        self.state = self.state * self.live(net) + (1 - self.state)*(self.dead(net))
        self.notify()

    def notify(self):
        for cb in self.observers:
            cb(state=self.state)

def GliderWorld(width=800, height=800, pop=0.05):
    initial_state = np.random.binomial(1, pop, size=(width, height))
    live = lambda x: 0.7 * np.exp(-4 * (x - 3) ** 2)
    dead = lambda x: 1.5 * np.exp(-4 * (x - 3) ** 2)
    return GOL(initial_state, live, dead)

def GOLVanilla(width=800, height=800, pop=0.05):
    initial_state = np.random.binomial(1, pop, size=(width, height))
    live = lambda x: np.where((x == 2) | (x == 3), 1, 0)
    dead = lambda x: np.where((x >= 3), 1, 0)
    return GOL(initial_state, live, dead)

if __name__ == "__main__":
    gui = Tk.Tk()
    gui.geometry('800x600')
    smooth_frame = GOLGui(gui, width=800, height=600)
    gol_smooth = GliderWorld(16*30, 9*30, pop=0.07)
    gol_smooth.observers.append(smooth_frame.draw)
    smooth_frame.loop(gol_smooth.update_state)

    gui.mainloop()

