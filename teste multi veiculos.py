import gestionIntersections as gi
import numpy as np
from swiglpk import *
import time

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
        
#        comptagesCodes = {}
#        for code in chemin.carrefour.codesPriorite:
#            comptagesCodes[code] = len([demande for demande in demandesPriorite if demande[1] == code])
            
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

tBegin = time.time()

sommets = [phase for phase in carrefour.listePhases if phase.solicitee or phase.prioritaire]
numeroSommets = [sommet.numero for sommet in sommets]
matriceSubgraphe = carrefour.matriceGraphe[numeroSommets,:][:, numeroSommets]
subgraphe = Graphe(matriceSubgraphe, sommets)

listeChemins = subgraphe.chemins(carrefour, demandesPriorite)



#chemin = listeChemins[2]

#######################################################################################

# Encapsulamentos

class constraintsMatrix:
    def __init__(self, M=1000):
        self.ia = intArray(1+M)
        self.ja = intArray(1+M)
        self.ar = doubleArray(1+M)
        self.N = 0
        
    def add(self, i, j, x):
        self.N += 1
        self.ia[self.N] = i
        self.ja[self.N] = j
        self.ar[self.N] = x
                
    def load(self, lp):
        glp_load_matrix(lp, self.N, self.ia, self.ja, self.ar)
        
    def __str__(self):
        string = ''
        for i in range(self.N):
            string += str(self.ia[i+1]) + ' ' + str(self.ja[i+1]) + ' ' + str(self.ar[i+1]) + '\n'
        string += 'N = ' + str(self.N)
        return string


def glp_print_col(lp, j):
    lb = glp_get_col_lb(lp, j)
    ub = glp_get_col_ub(lp, j)
    name = glp_get_col_name(lp, j)
    print(lb, '<=', name, '<=', ub)
    
def glp_print_row(lp, i):
    n = glp_get_num_cols(lp)
    ind = intArray(n+1)
    val = doubleArray(n+1)
    glp_get_mat_row(lp, i, ind, val)
    
    string = ''
    for k in range(n):
        if ind[k+1] == 0:
            break
        name = glp_get_col_name(lp, ind[k+1])
        if string == '':
            string += str(val[k+1]) + '*' + name
        else:
            string += ' + ' + str(val[k+1]) + '*' + name
    
    if string == '':
        string += '0'
    
    rowType = glp_get_row_type(lp, i)
    typeDict = {GLP_LO:' >= ', GLP_UP:' <= '  , GLP_FX:' = '}
    if rowType in typeDict:
        string += typeDict[rowType]
        
        if rowType == GLP_LO:
            b = str(glp_get_row_lb(lp, i))
        else:
            b = str(glp_get_row_ub(lp, i))
        string += b
    
    print(string)
    

############################################################################################

for chemin in listeChemins:
    print(chemin)
    
    lp = glp_create_prob() # Cria o objeto do problema LP
    glp_set_prob_name(lp, 'problem') # Define o nome do problema
    glp_set_obj_name(lp, 'Deviation') # Define o nome da funcao objetivo
    glp_set_obj_dir(lp, GLP_MIN) # Define se queremos maximizar ou minimizar o objetivo
    
   
    
    
    # Add variaveis x
    colX = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin.listePhases):
        glp_set_col_name(lp, colX+i, 'x'+str(i+1))
        glp_set_col_bnds(lp, colX+i, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
    
    if carrefour.phaseActuelle.type == 'Phase': # Ajusta o LB de x1 caso necessario
        phase0 = chemin.listePhases[0]
        if carrefour.tempsPhase > phase0.dureeMinimale:
            glp_set_col_bnds(lp, colX,GLP_DB, carrefour.tempsPhase, phase.dureeMaximale)
        
    # Add variaveis u
    colU = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin.listePhases):
        glp_set_col_name(lp, colU+i, 'u'+str(i+1))
        glp_set_col_bnds(lp, colU+i, GLP_LO, 0, 0)
        glp_set_obj_coef(lp, colU+i, 1)
        
    # Add variaveis r
    colR = glp_add_cols(lp, len(demandesPriorite))
    for i,demande in enumerate(demandesPriorite):
        glp_set_col_name(lp, colR+i, 'r'+str(i+1))
        glp_set_col_bnds(lp, colR+i, GLP_LO, 0, 0)
        glp_set_obj_coef(lp, colR+i, 100)
    
    # Matriz de restriçoes
    glp_matrix = constraintsMatrix()
    
    # Restricoes de u
    rowU = glp_add_rows(lp, 2*len(chemin))
    for i,phase in enumerate(chemin.listePhases):
        glp_set_row_name(lp, rowU+2*i,'u'+str(i+1)+'<')
        glp_matrix.add(rowU+2*i, colX+i, 1)
        glp_matrix.add(rowU+2*i, colU+i, -1)
        glp_set_row_bnds(lp, rowU+2*i, GLP_UP, 0, phase.dureeNominale)
        
        glp_set_row_name(lp, rowU+2*i+1,'u'+str(i+1)+'>')
        glp_matrix.add(rowU+2*i+1, colX+i, 1)
        glp_matrix.add(rowU+2*i+1, colU+i, 1)
        glp_set_row_bnds(lp, rowU+2*i+1, GLP_LO, phase.dureeNominale, 0)
    
    # Restricoes de delai
    rowD = glp_add_rows(lp, 2*len(demandesPriorite))
    for i,demande in enumerate(demandesPriorite):
        index = [phase.prioritaire==demande[1] for phase in chemin.listePhases].index(True)
        
        sommeInterphases = 0
        for k in range(index):
            phase1 = chemin.listePhases[k]
            phase2 = chemin.listePhases[k+1]
            sommeInterphases += carrefour.matriceInterphase[phase1.numero][phase2.numero].duree
        
        glp_set_row_name(lp, rowD+2*i,'demande'+str(i+1)+'<')
        glp_set_row_name(lp, rowD+2*i+1,'demande'+str(i+1)+'>')
        for j in range(index):
            glp_matrix.add(rowD+2*i, colX+j, 1)
            glp_matrix.add(rowD+2*i+1, colX+j, 1)
        glp_matrix.add(rowD+2*i+1, colX+index, 1)
        glp_matrix.add(rowD+2*i, colR+i, -1)
        glp_matrix.add(rowD+2*i+1, colR+i, -1)
        b = float(demande[0] + carrefour.tempsPhase - sommeInterphases)
        if carrefour.phaseActuelle.type == 'Interphase':
            b -= carrefour.phaseActuelle.duree
        glp_set_row_bnds(lp, rowD+2*i, GLP_UP, 0, b)
        glp_set_row_bnds(lp, rowD+2*i+1, GLP_LO, b+chemin.listePhases[index].dureeBus, 0)
    
    # Carrega matriz de restriçoes
    glp_matrix.load(lp)
    
    
    
    # Resolve o problema
    parm = glp_smcp()
    glp_init_smcp(parm)
#    parm.meth = GLP_DUAL
    glp_simplex(lp, parm)
    
    
    # Leitura variaveis
    if glp_get_status(lp) == GLP_OPT:
        z = glp_get_obj_val(lp)
        
        x = []
        u = []
        r = []
        for i in range(len(chemin)):
            x.append(glp_get_col_prim(lp, colX+i))
            u.append(glp_get_col_prim(lp, colU+i))
        for j in range(len(demandesPriorite)):
            r.append(glp_get_col_prim(lp, colR+j))
        
    #    for i in range(glp_get_num_rows(lp)):
    #        glp_print_row(lp,i+1)
        
        print('z', z)
        print('x', x)
        print('u', u)
        print('r', r)
        print('')
    
    # Fim
    glp_delete_prob(lp)

tEnd = time.time()

print(tEnd-tBegin)
    
    
    
    
    