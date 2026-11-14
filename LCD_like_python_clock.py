import tkinter as tk
import time
import math

class SchaalbareMicroLCDKlok:
    def __init__(self, root):
        self.root = root
        self.root.title("Micro-LCD Schaalbare 4-Segmenten Klok")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        # Zachte LCD-achtergrondkleur (lichtgrijs/groenig zoals echt reflectief LCD)
        self.lcd_bg = '#d8e3d8'
        self.segment_aan = '#151828'
        self.segment_uit = '#cad6ca'
        
        self.root.configure(bg=self.lcd_bg)
        
        # Startgrootte in pixels (ca. 6 tot 8 mm cijferhoogte op een standaard monitor)
        # Schaal 0.16 betekent: oorspronkelijke hoogte 200px * 0.16 = 32px (ca. 7-8 mm op scherm)
        self.schaal = 0.18
        self.min_schaal = 0.08  # Ca. 3-4 mm cijferhoogte
        self.max_schaal = 0.50  # Ca. 15-20 mm cijferhoogte
        
        self.basis_breedte = 1100
        self.basis_hoogte = 280
        
        self.canvas = tk.Canvas(
            root, 
            width=int(self.basis_breedte * self.schaal), 
            height=int(self.basis_hoogte * self.schaal), 
            bg=self.lcd_bg, 
            highlightthickness=1,
            highlightbackground="#9aa89a"
        )
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
        
        # Muisbediening: slepen, rechtsklik sluiten, scrollwiel of +/- om te schalen
        self.canvas.bind("<Button-1>", self.start_slepen)
        self.canvas.bind("<B1-Motion>", self.doe_slepen)
        self.canvas.bind("<Button-3>", lambda e: self.root.destroy())
        
        # Scrollwiel voor traploos vergroten/verkleinen (Windows/Mac/Linux)
        self.canvas.bind("<MouseWheel>", self.scroll_schaal)
        self.canvas.bind("<Button-4>", lambda e: self.pas_schaal_aan(0.02))
        self.canvas.bind("<Button-5>", lambda e: self.pas_schaal_aan(-0.02))
        
        # Toetsenbord + en - om te schalen, Escape om te sluiten
        self.root.bind("<plus>", lambda e: self.pas_schaal_aan(0.02))
        self.root.bind("<equal>", lambda e: self.pas_schaal_aan(0.02))
        self.root.bind("<minus>", lambda e: self.pas_schaal_aan(-0.02))
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.centreer_venster()
        self.update_klok()

    def centreer_venster(self):
        b = int(self.basis_breedte * self.schaal)
        h = int(self.basis_hoogte * self.schaal)
        scherm_breedte = self.root.winfo_screenwidth()
        scherm_hoogte = self.root.winfo_screenheight()
        x = (scherm_breedte // 2) - (b // 2)
        y = (scherm_hoogte // 2) - (h // 2)
        self.root.geometry(f"{b}x{h}+{x}+{y}")

    def scroll_schaal(self, event):
        if event.delta > 0:
            self.pas_schaal_aan(0.02)
        else:
            self.pas_schaal_aan(-0.02)

    def pas_schaal_aan(self, delta):
        nieuwe_schaal = round(self.schaal + delta, 3)
        if self.min_schaal <= nieuwe_schaal <= self.max_schaal:
            self.schaal = nieuwe_schaal
            b = int(self.basis_breedte * self.schaal)
            h = int(self.basis_hoogte * self.schaal)
            self.canvas.config(width=b, height=h)
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry(f"{b}x{h}+{x}+{y}")
            self.teken_nu()

    def start_slepen(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def doe_slepen(self, event):
        x = self.root.winfo_x() + (event.x - self.start_x)
        y = self.root.winfo_y() + (event.y - self.start_y)
        self.root.geometry(f"+{x}+{y}")

    def transformeer_punt(self, x, y, cy=150, schuinte=0.20):
        nieuw_x = x + schuinte * (cy - y)
        return nieuw_x * self.schaal, y * self.schaal

    def teken_schuine_lijn(self, x1, y1, x2, y2, kleur, dikte):
        tx1, ty1 = self.transformeer_punt(x1, y1)
        tx2, ty2 = self.transformeer_punt(x2, y2)
        geschaalde_dikte = max(1.0, dikte * self.schaal)
        self.canvas.create_line(tx1, ty1, tx2, ty2, fill=kleur, width=geschaalde_dikte, capstyle='round')

    def teken_schuine_boog(self, x_offset, cx, cy, r_x, r_y, start_graden, extent_graden, kleur, dikte):
        punten = []
        stappen = 30
        for i in range(stappen + 1):
            hoek_rad = math.radians(start_graden + (extent_graden * i / stappen))
            px = cx + r_x * math.cos(hoek_rad)
            py = cy - r_y * math.sin(hoek_rad)
            tx, ty = self.transformeer_punt(px, py)
            punten.append((tx, ty))
        geschaalde_dikte = max(1.0, dikte * self.schaal)
        for i in range(len(punten) - 1):
            self.canvas.create_line(punten[i], punten[i+1], fill=kleur, width=geschaalde_dikte, capstyle='round', joinstyle='round')

    def teken_segment(self, x_offset, segment_naam, actief):
        w, h = 100, 200
        cy = 150
        kleur = self.segment_aan if actief else self.segment_uit
        dikte = 16 if actief else 1.2
        
        if segment_naam == 'S1':
            cx_boog = x_offset + 34 + (w - 25) / 2
            cy_boog = cy + (h / 2) / 2
            r_x = (w - 10) / 2
            r_y = (h / 2) / 2
            self.teken_schuine_boog(x_offset, cx_boog, cy_boog, r_x, r_y, 194, 126, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 28, cy + 88 - 0.6 * h/4, x_offset + w - 68, cy + 78 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 58, cy + 30 - 0.6 * h/4, x_offset + w - 40, cy + 30 - 0.3 * h/2, kleur, dikte)

        elif segment_naam == 'S2':
            cx_boog = x_offset + 25 + (w - 25) / 2
            cy_boog = (cy + 20 - h/2) + ((cy + 20) - (cy + 20 - h/2)) / 2
            r_x = (w - 25) / 2
            r_y = ((cy + 20) - (cy + 20 - h/2)) / 2
            self.teken_schuine_boog(x_offset, cx_boog, cy_boog, r_x, r_y, 135, 70, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 40, cy + 28 - 0.6 * h/4, x_offset + w - 52, cy + 28 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w + 8, cy - h/2 + 150, x_offset + w + 4, cy + h/2 - 65, kleur, dikte)

        elif segment_naam == 'S3':
            self.teken_schuine_lijn(x_offset + 48, cy + 10 - h/2, x_offset + w - 5, cy + 10 - h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 40, cy - 60 - 0.6 * h/4, x_offset + w - 65, cy - 55 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + 93, cy - 22 - 0.6 * h/4, x_offset + w - 4, cy - 30 - 0.3 * h/2, kleur, dikte)
            self.teken_schuine_lijn(x_offset + w + 2, cy - h/2 + 28, x_offset + w, cy + h/2 - 180, kleur, dikte)

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
        r = max(1.5, 15 * self.schaal)
        self.canvas.create_oval(x1, y1, x1 + r, y1 + r, fill=self.segment_aan, outline='')
        self.canvas.create_oval(x2, y2, x2 + r, y2 + r, fill=self.segment_aan, outline='')

    def teken_nu(self):
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

    def update_klok(self):
        self.teken_nu()
        self.root.after(250, self.update_klok)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchaalbareMicroLCDKlok(root)
    root.mainloop()
