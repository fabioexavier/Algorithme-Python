from copy import copy
import numpy as np

from LP import ResultatLP

# Classe chemin

class Chemin:
    def __init__(self, **kwargs):
        if 'carrefour' in kwargs:
            carrefour = kwargs['carrefour']
        
            if carrefour.phaseActuelle.type == 'phase':
                origine = carrefour.phaseActuelle
                self.sommeMin = max( (origine.dureeMinimale - carrefour.tempsPhase, 0) )
                
            elif carrefour.phaseActuelle.type == 'interphase':
                origine = carrefour.phaseActuelle.phaseDestination
                self.sommeMin = carrefour.phaseActuelle.duree - carrefour.tempsPhase + origine.dureeMinimale
            
            self.phases = [origine]
            
            self.comptageLignes = [1 if origine.lignesActives[ligne.numero] else 0 for ligne in carrefour.listeLignes]
            
            self.resultat = ResultatLP()
            
            self.carrefour = carrefour
            
            
        elif 'chemin' in kwargs:
            chemin = kwargs['chemin']
            
            self.phases = chemin.phases.copy()
            self.sommeMin = chemin.sommeMin
            self.comptageLignes = chemin.comptageLignes.copy()
            self.resultat = copy(chemin.resultat)
            self.carrefour = chemin.carrefour
    
    def append(self, phase):
        self.phases.append(phase)
        
        self.sommeMin += self.carrefour.matriceInterphase[self.phases[-2].numero][self.phases[-1].numero].duree
        self.sommeMin += phase.dureeMinimale  
    
        for ligne in self.carrefour.listeLignes:
            if phase.lignesActives[ligne.numero]:
                self.comptageLignes[ligne.numero] += 1
            
    def copy(self):
        return Chemin(chemin=self)

    def valide(self):
        return all(self.comptageLignes[demande.ligne] > 0 for demande in self.carrefour.demandesPriorite) and \
               any(self.phases[-1].lignesActives[demande.ligne] for demande in self.carrefour.demandesPriorite)
    
    def transitionPossible(self, phase):
        if phase.escamotable:
            lignesDemandees = set()
            nDemandesCompatibles = 0
            
            for demande in self.carrefour.demandesPriorite:
                if phase.lignesActives[demande.ligne]:
                    lignesDemandees.add(demande.ligne)
                    nDemandesCompatibles += 1
            
            phasesEquivalentes = {phase}
            nPhasesEquivalentes = 1
            
            for p in self:
                if any(p.lignesActives[ligne] for ligne in lignesDemandees):
                    phasesEquivalentes.add(p)
                    nPhasesEquivalentes += 1
            
            nSolicitations = 0
            
            for phase in phasesEquivalentes:
                if phase.solicitee:
                    nSolicitations += 1
                    
            return nDemandesCompatibles + nSolicitations >= nPhasesEquivalentes
        
        else:
            return True
        
    def __len__(self):
        return len(self.phases)
    
    def __iter__(self):
        self.iterIndex = 0
        return self
    
    def __next__(self):
        if self.iterIndex >= len(self.phases):
            raise StopIteration
            
        ret = self.phases[self.iterIndex]
        self.iterIndex += 1
        return ret
    
    def __str__(self):
        return str(self.phases)

# Classe Graphe
class Graphe:
   def  __init__(self, sommets, matriceTransitions):
        self.sommets = sommets
        self.matrice = matriceTransitions
        
   def enfants(self, sommet):
       i = self.sommets.index(sommet)
       
       return [enfant for j,enfant in enumerate(self.sommets[i:],i) if self.matrice[i,j] == 1] + \
              [enfant for j,enfant in enumerate(self.sommets[:i]) if self.matrice[i,j] == 1]
 
# Algorithme Recherche

def rechercheChemins(carrefour):
    cheminsTrouves = []
    
    # Calcule le graphe et initialise le chemin
    cheminBase = Chemin(carrefour=carrefour)
    graphe = calcGraphe(carrefour)
    
    # Recherche tous les chemins possibles récursivement
    rechercheRecursive(graphe, cheminBase, cheminsTrouves)
    
    return cheminsTrouves


def calcGraphe(carrefour):
    # Identifie les sommets du graphe comme etant toutes les phases
    sommets = carrefour.listePhases
    
    # Vérifie les transitions possibles et assemble la matrice
    matriceTransitions = np.zeros( (len(sommets), len(sommets) ) )
    
    for i,sommet1 in enumerate(sommets):
        j = (i+1) % len(sommets)
        sommet2 = sommets[j]
        testerTransition = True
        
        while testerTransition:
            if not (sommet1.lignesActives == sommet2.lignesActives):
                matriceTransitions[i,j] = 1
                
            if sommet2.escamotable:
                j = (j+1) % len(sommets)
                sommet2 = sommets[j]
                
                if sommet2 == sommet1:
                    testerTransition = False
            else:
                testerTransition = False
    
    return Graphe(sommets, matriceTransitions)


def rechercheRecursive(graphe, chemin, cheminsTrouves):
    # Enregistre le chemin s'il est acceptable
    if chemin.valide():
        cheminsTrouves.append(chemin)

    # Teste si on est arrivé à la fin de la branche
    if not finDeBranche(graphe, chemin):
        enfants = graphe.enfants(chemin.phases[-1])

        # Répète pour chaque enfant vers lequel la transition est valide
        for enfant in enfants:
            if chemin.transitionPossible(enfant):
                cheminDerive = chemin.copy()
                cheminDerive.append(enfant)

                rechercheRecursive(graphe, cheminDerive, cheminsTrouves)


def finDeBranche(graphe, chemin):
    # On est arrivé à la fin de la branche si la somme des minis est au moins égale au plus grand délai d'approche et
    # si le nombre de phases dans le chemin est au moins égal au nombre de sommets du graphe

    # Calcule plus grand delai d'approche
    maxDelai = max([demande.delaiApproche for demande in chemin.carrefour.demandesPriorite])

    return (chemin.sommeMin >= maxDelai) and (len(chemin) >= len(graphe.sommets) )

