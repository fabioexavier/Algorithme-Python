from swiglpk import *

def suivant(element, liste):
    return liste[(liste.index(element) + 1) % len(liste)]

class ResultatLP:
    def __init__(self):
        self.optimumTrouve = False
        self.durees = []
        self.deviations = []
        self.retards = []
        self.score = None
    
    def calcScore(self):
        if self.optimumTrouve:
            self.score = sum(self.deviations) + 100*sum(self.retards)
    
    def __bool__(self):
        return self.optimumTrouve
    
    def __str__(self):
        return "Durees: "       + str(self.durees)      + "\n" + \
               "Deviations: "   + str(self.deviations)  + "\n" + \
               "Retards: "      + str(self.retards)     + "\n" + \
               "Score: "        + str(self.score)       
        
class MatriceLP:
    def __init__(self, M=1000):
        self.ia = intArray(1+M)
        self.ja = intArray(1+M)
        self.ar = doubleArray(1+M)
        self.N = 0
        self.NMax = M
        
    def add(self, i, j, x):
        if self.N == self.NMax:
            raise RuntileError("Nombre d'elements dans la MatriceLP dépasse le maximum")
        else:
            self.N += 1
            self.ia[self.N] = i
            self.ja[self.N] = j
            self.ar[self.N] = x
                
    def load(self, lp):
        glp_load_matrix(lp, self.N, self.ia, self.ja, self.ar)

def analyseLP(chemin):
    carrefour = chemin.carrefour
    demandesPriorite = carrefour.demandesPriorite
    
    # INITIALISATION
    
    # Création du problème
    lp = glp_create_prob()

    # Minimise l'objective
    glp_set_obj_dir(lp, GLP_MIN)
      
    # Variables X
    colX = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin):
        glp_set_col_name(lp, colX+i, 'x'+str(i+1))
        glp_set_col_bnds(lp, colX+i, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
    
    phase0 = chemin.phases[0]
    if carrefour.tempsPhase > phase0.dureeMinimale:
        if carrefour.tempsPhase < phase0.dureeMaximale:
            glp_set_col_bnds(lp, colX,GLP_DB, carrefour.tempsPhase, phase0.dureeMaximale)
        else:
            glp_set_col_bnds(lp, colX,GLP_FX, carrefour.tempsPhase, carrefour.tempsPhase)
        
    # Variables U
    colU = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin):
        glp_set_col_name(lp, colU+i, 'u'+str(i+1))
        glp_set_col_bnds(lp, colU+i, GLP_LO, 0, 0)
        if phase.exclusive:
            glp_set_obj_coef(lp, colU+i, 2)
        else:
            glp_set_obj_coef(lp, colU+i, 1)
    
    # Variables R
    colR = glp_add_cols(lp, len(demandesPriorite))
    for i,demande in enumerate(demandesPriorite):
        glp_set_col_name(lp, colR+i, 'r'+str(i+1))
        glp_set_col_bnds(lp, colR+i, GLP_LO, 0, 0)
        glp_set_obj_coef(lp, colR+i, 100)
        
    
    # Partition des phases par rapport aux codes
    P = dict()
    for k in chemin.carrefour.codesPriorite:
        P[k] = [j for j,phase in enumerate(chemin) if phase.codePriorite == k]
            
    
    # Variables H
    colH = []
    for i,demande in enumerate(demandesPriorite):
        k = demande.codePriorite
        colH.append(glp_add_cols(lp, len(P[k]) ) )
        for j,p in enumerate(P[k]):
            glp_set_col_name(lp, colH[i]+j, 'h'+str(i+1)+str(j+1) )
            glp_set_col_kind(lp, colH[i]+j, GLP_BV)

    
    # CONTRAINTES    
    
    M = 1000 # Big M
    glp_matrix = MatriceLP()
    
    # Contraintes de variables U
    for i,phase in enumerate(chemin):
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(i+1)+'eq1')
        glp_matrix.add(row, colX+i, 1)
        glp_matrix.add(row, colU+i, -1)
        glp_set_row_bnds(lp, row, GLP_UP, 0, phase.dureeNominale)
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(i+1)+'eq2')
        glp_matrix.add(row, colX+i, 1)
        glp_matrix.add(row, colU+i, 1)
        glp_set_row_bnds(lp, row, GLP_LO, phase.dureeNominale, 0)
    
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(carrefour.demandesPriorite):
        k = demande.codePriorite
        
        # Pour chaque possible position de phase de passage
        for j,p in enumerate(P[k]):
            # Somme des durées des interphases
            sommeInterphases = 0
            for m in range(p):
                sommeInterphases += carrefour.interphase(chemin.phases[m], chemin.phases[m+1]).duree
            
            # Equation 1
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'v'+str(i+1)+str(j+1)+'eq1')
            for m in range(p):
                glp_matrix.add(row, colX+m, 1)
            glp_matrix.add(row, colR+i, -1)
            glp_matrix.add(row, colH[i]+j, M)
            rhs = demande.delaiApproche + carrefour.tempsPhase - sommeInterphases + M
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
            
            # Equation 2
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'v'+str(i+1)+str(j+1)+'eq2')
            for m in range(p+1):
                glp_matrix.add(row, colX+m, 1)
            glp_matrix.add(row, colR+i, -1)
            glp_matrix.add(row, colH[i]+j, -M)
            rhs = demande.delaiApproche + carrefour.tempsPhase - sommeInterphases - M + chemin.phases[p].dureeBus
            glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
            
        # Equation finale
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i+1)+'sum')
        for j,p in enumerate(P[k]):
            glp_matrix.add(row, colH[i]+j, 1)
        glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
    
    # Contraintes de au moins un véhicule par phase exclusive / dernière phase
    for p, phase in enumerate(chemin.phases[1:], 1):
        if phase.exclusive or p == len(chemin)-1:
            row = glp_add_rows(lp, 1)
            glp_set_row_name (lp, row, 'p'+str(p+1))
            k = phase.codePriorite
            j = P[k].index(p)
            for i,demande in enumerate(demandesPriorite):
                if demande.codePriorite == k:
                    glp_matrix.add(row, colH[i]+j, 1)
            glp_set_row_bnds(lp, row, GLP_LO, 1, 0)
                         
    # Contraintes de max 120s de rouge
    for i,ligne in enumerate(carrefour.listeLignes):
        if ligne.couleur == 'red' and ligne.solicitee():
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, ligne.nom)
            
            numPhases = 1 # Nombre de phases (fermées) du chemin jusqu'à l'ouverture de la ligne
            sommeInterphases = 0 # Somme des durées des interphases jusqu'à l'ouverture de la ligne
            sommeNominales = 0 # Somme des durées nominales des phases hors chemin jusqu'à l'ouverture de la ligne
            
            # Analyse les phases dans le chemin
            for j in range(1, len(chemin) ):
                sommeInterphases += carrefour.interphase(chemin.phases[j-1], chemin.phases[j]).duree
                if chemin.phases[j].lignesActives[i]:
                    break
                else:
                    numPhases += 1
                    
            # Si la ligne n'ouvre pas dans le chemin
            else:
                phase1 = chemin.phases[-1]
                
                # Calcule la phase qui vient immédiatement après la fin du chemin
                phase2 = suivant(phase1, carrefour.listePhases)
                while not phase2.solicitee:
                    phase2 = suivant(phase2, carrefour.listePhases)

                sommeInterphases += carrefour.interphase(phase1, phase2).duree

                # Analyse la séquence de phases hors chemin jusqu'à l'ouverture de la ligne
                while not phase2.lignesActives[i]:
                    phase1 = phase2
                    phase2 = suivant(phase1, carrefour.listePhases)
                    while not phase2.solicitee:
                        phase2 = suivant(phase2, carrefour.listePhases)

                    sommeInterphases += carrefour.interphase(phase1, phase2).duree
                    sommeNominales += phase1.dureeNominale
            
            # Ecrit la contrainte
            for k in range(numPhases):
                glp_matrix.add(row, colX+k, 1)
            
            rhs = 120 - ligne.compteurRouge + carrefour.tempsPhase - sommeInterphases - sommeNominales;
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
                
    
    # Contraintes d'intervalle entre véhicules dans la même phase exclusive
    for m,demandeM in enumerate(demandesPriorite[:-1]):
        for n,demandeN in enumerate(demandesPriorite[m+1:], m+1):
            k = demandeM.codePriorite
            if (demandeN.codePriorite == k):
                for j,p in enumerate(P[k]):
                    phase = chemin.phases[p]
                    if phase.exclusive and phase.intervalle >= 0:
                        # Equation 1
                        row = glp_add_rows(lp, 1)
                        glp_set_row_name(lp, row, 'p'+str(p+1)+'v'+str(m+1)+'v'+str(n+1)+'eq1')
                        glp_matrix.add(row, colR+m, 1)
                        glp_matrix.add(row, colR+n, -1)
                        glp_matrix.add(row, colH[m]+j, M)
                        glp_matrix.add(row, colH[n]+j, M)
                        rhs = phase.intervalle + 2*M - demandeM.delaiApproche + demandeN.delaiApproche
                        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
                        
                        # Equation 2
                        row = glp_add_rows(lp, 1)
                        glp_set_row_name(lp, row, 'p'+str(p+1)+'v'+str(m+1)+'v'+str(n+1)+'eq2')
                        glp_matrix.add(row, colR+m, -1)
                        glp_matrix.add(row, colR+n, 1)
                        glp_matrix.add(row, colH[m]+j, M)
                        glp_matrix.add(row, colH[n]+j, M)
                        rhs = phase.intervalle + 2*M + demandeM.delaiApproche - demandeN.delaiApproche
                        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )


                  
    # RESOLUTION
    
    # Charge la matrice de contraintes
    glp_matrix.load(lp) 
    
    # Résout le problème
    parm = glp_iocp()
    glp_init_iocp(parm)
    parm.presolve = GLP_ON
    glp_intopt(lp, parm)
    
#    for j in range(glp_get_num_cols(lp)):
#        glp_print_col(lp, j+1)
#    for i in range(glp_get_num_rows(lp)):
#        glp_print_row(lp, i+1)
#    print('')
    
    # Leitura variaveis
    resultat = ResultatLP()
    status = glp_mip_status(lp)

    if status == GLP_OPT:
        resultat.optimumTrouve = True
        resultat.durees = [round(glp_mip_col_val(lp, colX+i)) for i in range(len(chemin))]
        resultat.deviations = [round(glp_mip_col_val(lp, colU+i)) for i in range(len(chemin))]
        resultat.retards = [round(glp_mip_col_val(lp, colR+j)) for j in range(len(carrefour.demandesPriorite))]
        resultat.calcScore()
            
    # Fin
    glp_delete_prob(lp)

    return resultat


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
    typeDict = {GLP_LO:' >= ', GLP_UP:' <= ', GLP_FX:' = '}
    if rowType in typeDict:
        string += typeDict[rowType]
        
        if rowType == GLP_LO:
            b = str(glp_get_row_lb(lp, i))
        else:
            b = str(glp_get_row_ub(lp, i))
        string += b
    
    name = glp_get_row_name(lp, i)
    if name == None:
        name = ''
    print(name + ' : ' + string)