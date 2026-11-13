import tkinter as tk
import time
import math

class GeoptimaliseerdeVerbondenKlok:
    def __init__(self, root):
        self.root = root
        self.root.title("Pure 4-Segmenten Desktop Klok")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.configure(bg='#111111')
        self.root.wm_attributes("-transparentcolor", "#111111")
        self.canvas = tk.Canvas(root, width=1100, height=280, bg='#e0eee0', highlightthickness=0)
        self.canvas.pack()
        
        self.cijfer_matrix = {
            '0': ['S1'],
            '1': ['S4'],
            '2': ['S1', 'S3'],
            '3': ['S1', 'S3', 'S4'],
            '4': ['S2', 'S4'],
            '5': ['S1', 'S2', 'S3'],
            '6': ['S1', 'S2'],
            '7': ['S3', 'S4'],
            '8': ['S1', 'S2', 'S3', 'S4'],
            '9': ['S2', 'S3', 'S4']
        }
        
        self.canvas.bind("<Button-1>", self.start_slepen)
        self.canvas.bind("<B1-Motion>", self.doe_slepen)
        self.canvas.bind("<Button-3>", lambda e: self.root.destroy())
        self.centreer_venster(1100, 280)
        self.update_klok()

    def centreer_venster(self, breedte, hoogte):
        scherm_breedte = self.root.winfo_screenwidth()
        scherm_hoogte = self.root.winfo_screenheight()
        x = (scherm_breedte // 2) - (breedte // 2)
        y = (scherm_hoogte // 2) - (hoogte // 2)
        self.root.geometry(f"{breedte}x{hoogte}+{x}+{y}")

    def start_slepen(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def doe_slepen(self, event):
        x = self.root.winfo_x() + (event.x - self.start_x)
        y = self.root.winfo_y() + (event.y - self.start_y)
        self.root.geometry(f"+{x}+{y}")

    def transformeer_punt(self, x, y, cy=150, schuinte=0.20):
        nieuw_x = x + schuinte * (cy - y)
        return nieuw_x, y

    def teken_schuine_lijn(self, x1, y1, x2, y2, kleur, dikte):
        tx1, ty1 = self.transformeer_punt(x1, y1)
        tx2, ty2 = self.transformeer_punt(x2, y2)
        self.canvas.create_line(tx1, ty1, tx2, ty2, fill=kleur, width=dikte, capstyle='round')

    def teken_schuine_boog(self, x_offset, cx, cy, r_x, r_y, start_graden, extent_graden, kleur, dikte):
        punten = []
        stappen = 30
        for i in range(stappen + 1):
            hoek_rad = math.radians(start_graden + (extent_graden * i / stappen))
            px = cx + r_x * math.cos(hoek_rad)
            py = cy - r_y * math.sin(hoek_rad)
            tx, ty = self.transformeer_punt(px, py)
            punten.append((tx, ty))
        for i in range(len(punten) - 1):
            self.canvas.create_line(punten[i], punten[i+1], fill=kleur, width=dikte, capstyle='round', joinstyle='round')

    def teken_schuine_line_direct(self, exact_x1, exact_y1, x2, y2, kleur, dikte):
        tx1, ty1 = self.transformeer_punt(exact_x1, exact_y1, cy=150)
        tx2, ty2 = self.transformeer_punt(x2, y2)
        self.canvas.create_line(tx1, ty1, tx2, ty2, fill=kleur, width=dikte, capstyle='round')

    def teken_segment(self, x_offset, segment_naam, actief):
        w, h = 100, 200
        cy = 150
        kleur = '#191970' if actief else '#e0eee0'
        dikte = 16 if actief else 1.2
        dikte_verbinding = 1.0 if actief else 1.2
        
        if segment_naam == 'S1':
            cx_boog = x_offset + 34 + (w - 25) / 2
            cy_boog = cy + (h / 2) / 2
            r_x = (w - 10) / 2
            r_y = (h / 2) / 2
            self.teken_schuine_boog(x_offset, cx_boog, cy_boog, r_x, r_y, 194, 126, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 28, cy + 88 - 0.6 * h/4, x_offset + w - 68, cy + 78 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 58, cy + 30 - 0.6 * h/4, x_offset + w - 40, cy + 30 - 0.3 * h/2, kleur, dikte)
            boog_start_x = cx_boog + r_x * math.cos(math.radians(194))
            boog_start_y = cy_boog - r_y * math.sin(math.radians(194))

        elif segment_naam == 'S2':
            cx_boog = x_offset + 25 + (w - 25) / 2
            cy_boog = (cy + 20 - h/2) + ((cy + 20) - (cy + 20 - h/2)) / 2
            r_x = (w - 25) / 2
            r_y = ((cy + 20) - (cy + 20 - h/2)) / 2
            self.teken_schuine_boog(x_offset, cx_boog, cy_boog, r_x, r_y, 135, 70, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 40, cy + 28 - 0.6 * h/4, x_offset + w - 52, cy + 28 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w + 8, cy - h/2 + 150, x_offset + w + 4, cy + h/2 - 65, kleur, dikte)
            boog_onder_x = cx_boog + r_x * math.cos(math.radians(205))
            boog_onder_y = cy_boog - r_y * math.sin(math.radians(205))
            boog_boven_x = cx_boog + r_x * math.cos(math.radians(135))
            boog_boven_y = cy_boog - r_y * math.sin(math.radians(135))

        elif segment_naam == 'S3':
            self.teken_schuine_lijn(x_offset + 48, cy + 10 - h/2, x_offset + w - 5, cy + 10 - h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 40, cy - 60 - 0.6 * h/4, x_offset + w - 65, cy - 55 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 90, cy - 18 - 0.6 * h/4, x_offset + w - 4, cy - 30 - 0.3 * h/2, kleur, dikte)

        elif segment_naam == 'S4':
            self.teken_schuine_lijn(x_offset + w - 3, cy - h/2 + 120, x_offset + w, cy + h/2 - 75, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w + 2, cy - h/2 + 28, x_offset + w, cy + h/2 - 180, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w + 1, cy - h/2 + 62, x_offset + w, cy + h/2 - 140, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w + 8, cy - h/2 + 158, x_offset + 8 + w, cy + h/2 - 26, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 70, cy + 10 - 0.6 * h/4, x_offset + w - 22, cy - 1 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w - 10, cy + 10 - 0.6 * h/4, x_offset + w - 10, cy + 11 - 0.3 * h/2, kleur, dikte)


    def teken_cijfer(self, x_offset, cijfer):
        actieve_segmenten = self.cijfer_matrix.get(cijfer, [])
        for seg in ['S1', 'S2', 'S3', 'S4']:
            self.teken_segment(x_offset, seg, seg in actieve_segmenten)

    def teken_dubbele_punt(self, x_offset):
        x1, y1 = self.transformeer_punt(x_offset + 15, 115)
        x2, y2 = self.transformeer_punt(x_offset + 15, 185)
        self.canvas.create_oval(x1, y1, x1 + 15, y1 + 15, fill='#191970', outline='')
        self.canvas.create_oval(x2, y2, x2 + 15, y2 + 15, fill='#191970', outline='')

    def update_klok(self):
        self.canvas.delete("all")
        tijd_str = time.strftime("%H%M%S")
        p0, p1, p2, p3, p4, p5 = 50, 190, 400, 540, 760, 900
        self.teken_cijfer(p0, tijd_str[0])
        self.teken_cijfer(p1, tijd_str[1])
        self.teken_dubbele_punt(340)
        self.teken_cijfer(p2, tijd_str[2])
        self.teken_cijfer(p3, tijd_str[3])
        self.teken_dubbele_punt(690)
        self.teken_cijfer(p4, tijd_str[4])
        self.teken_cijfer(p5, tijd_str[5])
        self.root.after(250, self.update_klok)

if __name__ == "__main__":
    root = tk.Tk()
    app = GeoptimaliseerdeVerbondenKlok(root)
    root.mainloop()