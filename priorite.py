import numpy as np

def zoneMorte(x, gap):
    if gap < 0:
        gap = 0    
    
    if x < -gap:
        return x + gap
    elif x < gap:
        return 0
    else:
        return x - gap

class Chemin:
    def __init__(self, pCarrefour, pOrigine, pDestination, pNCycles):
        self.carrefour = pCarrefour
        self.phaseOrigine = pOrigine
        self.phaseDestination = pDestination
        self.nCycles = pNCycles
        
        self.listePhases = []
        
        self.valide = True # Indique si le chemin demandé est possible
        
        if self.phaseOrigine.type == 'Phase':
            phase = self.phaseOrigine
        elif self.phaseOrigine.type == 'Interphase':
            phase = self.phaseOrigine.phaseDestination
        n = 0
        
        if self.phaseDestination.escamotable:
            # Contagem depende da fase precedente
            phasePrecedente = self.carrefour.phasePrecedente(self.phaseDestination, self.carrefour.listePhases)
            
            # Se phasePrecedente for escamotavel, somente é possivel o caminho com nCycles=1
            if phasePrecedente.escamotable and self.nCycles > 1:
                self.valide = False 
             
            else:
                # Caso 1: escamotavel, inicial prioritaria
                if phase.prioritaire:
                    if self.nCycles == 1 and phase == self.phaseDestination:
                        self.listePhases.append(phase)
                    else:
                        self.valide = False
                                        
                # Caso 2: escamotavel, inicial nao prioritaria 
                else:
                    finChemin = False
                    while not finChemin:
                        self.listePhases.append(phase)
                        if phase == phasePrecedente:
                            n += 1
                            if n == self.nCycles:
                                self.listePhases.append(self.phaseDestination)
                                finChemin = True
                        if not finChemin:
                            phase = self.carrefour.phaseSuivante(phase, self.carrefour.cycleBase)
                            while phase.escamotable and phase in self.listePhases:
                                phase = self.carrefour.phaseSuivante(phase, self.carrefour.cycleBase)
                                
        # Caso 3: nao escamotavel       
        else:
            finChemin = False
            while not finChemin:
                self.listePhases.append(phase)
                if phase == self.phaseDestination:
                    n += 1
                    if n == self.nCycles:
                        finChemin = True
                if not finChemin:
                    phase = self.carrefour.phaseSuivante(phase, self.carrefour.cycleBase)
                    while phase.escamotable and phase in self.listePhases:
                        phase = self.carrefour.phaseSuivante(phase, self.carrefour.cycleBase)

        # Calculo dos min, nom e max
        if self.valide:
            self.delaiMinimal, self.delaiNominal, self.delaiMaximal = self.calcDelais()
                        
    def calcDelais(self):
        # Caso especial de ja começar na fase final
        if self.phaseOrigine.type == 'Phase' and len(self.listePhases) == 1:
            delaiMinimal = 0
            delaiNominal = (self.phaseDestination.dureeNominale - self.phaseDestination.dureeBus)//2 - self.carrefour.tempsPhase 
            delaiMaximal = self.phaseDestination.dureeMaximale - self.carrefour.tempsPhase - self.phaseDestination.dureeMaxBus
            
            return (delaiMinimal, delaiNominal, delaiMaximal)
        
        # Todos os outros casos
        if self.phaseOrigine.type == 'Phase':
            delaiMinimal = -min([self.phaseOrigine.dureeMinimale, self.carrefour.tempsPhase])
            delaiMaximal = -min([self.phaseOrigine.dureeMaximale, self.carrefour.tempsPhase])
            delaiNominal = -min([self.phaseOrigine.dureeNominale, self.carrefour.tempsPhase])
        elif self.phaseOrigine.type == 'Interphase':
            delaiMinimal = self.phaseOrigine.duree - self.carrefour.tempsPhase
            delaiMaximal = self.phaseOrigine.duree - self.carrefour.tempsPhase
            delaiNominal = self.phaseOrigine.duree - self.carrefour.tempsPhase
        
        for phase in self.listePhases[:-1]:
            delaiMinimal += phase.dureeMinimale
            delaiMaximal += phase.dureeMaximale
            delaiNominal += phase.dureeNominale
            
            delaiMinimal += self.carrefour.matriceInterphase[phase.numero][self.carrefour.phaseSuivante(phase, self.listePhases).numero].duree
            delaiMaximal += self.carrefour.matriceInterphase[phase.numero][self.carrefour.phaseSuivante(phase, self.listePhases).numero].duree
            delaiNominal += self.carrefour.matriceInterphase[phase.numero][self.carrefour.phaseSuivante(phase, self.listePhases).numero].duree
        
        if not self.phaseDestination.escamotable:
            delaiNominal += (self.phaseDestination.dureeNominale - self.phaseDestination.dureeBus)//2
            delaiMaximal += self.phaseDestination.dureeMaximale -self.phaseDestination.dureeMaxBus
            
        return (delaiMinimal, delaiNominal, delaiMaximal)
        
    def __str__(self):
        strPhases = str(self.listePhases)
        strDurees = str([phase.dureeNominale for phase in self.listePhases])
        
        if self.valide:
            strDelais = str(self.delaiMinimal) + ' ' + str(self.delaiNominal) + ' ' + str(self.delaiMaximal)
            return strPhases + '\n' + strDurees + '\n' + strDelais 
        else:
            return strPhases + '\n' + strDurees + '\n' +  'Pas valide\n'

    def tropCourt(self, delaiApproche):
        return delaiApproche > self.delaiMaximal
    
    def tropLong(self, delaiApproche):
        return delaiApproche < self.delaiMinimal
    
    def deviationNominale(self, delaiApproche):
        if self.phaseDestination.escamotable:
            if len(self.listePhases) == 1: # Para evitar a divisao por zero
                return 0
            else:
                return abs(delaiApproche - self.delaiNominal)/(len(self.listePhases)-1) # Nao considera a ultima fase pq nao mexe nela
        else:
            gap = (self.phaseDestination.dureeNominale - self.phaseDestination.dureeBus)//2
            deviation = zoneMorte(delaiApproche - self.delaiNominal, gap)
            if deviation > 0:
                return deviation/(len(self.listePhases))
            else:
                if len(self.listePhases) == 1: # Para evitar a divisao por zero
                    return 0
                else:
                    return -deviation/(len(self.listePhases)-1) # Nao considera a ultima fase pq nao pode diminuir ela
            
            
    def dureesIdeales(self, delaiApproche):
        if self.phaseDestination.escamotable:
            deltaTotal =  delaiApproche - self.delaiNominal    
        else:
            gap = (self.phaseDestination.dureeNominale - self.phaseDestination.dureeMaxBus)//2
            deltaTotal = zoneMorte(delaiApproche - self.delaiNominal, gap)
        
        minDurees = [phase.dureeMinimale for phase in self.listePhases]
        if self.carrefour.phaseActuelle.type == 'Phase' and self.carrefour.tempsPhase > minDurees[0]:
            minDurees[0] = self.carrefour.tempsPhase
        nomDurees = [phase.dureeNominale for phase in self.listePhases]
        maxDurees = [phase.dureeMaximale for phase in self.listePhases]
        
        minDurees[-1] = nomDurees[-1] # Nao permite encolher a ultima fase nunca
        if self.phaseDestination.escamotable:
            maxDurees[-1] = nomDurees[-1] # Nao permite aumentar a ultima fase se for escamotavel
        
        durees = nomDurees.copy()
        if self.carrefour.tempsPhase > durees[0]:
            durees[0] = self.carrefour.tempsPhase
        
        if (deltaTotal > 0):
            for i in range(deltaTotal):
                rapports = [nominal/(duree+1) if duree < maximal else 0 \
                            for duree,nominal,maximal in zip(durees, nomDurees, maxDurees)]
                durees[np.argmax(rapports)] += 1
        elif (deltaTotal < 0):
            for i in range(-deltaTotal):
                rapports = [(duree-1)/nominal if duree > minimal else 0 \
                            for duree,nominal,minimal in zip(durees, nomDurees, minDurees)]
                durees[np.argmax(rapports)] -= 1
        
        return durees        
            
    
    def getPlan(self, durees):
        plan = []
        for phase,duree in zip(self.listePhases, durees):
            if phase in plan:
                break
            phase.duree = duree
            plan.append(phase)
        return plan
                     
def meilleurChemin(carrefour, delaiApproche):
    #Lista todos os caminhos possiveis
    cheminsPossibles = []
    listePhasesPrioritaires = [phase for phase in carrefour.listePhases if phase.prioritaire]
    
    for phasePrioritaire in listePhasesPrioritaires:
        n = 1
        chemin = Chemin(carrefour, carrefour.phaseActuelle, phasePrioritaire, n)
        while chemin.valide:
            if chemin.tropLong(delaiApproche):
                break
            if not chemin.tropCourt(delaiApproche):
                cheminsPossibles.append(chemin)
            n += 1
            chemin = Chemin(carrefour, carrefour.phaseActuelle, phasePrioritaire, n)
    # Escolhe melhor caminho
    deviations = [chemin.deviationNominale(delaiApproche) for chemin in cheminsPossibles]
    if len(cheminsPossibles) > 0: # Se a lista nao for vazia
        return cheminsPossibles[np.argmin(deviations)]
    else:
        return None

