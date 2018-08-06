import tkinter as tk

class AppIntersection(tk.Frame):
    def __init__(self, master, pCarrefour):
        tk.Frame.__init__(self, master)
        self.pack()
        self.carrefour = pCarrefour
        self.pause = False
        
        self.codes = [code for code in self.carrefour.codesPriorite if code != 0]
        self.vehiculesParCode = 3
        
        # Criaçao dos widgets
        self.diagrammeLignes = DiagrammeLignes(self)
                
        self.buttonPause = tk.Button(self, text='Pause', command = self.pauser)
        
        self.frameEscamotable = tk.Frame(self)
        self.commandesEscamotables = [CommandeEscamotable(self.frameEscamotable, phase, lambda i=phase.numero:self.soliciterPhase(i)) \
                                     for phase in self.carrefour.listePhases if phase.escamotable and not phase.codePriorite]
        
#        self.buttonsPhase = [tk.Button(self.frameEscamotable, text='Phase '+str(i), command=lambda i=i:self.soliciterPhase(i)) \
#                         for i,phase in enumerate(self.carrefour.listePhases) if phase.escamotable and not phase.codePriorite]
#        self.stringsPhase = [tk.stringVar() for button in self.buttonsPhase]
#        self.labelsPhase = [tk.Label(self.frameEscamotable, text='o') for phase in self.carrefour.listePhases if phase.escamotable and not phase.codePriorite]
        
        
        self.framePriorite = tk.Frame(self)
        self.entriesDelai = [tk.Entry(self.framePriorite, width=15) for i in range(len(self.codes)*self.vehiculesParCode)]
        self.buttonsDelai = [tk.Button(self.framePriorite, text='Envoyer', command=lambda i=i:self.envoyerDelai(i)) \
                            for i in range(len(self.codes)*self.vehiculesParCode)]
        
        # Posicionamento
        self.diagrammeLignes.grid(column=0, row=0, columnspan=2)
        self.buttonPause.grid(column=0, row=1, columnspan=2, pady=15)
        self.frameEscamotable.grid(column=0, row=2)
        self.framePriorite.grid(column=1, row=2)
        
        # Frame fases escamotaveis
        for i,commande in enumerate(self.commandesEscamotables):
            commande.button.grid(column=i, row=0, padx=15)
            commande.label.grid(column=i, row=1, padx=15)

        # Frame demandas prioridade
        for i,code in enumerate(self.codes):
            tk.Label(self.framePriorite, text='Code '+str(code), font='Helvetica 10 bold').grid(column=2*i, row=0, columnspan=2)
            
        for i,(entry,button) in enumerate(zip(self.entriesDelai, self.buttonsDelai)):
            entry.grid(column=2*(i//self.vehiculesParCode), row=1+i%self.vehiculesParCode, padx=5, pady=5)
            button.grid(column=2*(i//self.vehiculesParCode)+1, row=1+i%self.vehiculesParCode, padx=5, pady=5)
        
        self.after(0, self.cycleCarrefour)
        self.after(0, self.cycleEscamotables)
    
    def pauser(self):
        self.pause = not self.pause
     
    def soliciterPhase(self,n):
        self.carrefour.soliciterPhase(n)
    
    def envoyerDelai(self, index):
        try:
            delaiApproche = int(self.entriesDelai[index].get())
            codePriorite = self.codes[index//self.vehiculesParCode]
            codeVehicule = index
            self.carrefour.demanderPriorite(delaiApproche, codePriorite, codeVehicule)
            
        except ValueError:
            pass
    
    def cycleCarrefour(self):
        if not self.pause:
            self.carrefour.update()
            
            lignes = self.carrefour.listeLignes
            couleurs = [ligne.couleur for ligne in lignes]
            compteursRouge = [ligne.compteurRouge for ligne in lignes]
            
            transition = self.carrefour.transition
            phase = self.carrefour.phaseActuelle.numero if self.carrefour.phaseActuelle.type == 'phase' else None
            
            delaisApproche = [None]*len(self.codes)*self.vehiculesParCode
            for demande in self.carrefour.demandesPriorite:
                delaisApproche[demande.codeVehicule] = demande.delaiApproche            
            
            self.diagrammeLignes.add(couleurs, transition, phase, self.carrefour.tempsPhase, delaisApproche, compteursRouge)
            
        self.after(500, self.cycleCarrefour)
    
    def cycleEscamotables(self):
        for commande in self.commandesEscamotables:
            if commande.phase.solicitee:
                commande.stringVar.set(u'\u2022')
            else:
                commande.stringVar.set('')
        
        self.after(100, self.cycleEscamotables)

class CommandeEscamotable:
    def __init__(self, master, phase, function):
        self.phase = phase
        self.button = tk.Button(master, text=str(phase), command=function)
        self.stringVar = tk.StringVar()
        self.label = tk.Label(master, textvariable=self.stringVar, font=('', 24))
    
class DiagrammeLignes(tk.Canvas):
    def __init__(self, master):
        self.nomLignes = [ligne.nom for ligne in master.carrefour.listeLignes]
        self.nombreLignes = len(master.carrefour.listeLignes)
        self.compteursRouge = [ligne.compteurRouge for ligne in master.carrefour.listeLignes]
        
        self.x0 = 40
        self.y0 = 45
        self.lx = 18
        self.ly = 10
        self.maxLen = 40
        
        self.width = (self.maxLen+4)*self.lx
        self.height = 3*self.ly*(self.nombreLignes+1)+15*len(master.codes)*master.vehiculesParCode
        
        tk.Canvas.__init__(self, master, width=self.width, height=self.height)
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
        
        for i, (vecCouleurs,transition,phase,temps,delais) in enumerate(zip(self.bufferLignes, self.bufferTransitions, self.bufferPhases, self.bufferTemps, self.bufferDelais)):
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
            for j,delai in enumerate(delais):
                if delai != None:
                    self.create_text(x+self.lx, self.y0+3*self.ly*self.nombreLignes+(j-1)*15+8, text=str(delai))
        
        # Compteur Rouge
        for i,temps in enumerate(self.compteursRouge):
            self.create_text(self.x0 + self.lx*(self.maxLen+1), self.y0+3*self.ly*i+self.ly//2, text=str(temps))
        
        self.after(100, self.updateDiagramme)
    
