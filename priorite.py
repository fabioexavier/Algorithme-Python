import numpy as np

def suivant(element, liste):
    index = liste.index(element) + 1
    if index == len(liste):
        index = 0
    return liste[index]

def zoneMorte(x, gap):
    if gap < 0:
        gap = 0
    if x <= -gap:
        return x + gap
    elif x <= gap:
        return 0
    else:
        return x - gap


class Chemin:
    def __init__(self, pOrigine, pCarrefour, pListePhases, pSommeMin=0, pSommeNom=0, pSommeMax=0):
        self.origine = pOrigine
        self.carrefour = pCarrefour
        self.listePhases = pListePhases
        self.sommeMin = pSommeMin
        self.sommeNom = pSommeNom
        self.sommeMax = pSommeMax
        
    def append(self, phase):
        self.listePhases.append(phase)
        if len(self) == 1:
            if self.origine.type == 'Phase':
                self.sommeMin = phase.dureeMinimale - self.carrefour.tempsPhase if phase.dureeMinimale - self.carrefour.tempsPhase > 0 else 0
                self.sommeNom = phase.dureeNominale - self.carrefour.tempsPhase if phase.dureeNominale - self.carrefour.tempsPhase > 0 else 0
                self.sommeMax = phase.dureeMaximale - self.carrefour.tempsPhase if phase.dureeMaximale - self.carrefour.tempsPhase > 0 else 0
            elif self.origine.type == 'Interphase':
                self.sommeMin = self.origine.duree - self.carrefour.tempsPhase + phase.dureeMinimale
                self.sommeNom = self.origine.duree - self.carrefour.tempsPhase + phase.dureeNominale
                self.sommeMax = self.origine.duree - self.carrefour.tempsPhase + phase.dureeMaximale             
        else:
            self.sommeMin += self.carrefour.matriceInterphase[self.listePhases[-2].numero][self.listePhases[-1].numero].duree
            self.sommeNom += self.carrefour.matriceInterphase[self.listePhases[-2].numero][self.listePhases[-1].numero].duree
            self.sommeMax += self.carrefour.matriceInterphase[self.listePhases[-2].numero][self.listePhases[-1].numero].duree
            
            self.sommeMin += phase.dureeMinimale
            self.sommeNom += phase.dureeNominale
            self.sommeMax += phase.dureeMaximale
    
    def deviation(self, delaiApproche):
        deviationTotale = delaiApproche - self.delaiNominal()
        return abs(deviationTotale)
    
    def dureesIdeales(self, delaiApproche):
        if self.listePhases[-1].exclusive:
            instantOuverture = 0
        else:
            instantOuverture = (self.listePhases[-1].dureeNominale - self.listePhases[-1].dureeBus)//2
                
        # deltaTotal é o quanto se tem que aumentar a duraçao do caminho em relacao ao que se faria no modo sem prioridade
        deltaTotal =  zoneMorte(delaiApproche - self.delaiNominal(), instantOuverture - (self.listePhases[-1].dureeMaxBus - self.listePhases[-1].dureeBus))
        
        minDurees = [phase.dureeMinimale for phase in self.listePhases]
        if self.carrefour.phaseActuelle.type == 'Phase' and self.carrefour.tempsPhase > minDurees[0]:
            minDurees[0] = self.carrefour.tempsPhase
            
        nomDurees = [phase.dureeNominale for phase in self.listePhases]
                    
        maxDurees = [phase.dureeMaximale for phase in self.listePhases]
        
        minDurees[-1] = nomDurees[-1] # Nao permite encolher a ultima fase nunca
        if self.listePhases[-1].exclusive:
            maxDurees[-1] = nomDurees[-1] # Nao permite aumentar a ultima fase se for exclusiva
        
        durees = nomDurees.copy()
        # Caso ja tenha ultrapassado o nominal da fase
        if self.carrefour.phaseActuelle.type == 'Phase' and self.carrefour.tempsPhase > nomDurees[0]:
            if len(self) > 1: # Nao faz a correçao se ja estiver na ultima fase
                durees[0] = self.carrefour.tempsPhase
        
        if (deltaTotal > 0):
            for i in range(deltaTotal):
                rapports = [nominal/(duree+1) if duree < maximal else 0 \
                            for duree,nominal,maximal in zip(durees, nomDurees, maxDurees)]
                if max(rapports) > 0:
                    durees[np.argmax(rapports)] += 1
        elif (deltaTotal < 0):
            for i in range(-deltaTotal):
                rapports = [(duree-1)/nominal if duree > minimal else 0 \
                            for duree,nominal,minimal in zip(durees, nomDurees, minDurees)]
                if max(rapports) > 0:
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
    
    def delaiMinimal(self):
        # Caso especial de ja começar na fase final
        if self.origine.type == 'Phase' and len(self) == 1:
            return 0
        else:
            return self.sommeMin - self.listePhases[-1].dureeMinimale
    
    def delaiNominal(self):
        if self.listePhases[-1].exclusive:
            instantOuverture = 0
        else:
            instantOuverture = (self.listePhases[-1].dureeNominale - self.listePhases[-1].dureeBus)//2
                
        # Caso especial de ja começar na fase final
        if self.origine.type == 'Phase' and len(self) == 1:
            return instantOuverture - self.carrefour.tempsPhase
        
        else:
            return self.sommeNom - (self.listePhases[-1].dureeNominale - instantOuverture)
    
    def delaiMaximal(self):
        instantOuverture = self.listePhases[-1].dureeMaximale - self.listePhases[-1].dureeMaxBus
        
        # Caso especial de ja começar na fase final
        if self.origine.type == 'Phase' and len(self) == 1:
            return instantOuverture - self.carrefour.tempsPhase if instantOuverture - self.carrefour.tempsPhase > 0 else 0
        else:
            return self.sommeMax - self.listePhases[-1].dureeMaxBus
            
    def copy(self):
        return Chemin(self.origine, self.carrefour, self.listePhases.copy(), self.sommeMin, self.sommeNom, self.sommeMax)
    
    def __len__(self):
        return len(self.listePhases)
    
    def __str__(self):
        strPhases = str(self.listePhases)
        strDurees = str([phase.dureeNominale for phase in self.listePhases])
        strDelais = str(self.delaiMinimal()) + ' ' + str(self.delaiNominal()) + ' ' + str(self.delaiMaximal())
        
        return strPhases + '\n' + strDurees + '\n' + strDelais 
    __repr__ = __str__
    
    
    
class Graphe:
    def __init__(self, pMatrice, pSommets):
        self.matrice = pMatrice
        self.listeSommets = pSommets
        self.listeChemins = []

    def chemins(self, origine, destination, carrefour, delaiApproche):
        cheminBase = Chemin(origine, carrefour, [])
        if origine.type == 'Interphase':
            origine = origine.phaseDestination
        
        if origine in self.listeSommets:
            self.rechercheChemins(origine, destination, cheminBase, delaiApproche)
        chemins = self.listeChemins
        self.listeChemins = []
        
        return chemins

    def rechercheChemins(self, origine, destination, chemin, delaiApproche):
        chemin.append(origine)
#        print(origine, chemin.sommeMax, chemin.delaiMaximal())
        continuer = False
        
        if origine == destination:
            self.listeChemins.append(chemin)
            if not destination.escamotable:
                continuer = True
        else:
            phaseInterdite = origine.escamotable and origine in chemin.listePhases[:-1]
            if (delaiApproche > chemin.sommeMin or len(chemin) < len(self.listeSommets)) and not phaseInterdite:
                continuer = True
        
        if continuer:
            i = self.listeSommets.index(origine)
            enfants = [sommet for j,sommet in enumerate(self.listeSommets) if self.matrice[i,j] == 1]
            for sommet in enfants:
                self.rechercheChemins(sommet, destination, chemin.copy(), delaiApproche)
        

def meilleurChemin(carrefour):        
    listeChemins = []
    
    listePhasesPrioritaires = [phase for phase in carrefour.listePhases if phase.prioritaire]
    for phasePrioritaire in listePhasesPrioritaires:
#        phaseInterdite = SE FOR EXCLUSIVA E NENHUMA DAS POSSIVEIS FASES SEGUINTES SOLICITADAS
        phaseInterdite = False
        if not phaseInterdite:
            sommets = [phase for phase in carrefour.listePhases if phase in carrefour.cycleBase or phase == phasePrioritaire]
#            print(sommets)
            numeroSommets = [sommet.numero for sommet in sommets]
            matriceSubgraphe = carrefour.matriceGraphe[numeroSommets,:][:, numeroSommets]
#            print(matriceSubgraphe)
            subgraphe = Graphe(matriceSubgraphe, sommets)
            
            listeChemins += subgraphe.chemins(carrefour.phaseActuelle, phasePrioritaire, carrefour, carrefour.delaiApproche)
            
    cheminsPossibles = []
    cheminsLongs = []
    
    for chemin in listeChemins:
        if carrefour.delaiApproche <= chemin.delaiMaximal():
            if carrefour.delaiApproche >= chemin.delaiMinimal():
                cheminsPossibles.append(chemin)
            else:
                cheminsLongs.append(chemin)
            
    if cheminsPossibles: # Se nao estiver vazia
        deviations = [chemin.deviation(carrefour.delaiApproche) for chemin in cheminsPossibles]
        meilleurChemin = cheminsPossibles[np.argmin(deviations)]
    else:
        minimums = [chemin.delaiMinimal() for chemin in cheminsLongs]
        meilleurChemin = cheminsLongs[np.argmin(minimums)]
        
    return meilleurChemin

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    



