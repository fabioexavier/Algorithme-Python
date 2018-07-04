import tkinter as tk

class AppIntersection(tk.Frame):
    def __init__(self, master, pCarrefour):
        tk.Frame.__init__(self, master)
        self.pack()
        self.carrefour = pCarrefour
        self.pause = False
        
        self.diagrammeLignes = DiagrammeLignes(self)
        self.buttonPause = tk.Button(self, text='Pause', command = self.pauser)
        
        
        self.buttonPhase = [tk.Button(self, text='Phase '+str(i), command=lambda i=i:self.soliciterPhase(i)) \
                         for i,phase in enumerate(self.carrefour.listePhases) if phase.escamotable]
        
        self.diagrammeLignes.pack()
        self.buttonPause.pack()
        for button in self.buttonPhase:
            button.pack()
        
        self.after(0, self.cycleCarrefour)
    
    def pauser(self):
        self.pause = not self.pause
     
    def soliciterPhase(self,n):
        self.carrefour.soliciterPhase(n)
    
    def cycleCarrefour(self):
        if (not self.pause):
            lignes, transition = self.carrefour.update()
            couleurs = [ligne.couleur for ligne in lignes]
            self.diagrammeLignes.add(couleurs, transition)
            
        self.after(200, self.cycleCarrefour)
    
class DiagrammeLignes(tk.Canvas):
    def __init__(self, master):
        self.nomLignes = master.carrefour.nomLignes()
        self.nombreLignes = len(self.nomLignes)
        
        tk.Canvas.__init__(self, master, width=1000, height=30*self.nombreLignes)
        self.pause = False
        
        self.x0 = 20
        self.y0 = 10
        
        self.bufferLignes = []
        self.bufferTransitions = []
        self.maxLen = 90
        
        self.after(0, self.updateDiagramme)
    
    def add(self, couleurs, transition):
        self.bufferLignes.append(couleurs)
        self.bufferTransitions.append(transition)
        if (len(self.bufferLignes) > self.maxLen):
            self.bufferLignes.pop(0)
            self.bufferTransitions.pop(0)
    
    def updateDiagramme(self):
        self.delete('all')
        
        for i,nom in enumerate(self.nomLignes):
            self.create_text(self.x0-10, self.y0+30*i+5, text=nom)
        
        self.create_line(self.x0, self.y0, self.x0, self.y0+30*self.nombreLignes-20)      
        for i,vecCouleurs in enumerate(self.bufferLignes):
            for j,couleur in enumerate(vecCouleurs):
                x = self.x0+10*i
                y = self.y0+30*j
                self.create_rectangle(x, y, x+10, y+10, fill=couleur, outline='')
                if couleur == 'green':
                    self.create_line(x, y+5, x+10, y+5)
            if self.bufferTransitions[i]:
                self.create_line(x, self.y0, x, self.y0+30*self.nombreLignes-20)       
        
        self.after(100, self.updateDiagramme)
    
