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
        self.listeDurees = []
        
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
    
    def deviation(self):
        deviationTotale = self.carrefour.delaiApproche - self.delaiNominal()
        return abs(deviationTotale)
    
    def calcDureesIdeales(self):
        if self.listePhases[-1].exclusive:
            instantOuverture = 0
        else:
            instantOuverture = (self.listePhases[-1].dureeNominale - self.listePhases[-1].dureeBus)//2
                
        # deltaTotal é o quanto se tem que aumentar a duraçao do caminho em relacao ao que se faria no modo sem prioridade
        deltaTotal =  zoneMorte(self.carrefour.delaiApproche - self.delaiNominal(), instantOuverture - (self.listePhases[-1].dureeMaxBus - self.listePhases[-1].dureeBus))
        
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
        
        self.listeDurees = durees        
    
    def durees(self):
        if not self.listeDurees: # se estiver vazia
            self.calcDureesIdeales()
        
        return self.listeDurees
    
    def tempsRouge(self):
        tempsRouge = [ligne.compteurRouge for ligne in self.carrefour.listeLignes]
        
        for ligne in self.carrefour.listeLignes:
            if ligne.compteurRouge > 0:
                if self.origine.type == 'Phase':
                    tempsRouge[ligne.numero] -= self.carrefour.tempsPhase
                elif self.origine.type == 'Interphase':
                    tempsRouge[ligne.numero] += self.origine.duree - self.carrefour.tempsPhase
                    
                finished = False
                for phase1, phase2, duree in zip(self.listePhases, self.listePhases[1:], self.durees()):
                    if phase1.lignesActives[ligne.numero] == True:
                        finished = True
                        break
                    tempsRouge[ligne.numero] += duree
                    tempsRouge[ligne.numero] += self.carrefour.matriceInterphase[phase1.numero][phase2.numero].duree
                    
                if not finished:
                    phase1 = self.listePhases[-1]
                    while not phase1.lignesActives[ligne.numero]:
                        phase2 = suivant(phase1, self.carrefour.listePhases)
                        while not phase2.solicitee:
                            phase2 = suivant(phase2, self.carrefour.listePhases)
                        tempsRouge[ligne.numero] += phase1.dureeNominale
                        tempsRouge[ligne.numero] += self.carrefour.matriceInterphase[phase1.numero][phase2.numero].duree
                        phase1 = phase2
        
        return max(tempsRouge)
    
    def getPlan(self):
        plan = []
        for phase,duree in zip(self.listePhases, self.durees()):
            if phase in plan:
                break
            phase.duree = duree
            plan.append(phase)
        return plan
    
    def copy(self):
        return Chemin(self.origine, self.carrefour, self.listePhases.copy(), self.sommeMin, self.sommeNom, self.sommeMax)
    
    def __len__(self):
        return len(self.listePhases)
    
    def __str__(self):
        strPhases = str(self.listePhases)
        strDureesNominales = str([phase.dureeNominale for phase in self.listePhases])
        strDurees = str(self.durees())
        strDelais = str(self.delaiMinimal()) + ' ' + str(self.delaiNominal()) + ' ' + str(self.delaiMaximal())
        strDeviation = 'Deviation: ' + str(self.deviation())
        strTemps = 'Temps Rouge Max: ' + str(self.tempsRouge())
        
        return strPhases + '\n' + strDureesNominales + '\n' + strDurees + '\n' + strDelais + '\n' + strDeviation + '\n' + strTemps + '\n'
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
            # phaseInterdite significa que ela é escamotavel e ja esta no caminho, e assim nao faz sentido adicionar de novo
            # OBS: FALTA TRATAR POSSIBILIDADE DE REPETIR DUAS VEZES A MESMA FASE ESCAMOTAVEL CASO SEJA PENE
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
        i = carrefour.listePhases.index(phasePrioritaire)
        destinations = [phase for j,phase in enumerate(carrefour.listePhases) if carrefour.matriceGraphe[i,j] == 1]
        
        if any(phase.solicitee for phase in destinations): # Se pelo menos uma das possiveis fases destino for solicitada
            sommets = [phase for phase in carrefour.listePhases if phase in carrefour.cycleBase or phase == phasePrioritaire]
            numeroSommets = [sommet.numero for sommet in sommets]
            matriceSubgraphe = carrefour.matriceGraphe[numeroSommets,:][:, numeroSommets]
            subgraphe = Graphe(matriceSubgraphe, sommets)
            
            listeChemins += subgraphe.chemins(carrefour.phaseActuelle, phasePrioritaire, carrefour, carrefour.delaiApproche)
            
    cheminsPossibles = []
    cheminsLongs = [] # min > delaiApproche
     
    for chemin in listeChemins:
        if carrefour.delaiApproche <= chemin.delaiMaximal():
            if carrefour.delaiApproche >= chemin.delaiMinimal():
                cheminsPossibles.append(chemin)
            else:
                cheminsLongs.append(chemin)
            
    if cheminsPossibles: # Se nao estiver vazia
        deviations = [chemin.deviation() for chemin in cheminsPossibles]
#        tempsRouge = [chemin.tempsRouge()  for chemin in cheminsPossibles]
        
        meilleurChemin = cheminsPossibles[np.argmin(deviations)]
        
        for chemin in cheminsPossibles:
            print(chemin)        
        
    else:
        minimums = [chemin.delaiMinimal() for chemin in cheminsLongs]
        meilleurChemin = cheminsLongs[np.argmin(minimums)]
        
    return meilleurChemin

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    



