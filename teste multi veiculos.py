import gestionIntersections as gi
import numpy as np
import scipy.optimize as opt
import pulp

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
               
listePhases = [gi.Phase(0, [False, False, False, True, True, False, False, True, True, False], 14, 50, 80, False, 0, False, 0),\
               gi.Phase(1, [True, True, False, False, False, False, False, False, False, True], 4, 8, 30, True, 1, True, 4),\
               gi.Phase(2, [False, True, True, False, False, True, True, False, False, True], 11, 15, 40, False, 2, False, 4),\
               gi.Phase(3, [True, False, False, True, False, False, False, True, False, False], 4, 8, 30, True, 1, True, 4)]
               

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


class Chemin:
    def __init__(self, pCarrefour, pListePhases=None, pSommeMin=0, pComptagesCodes=None):
        self.carrefour = pCarrefour
        self.listePhases = pListePhases
        self.sommeMin = pSommeMin
        self.comptagesCodes = pComptagesCodes
        
        # Inicializa o caminho partindo da fase atual do carrefour
        if pListePhases == None:
            origine = pCarrefour.phaseActuelle

            if origine.type == 'Phase':
                self.listePhases = [origine]
                self.sommeMin = origine.dureeMinimale - pCarrefour.tempsPhase if origine.dureeMinimale - pCarrefour.tempsPhase > 0 else 0
                
            elif origine.type == 'Interphase':
                self.listePhases = [origine.phaseDestination]
                self.sommeMin = origine.duree - pCarrefour.tempsPhase + origine.phaseDestination.dureeMinimale
                
            self.comptagesCodes = {}
            for code in pCarrefour.codesPriorite:
                self.comptagesCodes[code] = 0
            
            self.comptagesCodes[listePhases[0].prioritaire] += 1
            
    def append(self, phase):
        self.listePhases.append(phase)
        
        self.sommeMin += self.carrefour.matriceInterphase[self.listePhases[-2].numero][self.listePhases[-1].numero].duree
        self.sommeMin += phase.dureeMinimale  
    
        self.comptagesCodes[phase.prioritaire] += 1
        
    def copy(self):
        return Chemin(self.carrefour, self.listePhases.copy(), self.sommeMin, self.comptagesCodes.copy())
    
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

#        print('Codes Demandes:', {demande[1] for demande in demandesPriorite})
#        print('Max delai:', max([demande[0] for demande in demandesPriorite]))
        
        comptagesCodes = {}
        for code in chemin.carrefour.codesPriorite:
            comptagesCodes[code] = len([demande for demande in demandesPriorite if demande[1] == code])
            
#        print('Comptages:', comptagesCodes)

        self.rechercheRecursive(cheminBase, demandesPriorite)
        
        chemins = self.listeChemins
        self.listeChemins = []
        
        return chemins

    def rechercheRecursive(self, chemin, demandesPriorite):
#        print('')
#        print(chemin)
#        print(chemin.comptagesCodes)
        codesDemandes = {demande[1] for demande in demandesPriorite}
        maxDelai = max([demande[0] for demande in demandesPriorite])
        
        comptagesCodes = {}
        for code in chemin.carrefour.codesPriorite:
            comptagesCodes[code] = len([demande for demande in demandesPriorite if demande[1] == code])
    
        # Testa para ver se o caminho é aceitavel
        if chemin.listePhases[-1].prioritaire in codesDemandes: # Se a ultima fase foi demandada
            for code in codesDemandes:
                if chemin.comptagesCodes[code] == 0:
#                    print('Caminho nao aceitavel; fases insuficientes com codigo', code)
                    break
            else: # Se para todos os codigos demandados existe pelo menos uma fase no caminho
#                print('Caminho aceitavel')
                self.listeChemins.append(chemin)
#        else:
#            print('Caminho nao aceitavel; fase final nao demandada')
        
        # Verifica se chegou no fim do galho
#        print('Min', chemin.sommeMin)
        # OBS len(self.listeSommets) nao ta certo
        if chemin.sommeMin < maxDelai or len(chemin) < len(self.listeSommets): # Continua a busca
#            print('Nao chegou no fim do galho')
            i = self.listeSommets.index(chemin.listePhases[-1])
            enfants = [sommet for j,sommet in enumerate(self.listeSommets) if self.matrice[i,j] == 1]
#            print('Enfants:', enfants)
            
            for sommet in enfants:
                # Verififica se a transicao é valida
                transitionPossible = True
                if sommet.escamotable:
                    if not sommet.prioritaire: # ESC
                        if sommet in chemin:
                            transitionPossible = False
#                            print(sommet, 'Transicao impossivel: ESC')
                    elif sommet.exclusive: # PEE
                        code = sommet.prioritaire
                        if chemin.comptagesCodes[code] == comptagesCodes[code]:
                            transitionPossible = False
#                            print(sommet, 'Transicao impossivel: PEE')
                    else: #PENE
                        pass # ESCREVER ESSE PEDACO
                        
                if transitionPossible:
#                    print(sommet, 'Transicao possivel')
                    cheminDerive = chemin.copy()
                    cheminDerive.append(sommet)
                    self.rechercheRecursive(cheminDerive, demandesPriorite)
#        else:
#            print('Chegou no fim do galho')

#######################################################################################################

# (delaiApproche, code)
carrefour.tempsPhase = 5
demandesPriorite = [(30,2), (75,1)]

sommets = [phase for phase in carrefour.listePhases if phase.solicitee or phase.prioritaire]
numeroSommets = [sommet.numero for sommet in sommets]
matriceSubgraphe = carrefour.matriceGraphe[numeroSommets,:][:, numeroSommets]
subgraphe = Graphe(matriceSubgraphe, sommets)

listeChemins = subgraphe.chemins(carrefour, demandesPriorite)

for chemin in listeChemins:
    print(chemin)

#######################################################################################"
    # Teste pulp
    
    prob = pulp.LpProblem('Distribution des durees', pulp.LpMinimize)
    
    # Variaveis
    
    # Duracao das fases
    x = [None for i in range(len(chemin))]
    for i,phase in enumerate(chemin.listePhases):
        if i == 0:
            mini = max((carrefour.tempsPhase,phase.dureeMinimale))
        else:
            mini = phase.dureeMinimale
        maxi = phase.dureeMaximale
        x[i] = pulp.LpVariable('x'+str(i), mini, maxi)
    
    # Atraso de cada demanda
    r = [None for i in range(len(demandesPriorite))]
    for i in range(len(demandesPriorite)):
        r[i] = pulp.LpVariable('r'+str(i), 0, None)
    
    # Extras para poder tratar soma de valores absolutos como linear
    u = [None for i in range(len(chemin))]
    for i in range(len(chemin)):
        u[i] = pulp.LpVariable('u'+str(i), 0, None)
    
    
    # Funcao objetivo
    obj = 0
    for ui in u:
        obj += ui
    for ri in r:
        obj += 100*ri
    prob += obj, 'Deviation totale par rapport aux temps nominaux'
    
    # Restricoes dos delais
    for j,demande in enumerate(demandesPriorite):
        indexPassage = [phase.prioritaire==demande[1] for phase in chemin.listePhases].index(True)
        
        sommeX = 0
        sommeInterphases = 0
        for i in range(indexPassage):
            sommeX += x[i]
            phase1 = chemin.listePhases[i]
            phase2 = chemin.listePhases[i+1]
            sommeInterphases += carrefour.matriceInterphase[phase1.numero][phase2.numero].duree
        
        prob += sommeX <= demande[0]+r[j] + carrefour.tempsPhase - sommeInterphases, 'LB demande '+str(j)
        prob += sommeX+x[indexPassage] >= demande[0]+r[j] + carrefour.tempsPhase - sommeInterphases + chemin.listePhases[indexPassage].dureeBus, 'UB demande '+str(j)
    
    # Restricoes de u
    for i,phase in enumerate(chemin.listePhases):
        prob += u[i] >= x[i]-phase.dureeNominale, 'u'+str(i)+' pos'
        prob += u[i] >= -(x[i]-phase.dureeNominale), 'u'+str(i)+' neg'
    
    
    
    # Solve
    #print(prob)
    
    prob.solve()
    
    print("Status:", pulp.LpStatus[prob.status])
    
    for xi in x:
        print(xi.name, "=", xi.varValue)
    for ri in r:
        print(ri.name, "=", ri.varValue)
        
    print("Deviation totale = ", np.sum([ui.varValue for ui in u]))
    print("Score = ", pulp.value(prob.objective))

    print('')