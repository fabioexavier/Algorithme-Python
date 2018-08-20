import numpy as np

# Classe chemin

class Chemin:
    def __init__(self, **kwargs):
        if 'carrefour' in kwargs:
            carrefour = kwargs['carrefour']
        
            origine = carrefour.phaseActuelle
            
            self.phases = []
            self.phases.append(origine)
            
            self.sommeMin = max( (origine.dureeMinimale - carrefour.tempsPhase, 0) )
            
            self.comptageCodes = dict()
            for code in carrefour.codesPriorite:
                self.comptageCodes[code] = 0
            self.comptageCodes[origine.codePriorite] += 1
            
            self.carrefour = carrefour
            
            
        elif 'chemin' in kwargs:
            chemin = kwargs['chemin']
            
            self.phases = chemin.phases.copy()
            self.sommeMin = chemin.sommeMin
            self.comptageCodes = chemin.comptageCodes.copy()
            self.carrefour = chemin.carrefour
    
    def append(self, phase):
        self.phases.append(phase)
        
        self.sommeMin += self.carrefour.matriceInterphase[self.phases[-2].numero][self.phases[-1].numero].duree
        self.sommeMin += phase.dureeMinimale  
    
        self.comptageCodes[phase.codePriorite] += 1
            
    def copy(self):
        return Chemin(chemin=self)

    def valide(self):
        return any(demande.codePriorite == self.phases[-1].codePriorite for demande in self.carrefour.demandesPriorite) \
               and all(self.comptageCodes[demande.codePriorite] != 0 for demande in self.carrefour.demandesPriorite)
    
    def transitionPossible(self, phase):
        transitionPossible = True
        
        if phase.escamotable:
            # Phase ESC
            if phase.codePriorite == 0:
                # Si la phase est deja dans le chemin
                if phase in self:
                    transitionPossible = False
        
            # Phase PEE ou PENE
            else:
                code = phase.codePriorite
    
                # Nombre max admissible de phases avec ce code dans le chemin
                # Admet une phase en plus si la première phase est PEE et a le même code
                maxPhases = 1 if self.phases[0].exclusive and (self.phases[0].codePriorite == code) else 0
                # +1 pour chaque demande avec le même code
                for demande in self.carrefour.demandesPriorite:
                    if demande.codePriorite == code:
                        maxPhases += 1
                
                # +1 pour chaque phase PENE distincte, solicitée, avec le même code et dans le chemin
                for phase in self.carrefour.listePhases:
                    if (not phase.exclusive) and phase.solicitee and (phase.codePriorite == code) and (phase in self):
                        maxPhases += 1
    
                # Empêche la transition si le nombre max de phases est déjà atteint
                if self.comptageCodes[code] == maxPhases:
                    transitionPossible = False
        
        return transitionPossible;
    
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
       
       return [enfant for j,enfant in enumerate(self.sommets) if self.matrice[i,j] == 1]
 
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
    # Identifie les sommets du graphe
    sommets = [phase for phase in carrefour.listePhases if phase.solicitee or phase.codePriorite != 0]
    
    # Vérifie les transitions possibles et assemble la matrice
    matriceTransitions = np.zeros( (len(sommets), len(sommets) ) )
    
    for i,sommet1 in enumerate(sommets):
        j = (i+1) % len(sommets)
        sommet2 = sommets[j]
        ajouterTransition = True
        
        while ajouterTransition:
            if not (sommet1.exclusive and sommet2.exclusive and sommet1.codePriorite == sommet2.codePriorite):
                matriceTransitions[i,j] = 1
                
            ajouterTransition = False
            if sommet2.escamotable:
                j = (j+1) % len(sommets)
                sommet2 = sommets[j]
                
                if sommet2 != sommet1:
                    ajouterTransition = True
    
    return Graphe(sommets, matriceTransitions)


def rechercheRecursive(graphe, chemin, cheminsTrouves):
#    print("")
#    print(chemin)
    # Enregistre le chemin s'il est acceptable
    if chemin.valide():
#        print("Valide")
        cheminsTrouves.append(chemin)
#    else:
#        print("Pas valide")

    # Teste si on est arrivé à la fin de la branche
#    print("Somme min:", chemin.sommeMin)
    if not finDeBranche(graphe, chemin):
#        print("Pas fin de branche")
        enfants = graphe.enfants(chemin.phases[-1])
#        print("Enfants:", enfants)

        # Répète pour chaque enfant vers lequel la transition est valide
        for enfant in enfants:
            if chemin.transitionPossible(enfant):
#                print("Enfant", enfant, "Transition possible")
                cheminDerive = chemin.copy()
                cheminDerive.append(enfant)

                rechercheRecursive(graphe, cheminDerive, cheminsTrouves)
#            else:
#                print("Enfant", enfant, "Transition pas possible")
#    else:
#        print("Fin de branche")


def finDeBranche(graphe, chemin):
    # On est arrivé à la fin de la branche si la somme des minis est au moins égale au plus grand délai d'approche et
    # si le nombre de phases dans le chemin est au moins égal au nombre de sommets du graphe

    # Calcule plus grand delai d'approche
    maxDelai = max([demande.delaiApproche for demande in chemin.carrefour.demandesPriorite])

    return (chemin.sommeMin >= maxDelai) and (len(chemin) >= len(graphe.sommets) )

