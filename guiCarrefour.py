import tkinter as tk

class AppIntersection(tk.Frame):
    def __init__(self, master, pCarrefour):
        tk.Frame.__init__(self, master)
        self.pack()
        self.carrefour = pCarrefour
        self.pause = False
        
        self.diagrammeLignes = DiagrammeLignes(self)
        self.buttonPause = tk.Button(self, text='Pause', command = self.pauser)
        self.buttonPhases = [tk.Button(self, text='Phase '+str(i), command=lambda i=i:self.soliciterPhase(i)) \
                         for i,phase in enumerate(self.carrefour.listePhases) if phase.escamotable and not phase.prioritaire]
        self.entryDelai = tk.Entry(self, width=5)
        self.buttonDelai = tk.Button(self, text='Envoyer', command=lambda: self.envoyerDelai(self.entryDelai.get()))
        
        self.diagrammeLignes.pack()
        self.buttonPause.pack()
        for button in self.buttonPhases:
            button.pack()
        self.entryDelai.pack()
        self.buttonDelai.pack()
        
        self.after(0, self.cycleCarrefour)
    
    def pauser(self):
        self.pause = not self.pause
     
    def soliciterPhase(self,n):
        self.carrefour.soliciterPhase(n)
    
    def envoyerDelai(self, delaiString):
        try:
            delai = int(delaiString)
            self.carrefour.delaiApproche = delai
        except ValueError:
            pass
    
    def cycleCarrefour(self):
        if (not self.pause):
            lignes, transition = self.carrefour.update()
            couleurs = [ligne.couleur for ligne in lignes]
            compteursRouge = [ligne.compteurRouge for ligne in lignes]
            phase = self.carrefour.phaseActuelle.numero if self.carrefour.phaseActuelle.type == 'Phase' else None
            self.diagrammeLignes.add(couleurs, transition, phase, self.carrefour.tempsPhase, self.carrefour.delaiApproche, compteursRouge)
            
        self.after(300, self.cycleCarrefour)
    
class DiagrammeLignes(tk.Canvas):
    def __init__(self, master):
        self.nomLignes = master.carrefour.nomLignes()
        self.nombreLignes = len(self.nomLignes)
        self.compteursRouge = [0 for i in range(self.nombreLignes)]
        
        self.x0 = 40
        self.y0 = 45
        self.lx = 18
        self.ly = 10
        self.maxLen = 65
        
        tk.Canvas.__init__(self, master, width=(self.maxLen+4)*self.lx, height=3*self.ly*(self.nombreLignes+2))
        self.pause = False
        
        self.bufferLignes = []
        self.bufferTransitions = []
        self.bufferPhases = []
        self.bufferTemps = []
        self.bufferDelais = []
        
        self.after(0, self.updateDiagramme)
    
    def add(self, couleurs, transition, phase, tempsPhase, delaiApproche, compteursRouge):
        self.bufferLignes.append(couleurs)
        self.bufferTransitions.append(transition)
        self.bufferPhases.append(phase)
        self.bufferTemps.append(tempsPhase)
        self.bufferDelais.append(delaiApproche)
        
        if (len(self.bufferLignes) > self.maxLen):
            self.bufferLignes.pop(0)
            self.bufferTransitions.pop(0)
            self.bufferPhases.pop(0)
            self.bufferTemps.pop(0)
            self.bufferDelais.pop(0)
            
        self.compteursRouge = compteursRouge
        
    def updateDiagramme(self):
        self.delete('all')
        
        # Nome das linhas
        for i,nom in enumerate(self.nomLignes):
            self.create_text(self.x0-15, self.y0+3*self.ly*i+self.ly//2, text=nom)
        
        # Barra no inicio
        self.create_line(self.x0, self.y0, self.x0, self.y0+3*self.ly*self.nombreLignes-2*self.ly, width=2)
        
        for i, (vecCouleurs,transition,phase,temps,delai) in enumerate(zip(self.bufferLignes, self.bufferTransitions, self.bufferPhases, self.bufferTemps, self.bufferDelais)):
            x = self.x0 + self.lx*i
            
            # Barra a cada segundo
            self.create_line(x+self.lx, self.y0, x+self.lx, self.y0+3*self.ly*self.nombreLignes-2*self.ly, fill='gray')            
            
            for j,couleur in enumerate(vecCouleurs):
                y = self.y0 + 3*self.ly*j
                
                # Status de cada linha
                self.create_rectangle(x, y, x+self.lx, y+self.ly, fill=couleur, outline='')
                if couleur == 'green':
                    self.create_line(x, y+self.ly//2, x+self.lx, y+self.ly//2)
            
            # Barra separadora de fases
            if transition:
                self.create_line(x, self.y0, x, self.y0+3*self.ly*self.nombreLignes-2*self.ly, width=2)
            
            # Numero da fase
            if phase != None:
                self.create_text(x+self.lx//2, self.y0-25, text=str(phase), fill='red')
                
            # Tempo na fase
            self.create_text(x+self.lx, self.y0-10, text=str(temps))
            
            # Delai Approche
            if delai >= 0:
                self.create_text(x+self.lx, self.y0+3*self.ly*self.nombreLignes-self.ly, text=str(delai))
        
        # Compteur Rouge
        for i,temps in enumerate(self.compteursRouge):
            self.create_text(self.x0 + self.lx*(self.maxLen+1), self.y0+3*self.ly*i+self.ly//2, text=str(temps))
        
        self.after(100, self.updateDiagramme)
    
