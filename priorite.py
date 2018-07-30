import numpy as np
from swiglpk import *
import time

def suivant(element, liste):
    index = liste.index(element) + 1
    if index == len(liste):
        index = 0
    return liste[index]

class Chemin:
    def __init__(self, pCarrefour, pListePhases=None, pSommeMin=0, pComptagesCodes=None):
        self.carrefour = pCarrefour
        self.listePhases = pListePhases
        self.sommeMin = pSommeMin
        self.comptagesCodes = pComptagesCodes
        
        self.score = -1
        self.durees = []
        self.deviations = []
        self.retards = []
        
        # Inicializa o caminho partindo da fase atual do carrefour
        if pListePhases == None:
            origine = pCarrefour.phaseActuelle

            if origine.type == 'phase':
                self.listePhases = [origine]
                self.sommeMin = origine.dureeMinimale - pCarrefour.tempsPhase if origine.dureeMinimale - pCarrefour.tempsPhase > 0 else 0
                
            elif origine.type == 'interphase':
                self.listePhases = [origine.phaseDestination]
                self.sommeMin = origine.duree - pCarrefour.tempsPhase + origine.phaseDestination.dureeMinimale
                
            self.comptagesCodes = {}
            for code in pCarrefour.codesPriorite:
                self.comptagesCodes[code] = 0
            
            self.comptagesCodes[self.listePhases[0].codePriorite] += 1
            
    def append(self, phase):
        self.listePhases.append(phase)
        
        self.sommeMin += self.carrefour.matriceInterphase[self.listePhases[-2].numero][self.listePhases[-1].numero].duree
        self.sommeMin += phase.dureeMinimale  
    
        self.comptagesCodes[phase.codePriorite] += 1
        
    def copy(self):
        return Chemin(self.carrefour, self.listePhases.copy(), self.sommeMin, self.comptagesCodes.copy())
    
    def __len__(self):
        return len(self.listePhases)
    
    def __str__(self):
        strPhases = str(self.listePhases) + '\n'
#        strScore = 'Score: ' + str(self.score) + '\n'
        strDurees = 'Durees: ' + str(self.durees) + '\n'
        strDeviations = 'Deviations: ' + str(self.deviations) + '\n'
        strRetards = 'Retards: ' + str(self.retards)
        return strPhases + strDurees + strDeviations + strRetards
    __repr__ = __str__
    
    
class Graphe:
    def __init__(self, pMatrice, pSommets):
        self.matrice = pMatrice
        self.listeSommets = pSommets
        self.listeChemins = []

    def chemins(self, carrefour):
        cheminBase = Chemin(carrefour)

        self.rechercheRecursive(cheminBase, carrefour.demandesPriorite)
        
        chemins = self.listeChemins
        self.listeChemins = []
        
        return chemins

    def rechercheRecursive(self, chemin, demandesPriorite):
#        print('')
#        print(chemin.listePhases)
#        print(chemin.comptagesCodes)
        codesDemandes = {demande.codePriorite for demande in demandesPriorite}
        maxDelai = max([demande.delaiApproche for demande in demandesPriorite])
        
        comptagesCodes = {}
        for code in chemin.carrefour.codesPriorite:
            comptagesCodes[code] = len([demande for demande in demandesPriorite if demande.codePriorite == code])
    
        # Testa para ver se o caminho é aceitavel
        if chemin.listePhases[-1].codePriorite in codesDemandes: # Se a ultima fase foi demandada
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
        
        if chemin.sommeMin < maxDelai or len(chemin) < len(self.listeSommets): # Continua a busca
#            print('Nao chegou no fim do galho')
            i = self.listeSommets.index(chemin.listePhases[-1])
            enfants = [sommet for j,sommet in enumerate(self.listeSommets) if self.matrice[i,j] == 1]
#            print('Enfants:', enfants)
            
            for sommet in enfants:
                # Verififica se a transicao é valida
                transitionPossible = True
                if sommet.escamotable:
                    if not sommet.codePriorite: # ESC
                        if sommet in chemin.listePhases:
                            transitionPossible = False
#                            print(sommet, 'Transicao impossivel: ESC')
                    elif sommet.exclusive: # PEE
                        code = sommet.codePriorite
                        # Nao contabiliza a primeira fase caso ela possua o mesmo codigo da fase que queremos adicionar
                        if chemin.listePhases[0].codePriorite == code:
                            if chemin.comptagesCodes[code]-1 >= comptagesCodes[code]:
                                transitionPossible = False
                        else:
                            if chemin.comptagesCodes[code] >= comptagesCodes[code]:
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

class constraintsMatrix:
    def __init__(self, M=1000):
        self.ia = intArray(1+M)
        self.ja = intArray(1+M)
        self.ar = doubleArray(1+M)
        self.N = 0
        self.M = M
        
    def add(self, i, j, x):
        if self.N < self.M:
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


def analyseSimplex(listeChemins, carrefour):
    cheminsPossibles = []
    
#    for chemin in listeChemins:
#        print(chemin.listePhases)
    
    for chemin in listeChemins:
        lp = glp_create_prob() # Cria o objeto do problema LP
#        glp_set_prob_name(lp, 'problem') # Define o nome do problema
#        glp_set_obj_name(lp, 'Deviation') # Define o nome da funcao objetivo
        glp_set_obj_dir(lp, GLP_MIN) # Define se queremos maximizar ou minimizar o objetivo
          
        # Add variaveis x
        colX = glp_add_cols(lp, len(chemin))
        for i,phase in enumerate(chemin.listePhases):
            glp_set_col_name(lp, colX+i, 'x'+str(i+1))
            glp_set_col_bnds(lp, colX+i, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
        
        if carrefour.phaseActuelle.type == 'phase': # Ajusta o LB de x1 caso necessario
            phase0 = chemin.listePhases[0]
            if carrefour.tempsPhase > phase0.dureeMinimale:
                if carrefour.tempsPhase < phase0.dureeMaximale:
                    glp_set_col_bnds(lp, colX,GLP_DB, carrefour.tempsPhase, phase0.dureeMaximale)
                else:
                    glp_set_col_bnds(lp, colX,GLP_FX, carrefour.tempsPhase, carrefour.tempsPhase)
            
        # Add variaveis u
        colU = glp_add_cols(lp, len(chemin))
        for i,phase in enumerate(chemin.listePhases):
            glp_set_col_name(lp, colU+i, 'u'+str(i+1))
            glp_set_col_bnds(lp, colU+i, GLP_LO, 0, 0)
            if phase.exclusive:
                glp_set_obj_coef(lp, colU+i, 2)
            else:
                glp_set_obj_coef(lp, colU+i, 1)
        
        # Add variaveis r
        colR = glp_add_cols(lp, len(carrefour.demandesPriorite))
        for i,demande in enumerate(carrefour.demandesPriorite):
            glp_set_col_name(lp, colR+i, 'r'+str(i+1))
            glp_set_col_bnds(lp, colR+i, GLP_LO, 0, 0)
            glp_set_obj_coef(lp, colR+i, 100)
        
        # Matriz de restriçoes
        glp_matrix = constraintsMatrix()
        
        # Restricoes de u
        rowU = glp_add_rows(lp, 2*len(chemin))
        for i,phase in enumerate(chemin.listePhases):
            glp_set_row_name(lp, rowU+2*i,'u'+str(i+1)+'eq1')
            glp_matrix.add(rowU+2*i, colX+i, 1)
            glp_matrix.add(rowU+2*i, colU+i, -1)
            glp_set_row_bnds(lp, rowU+2*i, GLP_UP, 0, phase.dureeNominale)
            
            glp_set_row_name(lp, rowU+2*i+1,'u'+str(i+1)+'eq2')
            glp_matrix.add(rowU+2*i+1, colX+i, 1)
            glp_matrix.add(rowU+2*i+1, colU+i, 1)
            glp_set_row_bnds(lp, rowU+2*i+1, GLP_LO, phase.dureeNominale, 0)
        
        # Restricoes de delai
        rowV = [0 for k in carrefour.demandesPriorite] # rowV[i] representa a coluna onde comecam as restricoes de delai do veiculo i
        colH = [0 for k in carrefour.demandesPriorite] # colH[i] representa a coluna onde comecam as variaveis h do veiculo i
        M = 1000 # Big M
        
        # Para cada veiculo
        for i,demande in enumerate(carrefour.demandesPriorite):
            P = [index for index,phase in enumerate(chemin.listePhases) if phase.codePriorite == demande.codePriorite]

            # Adiciona as variaveis h
            colH[i] = glp_add_cols(lp, len(P))
            rowV[i] = glp_add_rows(lp, 2*len(P)+1)
                        
            # Para cada fase em que o veiculo pode passar
            for j,p in enumerate(P):
                # Configuracao das variaveis h
                glp_set_col_name(lp, colH[i]+j, 'h'+str(i+1)+str(j+1))
                glp_set_col_kind(lp, colH[i]+j, GLP_BV)
                
                # Soma das duracoes de interfase
                sommeInterphases = 0
                for m in range(p):
                    phase1 = chemin.listePhases[m]
                    phase2 = chemin.listePhases[m+1]
                    sommeInterphases += carrefour.interphase(phase1,phase2).duree
                if carrefour.phaseActuelle.type == 'interphase':
                    sommeInterphases += carrefour.phaseActuelle.duree
                
                # Equaçao 1
                glp_set_row_name(lp, rowV[i]+2*j, 'v'+str(i+1)+str(j+1)+'eq1')
                for m in range(p):
                    glp_matrix.add(rowV[i]+2*j, colX+m, 1)
                glp_matrix.add(rowV[i]+2*j, colR+i, -1)
                glp_matrix.add(rowV[i]+2*j, colH[i]+j, M)
                b = demande.delaiApproche + carrefour.tempsPhase - sommeInterphases
                glp_set_row_bnds(lp, rowV[i]+2*j, GLP_UP, 0, float(b+M))
                
                # Equaçao 2
                glp_set_row_name(lp, rowV[i]+2*j+1, 'v'+str(i+1)+str(j+1)+'eq2')
                for m in range(p+1):
                    glp_matrix.add(rowV[i]+2*j+1, colX+m, 1)
                glp_matrix.add(rowV[i]+2*j+1, colR+i, -1)
                glp_matrix.add(rowV[i]+2*j+1, colH[i]+j, -M)
                b = demande.delaiApproche + carrefour.tempsPhase - sommeInterphases
                glp_set_row_bnds(lp, rowV[i]+2*j+1, GLP_LO, float(b+chemin.listePhases[p].dureeBus-M), 0)
                
            # Equaçao Final
            glp_set_row_name(lp, rowV[i]+2*len(P), 'v'+str(i+1)+'sum')
            for m in range(len(P)):
                glp_matrix.add(rowV[i]+2*len(P), colH[i]+m, 1)
            glp_set_row_bnds(lp, rowV[i]+2*len(P), GLP_FX, 1, 1)
        
        # Pelo menos um veiculo por fase exclusiva (exceto na primeira)
        phasesExclusives = [index for index,phase in enumerate(chemin.listePhases) if phase.exclusive and index > 0]
        
        if phasesExclusives: # Se a lista nao for vazia 
            rowE = glp_add_rows(lp, len(phasesExclusives))      
            for m,p in enumerate(phasesExclusives):
                glp_set_row_name (lp, rowE+m, 'e'+str(m+1))
                k = chemin.listePhases[p].codePriorite
                # Todas as posicoes de fases com esse codigo
                P = [index for index,phase in enumerate(chemin.listePhases) if phase.codePriorite == k]
                # Indice da fase exclusiva na lista P
                j = P.index(p)
                
                # Para cada veiculo com o mesmo codigo da fase
                for i,demande in enumerate(carrefour.demandesPriorite):
                    if demande.codePriorite == k:
                        glp_matrix.add(rowE+m, colH[i]+j, 1)
                glp_set_row_bnds(lp, rowE+m, GLP_LO, 1, 0)
        
        # Pelo menos um veiculo na ultima fase
        if not chemin.listePhases[-1].exclusive:
            rowLast = glp_add_rows(lp, 1)
            glp_set_row_name (lp, rowL, 'last')
            
            N = len(chemin)-1
            k = chemin.listePhases[N].codePriorite
            # Todas as posicoes de fases com esse codigo
            P = [index for index,phase in enumerate(chemin.listePhases) if phase.codePriorite == k]
            # Indice da fase exclusiva na lista P
            j = P.index(N)
            
            # Para cada veiculo com o mesmo codigo da fase
            for i,demande in enumerate(carrefour.demandesPriorite):
                if demande.codePriorite == k:
                    glp_matrix.add(rowLast, colH[i]+j, 1)
            glp_set_row_bnds(lp, rowLast, GLP_LO, 1, 0)
                             
        # Restriçoes de 120s
        # OBS: Hipotese de que o algoritmo de prioridade somente é chamado durante fases (nunca interfase)
        for ligne in carrefour.listeLignes:
            if ligne.couleur == 'red' and ligne.solicitee():
                rowLigne = glp_add_rows(lp, 1)
                glp_set_row_name(lp, rowLigne, ligne.nom)
                
                sommeInterphases = 0
                sommeNominaux = 0
                
                index = 0
                # Se len(chemin) == 1, index permanece 0 e o for nao é executado
                for index in range(1, len(chemin)):
                    phase1 = chemin.listePhases[index-1]
                    phase2 = chemin.listePhases[index]
                    sommeInterphases += carrefour.interphase(phase1, phase2).duree
                    # Se a linha esta aberta nessa fase
                    if phase2.lignesActives[ligne.numero] == True:
                        break
                else: # Se chegou ate o fim do caminho sem encontrar uma fase com a linha aberta
                    phase1 = chemin.listePhases[index]
                    phase2 = suivant(phase1, carrefour.listePhases)
                    while not phase2.solicitee:
                        phase2 = suivant(phase2, carrefour.listePhases)
                    sommeInterphases += carrefour.interphase(phase1, phase2).duree
                    index += 1
                    
                    while not phase2.lignesActives[ligne.numero] == True:
                        phase1 = phase2
                        phase2 = suivant(phase1, carrefour.listePhases)
                        while not phase2.solicitee:
                            phase2 = suivant(phase2, carrefour.listePhases)
                        sommeNominaux += phase1.dureeNominale
                        sommeInterphases += carrefour.interphase(phase1, phase2).duree
                
                for i in range(index):
                    glp_matrix.add(rowLigne, colX+i, 1)
                    
                b = 120 - ligne.compteurRouge + carrefour.tempsPhase - sommeInterphases - sommeNominaux
                glp_set_row_bnds(lp, rowLigne, GLP_UP, 0, float(b))
                        
                    
        # Carrega matriz de restriçoes
        glp_matrix.load(lp) 
        
        # Print restriçoes
#        print(chemin.listePhases)
#        for j in range(glp_get_num_cols(lp)):
#            glp_print_col(lp, j+1)
#        for i in range(glp_get_num_rows(lp)):
#            glp_print_row(lp, i+1)
#        print('')
        
        # Resolve o problema
        parm = glp_iocp()
        glp_init_iocp(parm)
        parm.presolve = GLP_ON
        glp_intopt(lp, parm)
        
        # Leitura variaveis
        status = glp_mip_status(lp)
    
        if status == GLP_OPT:
            chemin.score = round(glp_mip_obj_val(lp))
            chemin.durees = [round(glp_mip_col_val(lp, colX+i)) for i in range(len(chemin))]
            chemin.deviations = [round(glp_mip_col_val(lp, colU+i)) for i in range(len(chemin))]
            chemin.retards = [round(glp_mip_col_val(lp, colR+j)) for j in range(len(carrefour.demandesPriorite))]
            cheminsPossibles.append(chemin)
                
        # Fim
        glp_delete_prob(lp)

    return cheminsPossibles


def cheminPrioritaire(carrefour):
    tBegin = time.time()
    
    sommets = [phase for phase in carrefour.listePhases if phase.solicitee or phase.codePriorite]
    numeroSommets = [sommet.numero for sommet in sommets]
    matriceSubgraphe = carrefour.matriceGraphe[numeroSommets,:][:, numeroSommets]
    
    subgraphe = Graphe(matriceSubgraphe, sommets)
    
    listeChemins = subgraphe.chemins(carrefour)
    
    cheminsPossibles = analyseSimplex(listeChemins, carrefour)
    
    scores = [chemin.score for chemin in cheminsPossibles]
    meilleurChemin = cheminsPossibles[np.argmin(scores)]
    
    tEnd = time.time()
    
    print('Meilleur chemin:', meilleurChemin)
    print('Chemins analisés: ', len(listeChemins))
    print('Temps (ms):', 1000*(tEnd-tBegin))
    print('')
    
    dureeActuelle = meilleurChemin.durees[0]
    phaseProchaine = meilleurChemin.listePhases[1] if len(meilleurChemin) > 1 else None
    
    return (dureeActuelle, phaseProchaine)    
    
    