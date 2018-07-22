import gestionIntersections as gi

# Dossier Reunion
listeLignes = [gi.LigneDeFeu(0, 'B2', 'Voiture', 3, True),  \
               gi.LigneDeFeu(1, 'P3', 'Pieton', 0, False),  \
               gi.LigneDeFeu(2, 'P4', 'Pieton', 0, False),  \
               gi.LigneDeFeu(3, 'P5', 'Pieton', 0, False),  \
               gi.LigneDeFeu(4, 'L6', 'Voiture', 3, False), \
               gi.LigneDeFeu(5, 'P7', 'Pieton', 0, False),  \
               gi.LigneDeFeu(6, 'L8', 'Voiture', 3, False), \
               gi.LigneDeFeu(7, 'P9', 'Pieton', 0, False),  \
               gi.LigneDeFeu(8, 'L10', 'Voiture', 3, False),\
               gi.LigneDeFeu(9, 'P11', 'Pieton', 0, False)]
               
listePhases = [gi.Phase(0, [False, False, False, True, True, False, False, True, True, False], 14, 50, 80, False, 0, False),\
               gi.Phase(1, [True, True, False, False, False, False, False, False, False, True], 4, 8, 30, True, 1, True),\
               gi.Phase(2, [False, True, True, False, False, True, True, False, False, True], 11, 15, 40, False, 2, False),\
               gi.Phase(3, [True, False, False, True, False, False, False, True, False, False], 4, 8, 30, True, 1, True)]
               

matriceSecurite = [[0,0,1,0,2,4,2,0,2,0],   \
                   [0,0,0,0,8,0,0,0,0,0],   \
                   [8,0,0,0,6,0,0,0,0,0],   \
                   [0,0,0,0,0,0,2,0,0,0],   \
                   [2,1,4,0,0,0,1,0,0,4],   \
                   [5,0,0,0,0,0,0,0,5,0],   \
                   [2,0,0,4,2,0,0,1,1,0],   \
                   [0,0,0,0,0,0,7,0,0,0],   \
                   [1,0,0,0,0,3,1,0,0,1],   \
                   [0,0,0,0,6,0,0,0,8,0]]

carrefour = gi.Carrefour(listeLignes, listePhases, matriceSecurite)

#####################################################################################################

# (delaiApproche, code)
demandesPriorite = [(30,1), (75,2)]


class Chemin:
    def __init__(self, pCarrefour, pListePhases=None, pSommeMin=0):
        self.carrefour = pCarrefour
        self.listePhases = pListePhases
        self.sommeMin = pSommeMin
        
        # Inicializa o caminho partindo da fase atual do carrefour
        if pListePhases == None:
            origine = pCarrefour.phaseActuelle

            if origine.type == 'Phase':
                self.listePhases = [origine]
                self.sommeMin = origine.dureeMinimale - pCarrefour.tempsPhase if origine.dureeMinimale - pCarrefour.tempsPhase > 0 else 0
                
            elif origine.type == 'Interphase':
                self.listePhases = [origine.phaseDestination]
                self.sommeMin = origine.duree - pCarrefour.tempsPhase + origine.phaseDestination.dureeMinimale
            
    def append(self, phase):
        self.listePhases.append(phase)
        
        self.sommeMin += self.carrefour.matriceInterphase[self.listePhases[-2].numero][self.listePhases[-1].numero].duree
        self.sommeMin += phase.dureeMinimale  
    
    def copy(self):
        return Chemin(self.origine, self.carrefour, self.listePhases.copy(), self.sommeMin)
    
    def __len__(self):
        return len(self.listePhases)
    
    def __str__(self):
        return str(self.listePhases)
    __repr__ = __str__
    
    
    
class Graphe:
    def __init__(self, pMatrice, pSommets):
        self.matrice = pMatrice
        self.listeSommets = pSommets
        self.listeChemins = []

    def chemins(self, carrefour, demandesPriorite):
        cheminBase = Chemin(carrefour)

        codesDemandes = {demande[1] for demande in demandesPriorite}


        
        if origine in self.listeSommets:
            self.rechercheChemins(origine, destination, cheminBase, delaiApproche)
        chemins = self.listeChemins
        self.listeChemins = []
        
        return chemins

    def rechercheChemins(self, origine, destination, chemin, delaiApproche):
        chemin.append(origine)
        arreter = False
        
        if origine == destination:
            self.listeChemins.append(chemin)
            
        # Condiçoes de parada    
        if origine.escamotable:
            if origine.prioritaire and origine.exclusive: # PEE
                if len(chemin) > 1:
                    arreter = True
            else: # PENE ou ESC
                if origine in self.listeChemins[:-1]: # Ja adicionada antes
                    arreter = True
        elif chemin.sommeMin >= delaiApproche and len(chemin) >= len(self.listeSommets): # Caminho muito longo sem chegar no destino
            arreter = True
        
        if not arreter:
            i = self.listeSommets.index(origine)
            enfants = [sommet for j,sommet in enumerate(self.listeSommets) if self.matrice[i,j] == 1]
            for sommet in enfants:
                self.rechercheChemins(sommet, destination, chemin.copy(), delaiApproche)

