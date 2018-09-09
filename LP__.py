from swiglpk import *
import numpy as np

def suivant(element, liste):
    return liste[(liste.index(element) + 1) % len(liste)]

class ResultatLP:
    def __init__(self):
        self.durees = []
        self.dureesRetard = []
        self.deviations = []
        self.attentes = []
        self.passages = []
        self.retardsEnsemble = []
        self.retardsIndividuels = []
        self.score = None
    
    def __bool__(self):
        return not (self.score is None)
    
    def __str__(self):

        return "Durees : "              + str(self.durees)              + "\n" + \
               "Deviations : "          + str(self.deviations)          + "\n" + \
               "Attentes: "             + str(self.attentes)            + "\n" + \
               "Retards Ensemble: "     + str(self.retardsEnsemble)     + "\n" + \
               "Retards Individuels: "  + str(self.retardsIndividuels)
#               "Score: "                + str(self.score)               + "\n" + \
#               "Durees Retard: "        + str(self.dureesRetard)        + "\n" + \
#               "Instants Passage: "     + str(self.passages)            + "\n" + \
               
        
class MatriceLP:
    def __init__(self, M=1000):
        self.ia = intArray(1+M)
        self.ja = intArray(1+M)
        self.ar = doubleArray(1+M)
        self.N = 0
        self.NMax = M
        
    def add(self, i, j, x):
        if self.N == self.NMax:
            raise RuntimeError("Nombre d'elements dans la MatriceLP dépasse le maximum")
        else:
            self.N += 1
            self.ia[self.N] = i
            self.ja[self.N] = j
            self.ar[self.N] = x
                
    def load(self, lp):
        glp_load_matrix(lp, self.N, self.ia, self.ja, self.ar)

def analyseAttentes(chemin, verbose = False):   
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
    
    if carrefour.phaseActuelle.type == 'phase':
        phase0 = chemin.phases[0]
        if carrefour.tempsPhase > phase0.dureeMinimale:
            if carrefour.tempsPhase < phase0.dureeMaximale:
                glp_set_col_bnds(lp, colX+0, GLP_DB, carrefour.tempsPhase, phase0.dureeMaximale)
            else:
                glp_set_col_bnds(lp, colX+0, GLP_FX, carrefour.tempsPhase, carrefour.tempsPhase)
    
    # Variables U
    colU = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin):
        glp_set_col_name(lp, colU+i, 'u'+str(i+1) )
        glp_set_col_bnds(lp, colU+i, GLP_LO, 0, 0)
    
    # Variables A
    colA = glp_add_cols(lp, len(demandesPriorite))
    for i,demande in enumerate(demandesPriorite):
        glp_set_col_name(lp, colA+i, 'a'+str(i+1))
        glp_set_col_bnds(lp, colA+i, GLP_LO, 0, 0)
        
    # Position des phases ouvertes à chaque ligne
    P = dict()
    for demande in demandesPriorite:
        l = demande.ligne
        if not l in P:
            P[l] = [j for j,phase in enumerate(chemin) if phase.lignesActives[l] == True]
            
    # Variables H
    colH = []
    for i,demande in enumerate(demandesPriorite):
        l = demande.ligne
        colH.append(glp_add_cols(lp, len(P[l]) ) )
        for j,p in enumerate(P[l]):
            glp_set_col_name(lp, colH[i]+j, 'h'+str(i+1)+str(j+1) )
            glp_set_col_kind(lp, colH[i]+j, GLP_BV)

    
    # Véhicules qui peuvent passer dans chaque phase spécifique et variables Y,Z
    
    phasesSpecifiques = [p for p,phase in enumerate(chemin.phases) if phase.exclusive]
    V = dict()
    
    colY = []
    colZ = []
    for i,p in enumerate(phasesSpecifiques):
        phase = chemin.phases[p]
        V[i] = [j for j,demande in enumerate(demandesPriorite) if phase.lignesActives[demande.ligne] ]
        if V[i]:
            colY.append(glp_add_cols(lp, len(V[i]) ) )
            colZ.append(glp_add_cols(lp, len(V[i]) ) )
            for j,v in enumerate(V[i]):
                glp_set_col_name(lp, colY[i]+j, 'y'+str(i+1)+str(j+1) )
                glp_set_col_kind(lp, colY[i]+j, GLP_BV)
                
                glp_set_col_name(lp, colZ[i]+j, 'z'+str(i+1)+str(j+1) )
                glp_set_col_kind(lp, colZ[i]+j, GLP_BV)
    
    colW = glp_add_cols(lp, 1)
    glp_set_col_kind(lp, colW, GLP_BV)
    
    # FONCTION OBJECTIVE
    paramExpObjective = 0.0693 # ln(2)/10 : Divise par 2 à chaque 10 s de différence
    
    for i,phase in enumerate(chemin):
        glp_set_obj_coef(lp, colU+i, 1)
    
    maxDelai = max([demande.delaiApproche for demande in demandesPriorite])
    for i,demande in enumerate(demandesPriorite):
        glp_set_obj_coef(lp, colA+i, 100*np.exp(-paramExpObjective*(demande.delaiApproche - maxDelai) ) )
    
    
    # CONTRAINTES    
    
    M = 1000 # Big M
    glp_matrix = MatriceLP()   
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(demandesPriorite):
        l = demande.ligne
        ligne = carrefour.listeLignes[l]
        
        # Pour chaque possible position de phase de passage
        for j,p in enumerate(P[l]):
            phase = chemin.phases[p]
            
            # Somme des durées des interphases
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
            for m in range(p):
                sommeInterphases += carrefour.interphase(chemin.phases[m], chemin.phases[m+1]).duree
            
            # Marge Fin
            margeFin = ligne.margeFin
            if p == 0 and carrefour.phaseActuelle.type == 'phase' and phase.lignesActives[l]:
                epsilon = min((-demande.delaiApproche, carrefour.tempsPhase-ligne.margeDebut))
                if epsilon >= margeFin:
                    margeFin = epsilon+1
            
            # Equation 1
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'v'+str(i+1)+str(j+1)+'eq1')
            for m in range(p):
                glp_matrix.add(row, colX+m, 1)
            glp_matrix.add(row, colA+i, -1)
            glp_matrix.add(row, colH[i]+j, M)
            rhs = carrefour.tempsPhase + demande.delaiApproche - sommeInterphases + M - ligne.margeDebut
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
            
            # Equation 2
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'v'+str(i+1)+str(j+1)+'eq2')
            for m in range(p+1):
                glp_matrix.add(row, colX+m, 1)
            glp_matrix.add(row, colA+i, -1)
            glp_matrix.add(row, colH[i]+j, -M)
            rhs = carrefour.tempsPhase + demande.delaiApproche - sommeInterphases - M + margeFin
            glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
            
        # Equation finale
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i+1)+'sum')
        for j,p in enumerate(P[l]):
            glp_matrix.add(row, colH[i]+j, 1)
        glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
    
    # Contraintes des variables U
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
    
    # Contrainte de au moins un véhicule dans la dernière phase (rédundant si elle est spécifique)
    phase = chemin.phases[-1]
    p = len(chemin)-1
    if not phase.exclusive:
        row = glp_add_rows(lp, 1)
        glp_set_row_name (lp, row, 'last')
        for i,demande in enumerate(demandesPriorite):
            l = demande.ligne
            if phase.lignesActives[l]:
                j = P[l].index(p)
                glp_matrix.add(row, colH[i]+j, 1)
        glp_set_row_bnds(lp, row, GLP_LO, 1, 0)
                         
    # Contraintes de max 120s de rouge
    for i,ligne in enumerate(carrefour.listeLignes):
        if ligne.couleur == 'red' and ligne.solicitee() and (not chemin.phases[0].lignesActives[i]):
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, ligne.nom)
            
            # Nombre de phases (fermées) du chemin jusqu'à l'ouverture de la ligne
            numPhases = 1 
            # Somme des durées des interphases jusqu'à l'ouverture de la ligne
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree 
            # Somme des durées nominales des phases hors chemin jusqu'à l'ouverture de la ligne
            sommeNominales = 0 
            
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
     
    # Contraintes des phases spécifiques

    # Un véhicule au début et fin de chaque phase spécifique
    for i,p in enumerate(phasesSpecifiques):
        if p != 0:
            for j in range(len(V[i]) ):
                k = V[i][j]
                demande = demandesPriorite[k]
                ligne = carrefour.listeLignes[demande.ligne]
                
                # Somme des durées des interphases
                sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
                for m in range(p):
                    sommeInterphases += carrefour.interphase(chemin.phases[m], chemin.phases[m+1]).duree
                
                # Equations Y
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'y'+str(i+1)+str(j+1)+'eq1')
                for m in range(p):
                    glp_matrix.add(row, colX+m, 1)
                glp_matrix.add(row, colA+k, -1)
                glp_matrix.add(row, colY[i]+j, M)
                rhs = carrefour.tempsPhase + demande.delaiApproche - sommeInterphases + M - ligne.margeDebut
                glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
                
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'y'+str(i+1)+str(j+1)+'eq2')
                for m in range(p):
                    glp_matrix.add(row, colX+m, 1)
                glp_matrix.add(row, colA+k, -1)
                glp_matrix.add(row, colY[i]+j, -M)
                rhs = carrefour.tempsPhase + demande.delaiApproche - sommeInterphases - M - ligne.margeDebut
                glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
                
                # Equations Z
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'z'+str(i+1)+str(j+1)+'eq1')
                for m in range(p+1):
                    glp_matrix.add(row, colX+m, 1)
                glp_matrix.add(row, colA+k, -1)
                glp_matrix.add(row, colZ[i]+j, M)
                rhs = carrefour.tempsPhase + demande.delaiApproche - sommeInterphases + M + ligne.margeFin
                glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
                
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'z'+str(i+1)+str(j+1)+'eq2')
                for m in range(p+1):
                    glp_matrix.add(row, colX+m, 1)
                glp_matrix.add(row, colA+k, -1)
                glp_matrix.add(row, colZ[i]+j, -M)
                rhs = carrefour.tempsPhase + demande.delaiApproche - sommeInterphases - M + ligne.margeFin
                glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
                
            # Equations finale
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'y'+str(i+1)+'sum')
            for j,p in enumerate(V[i]):
                glp_matrix.add(row, colY[i]+j, 1)
            glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
            
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'z'+str(i+1)+'sum')
            for j,p in enumerate(V[i]):
                glp_matrix.add(row, colZ[i]+j, 1)
            glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
    
#    # Contraintes d'intervalle entre véhicules dans la même phase exclusive
#    for m,demandeM in enumerate(demandesPriorite[:-1]):
#        for n,demandeN in enumerate(demandesPriorite[m+1:], m+1):
#            k = demandeM.codePriorite
#            if (demandeN.codePriorite == k):
#                for j,p in enumerate(P[k]):
#                    phase = chemin.phases[p]
#                    if phase.exclusive and phase.intervalle >= 0:
#                        # Equation 1
#                        row = glp_add_rows(lp, 1)
#                        glp_set_row_name(lp, row, 'p'+str(p+1)+'v'+str(m+1)+'v'+str(n+1)+'eq1')
#                        glp_matrix.add(row, colA+m, 1)
#                        glp_matrix.add(row, colA+n, -1)
#                        glp_matrix.add(row, colH[m]+j, M)
#                        glp_matrix.add(row, colH[n]+j, M)
#                        rhs = phase.intervalle + 2*M - demandeM.delaiApproche + demandeN.delaiApproche
#                        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
#                        
#                        # Equation 2
#                        row = glp_add_rows(lp, 1)
#                        glp_set_row_name(lp, row, 'p'+str(p+1)+'v'+str(m+1)+'v'+str(n+1)+'eq2')
#                        glp_matrix.add(row, colA+m, -1)
#                        glp_matrix.add(row, colA+n, 1)
#                        glp_matrix.add(row, colH[m]+j, M)
#                        glp_matrix.add(row, colH[n]+j, M)
#                        rhs = phase.intervalle + 2*M + demandeM.delaiApproche - demandeN.delaiApproche
#                        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )


                  
    # RESOLUTION
    
    # Charge la matrice de contraintes
    glp_matrix.load(lp) 
    
    # Résout le problème
    parm = glp_iocp()
    glp_init_iocp(parm)
    parm.presolve = GLP_ON
    parm.msg_level = GLP_MSG_OFF
    glp_intopt(lp, parm)
    
    if verbose:
        for j in range(glp_get_num_cols(lp)):
            glp_print_col(lp, j+1)
        for i in range(glp_get_num_rows(lp)):
            glp_print_row(lp, i+1)
        print('')
    
    # Leitura variaveis
    status = glp_mip_status(lp)

    chemin.resultat = ResultatLP()
    if status == GLP_OPT:
        chemin.resultat.durees = [round(glp_mip_col_val(lp, colX+i)) for i in range(len(chemin))]
        chemin.resultat.deviations = [round(glp_mip_col_val(lp, colU+i)) for i in range(len(chemin))]
        chemin.resultat.attentes = [round(glp_mip_col_val(lp, colA+j)) for j in range(len(demandesPriorite))]
        
        # Calcule les phases où passent les véhicules prioritaires
        for i,demande in enumerate(demandesPriorite):
            l = demande.ligne
            varsH = [glp_mip_col_val(lp, colH[i]+j) for j in range(len(P[l]) )]
            for j,Hij in enumerate(varsH):
                if Hij == 1:
                    chemin.resultat.passages.append(P[l][j])
                    break
        
        
        # Score du chemin
        chemin.resultat.score = sum(chemin.resultat.deviations) +                                                 \
                                100*sum([np.exp(-paramExpObjective*(demande.delaiApproche - maxDelai) )*attente   \
                                     for demande,attente in zip(demandesPriorite, chemin.resultat.attentes)])
            
    # Fin
    glp_delete_prob(lp)









def analyseRobustesse(chemin):
    demandesPriorite = chemin.carrefour.demandesPriorite
    chemin.resultat.retardsIndividuels = [0 for i in demandesPriorite]
    for vehicule in range(len(demandesPriorite) ):
        LPRobustesse(chemin, vehicule)
        
    LPRobustesse(chemin)

def LPRobustesse(chemin, vehicule=None):
    carrefour = chemin.carrefour
    demandesPriorite = carrefour.demandesPriorite
    resultat = chemin.resultat        
        
    # INITIALISATION
    
    # Création du problème
    lp = glp_create_prob()

    # Maximise l'objective
    glp_set_obj_dir(lp, GLP_MAX)
      
    # Variables X
    colX = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin):
        glp_set_col_name(lp, colX+i, 'x'+str(i+1))
        glp_set_col_bnds(lp, colX+i, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
    
    if carrefour.phaseActuelle.type == 'phase':
        phase0 = chemin.phases[0]
        if carrefour.tempsPhase > phase0.dureeMinimale:
            if carrefour.tempsPhase < phase0.dureeMaximale:
                glp_set_col_bnds(lp, colX,GLP_DB, carrefour.tempsPhase, phase0.dureeMaximale)
            else:
                glp_set_col_bnds(lp, colX,GLP_FX, carrefour.tempsPhase, carrefour.tempsPhase)
    
    # Variables Delta
    colD = glp_add_cols(lp, len(demandesPriorite))
    if vehicule is None:
        for i,demande in enumerate(demandesPriorite):
            glp_set_col_name(lp, colD+i, 'delta'+str(i+1))
            glp_set_col_bnds(lp, colD+i, GLP_LO, 0, 0)
    else:
        for i,demande in enumerate(demandesPriorite):
            glp_set_col_name(lp, colD+i, 'delta'+str(i+1))
            glp_set_col_bnds(lp, colD+i, GLP_FX, 0, 0)
        glp_set_col_bnds(lp, colD+vehicule, GLP_LO, 0, 0)

    # FONCTION OBJECTIVE
    
    for i,demande in enumerate(demandesPriorite):
        glp_set_obj_coef(lp, colD+i, 1)
    
    # CONTRAINTES    
    
    glp_matrix = MatriceLP()   
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(demandesPriorite):
        ligne = carrefour.listeLignes[demande.ligne]
        
        # Somme des durées des interphases
        sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
        for m in range(resultat.passages[i]):
            sommeInterphases += carrefour.interphase(chemin.phases[m], chemin.phases[m+1]).duree
        
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i+1)+'eq1')
        for m in range(resultat.passages[i]):
            glp_matrix.add(row, colX+m, 1)
        glp_matrix.add(row, colD+i, -1)
        rhs = demande.delaiApproche + resultat.attentes[i] + carrefour.tempsPhase - sommeInterphases - ligne.correctionDelai
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i+1)+'eq2')
        for m in range(resultat.passages[i]+1):
            glp_matrix.add(row, colX+m, 1)
        glp_matrix.add(row, colD+i, -1)
        rhs = demande.delaiApproche + resultat.attentes[i] + carrefour.tempsPhase - sommeInterphases + 1
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
        
                         
    # Contraintes de max 120s de rouge
    for i,ligne in enumerate(carrefour.listeLignes):
        if ligne.couleur == 'red' and ligne.solicitee() and (not chemin.phases[0].lignesActives[i]):
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, ligne.nom)
            
            # Nombre de phases (fermées) du chemin jusqu'à l'ouverture de la ligne
            numPhases = 1
            # Somme des durées des interphases jusqu'à l'ouverture de la ligne
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree 
            # Somme des durées nominales des phases hors chemin jusqu'à l'ouverture de la ligne
            sommeNominales = 0 
            
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
                
    
    # RESOLUTION    
    
    # Charge la matrice de contraintes
    glp_matrix.load(lp) 
    
    # Résout le problème
    parm = glp_iocp()
    glp_init_iocp(parm)
    parm.presolve = GLP_ON
    parm.msg_level = GLP_MSG_OFF
    glp_intopt(lp, parm)
    
#    for j in range(glp_get_num_cols(lp)):
#        glp_print_col(lp, j+1)
#    for i in range(glp_get_num_rows(lp)):
#        glp_print_row(lp, i+1)
#    print('')
    
    # Leitura variaveis
    status = glp_mip_status(lp)
    if status == GLP_OPT:
        if vehicule is None:
            resultat.dureesRetard = [round(glp_mip_col_val(lp, colX+j)) for j in range(len(chemin))]
            resultat.retardsEnsemble = [round(glp_mip_col_val(lp, colD+j)) for j in range(len(demandesPriorite))]
        else:
            resultat.retardsIndividuels[vehicule] = round(glp_mip_col_val(lp, colD+vehicule) )
            
    # Fin
    glp_delete_prob(lp)
        
        
def repartitionDurees(chemin):
    carrefour = chemin.carrefour
    resultat = chemin.resultat
    demandesPriorite = carrefour.demandesPriorite
    
    # INITIALISATION
    
    # Création du problème
    lp = glp_create_prob()

    # Minimise l'objective
    glp_set_obj_dir(lp, GLP_MIN)
      
    # Variables X
    colX = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin.phases):
        glp_set_col_name(lp, colX+i, 'x'+str(i+1))
        glp_set_col_bnds(lp, colX+i, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
#        glp_set_col_kind(lp, colX+i, GLP_IV)
    
    if carrefour.phaseActuelle.type == 'phase':
        phase0 = chemin.phases[0]
        if carrefour.tempsPhase > phase0.dureeMinimale:
            if carrefour.tempsPhase < phase0.dureeMaximale:
                glp_set_col_bnds(lp, colX,GLP_DB, carrefour.tempsPhase, phase0.dureeMaximale)
            else:
                glp_set_col_bnds(lp, colX,GLP_FX, carrefour.tempsPhase, carrefour.tempsPhase)
        
    # Variables U
    colU = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin):
        glp_set_col_name(lp, colU+i, 'u'+str(i+1) )
        glp_set_col_bnds(lp, colU+i, GLP_LO, 0, 0)
    
    # Variables Q
    colQ = glp_add_cols(lp, len(chemin))
    for i,phase in enumerate(chemin.phases):
        glp_set_col_name(lp, colQ+i, 'u'+str(i+1))
        glp_set_col_bnds(lp, colQ+i, GLP_LO, 0, 0)
        
        # Fonction Objective
        glp_set_obj_coef(lp, colQ+i, 1)
    
        
    # CONTRAINTES    
    
    glp_matrix = MatriceLP()
    
    # Somme des durees
    sommeNom = sum([phase.dureeNominale for phase in chemin.phases])
    sommeX = sum([x for x in chemin.resultat.durees])
    sommeU = sum([u for u in chemin.resultat.deviations])
    
    row = glp_add_rows(lp, 1)
    glp_set_row_name(lp, row,'sommeX')
    for i in range(len(chemin) ):
        glp_matrix.add(row, colX+i, 1)
    glp_set_row_bnds(lp, row, GLP_FX, sommeX, sommeX)
    
    row = glp_add_rows(lp, 1)
    glp_set_row_name(lp, row,'sommeU')
    for i in range(len(chemin) ):
        glp_matrix.add(row, colU+i, 1)
    glp_set_row_bnds(lp, row, GLP_FX, sommeU, sommeU)
    
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(demandesPriorite):
        ligne = carrefour.listeLignes[demande.ligne]
        
        # Somme des durées des interphases
        sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
        for m in range(resultat.passages[i]):
            sommeInterphases += carrefour.interphase(chemin.phases[m], chemin.phases[m+1]).duree
        
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i+1)+'eq1')
        for m in range(resultat.passages[i]):
            glp_matrix.add(row, colX+m, 1)
        rhs = demande.delaiApproche + resultat.attentes[i] + carrefour.tempsPhase - sommeInterphases - ligne.correctionDelai
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i+1)+'eq2')
        for m in range(resultat.passages[i]+1):
            glp_matrix.add(row, colX+m, 1)
        rhs = demande.delaiApproche + resultat.attentes[i] + carrefour.tempsPhase - sommeInterphases + 1
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
    
    # Contraintes des variables U
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
    
    # Contraintes de variables Q
    for i,phase in enumerate(chemin.phases):
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(i+1)+'eq1')
        glp_matrix.add(row, colX+i, 1)
        glp_matrix.add(row, colQ+i, -sommeX)
        glp_set_row_bnds(lp, row, GLP_UP, 0, phase.dureeNominale*sommeX/sommeNom)
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(i+1)+'eq2')
        glp_matrix.add(row, colX+i, 1)
        glp_matrix.add(row, colQ+i, sommeX)
        glp_set_row_bnds(lp, row, GLP_LO, phase.dureeNominale*sommeX/sommeNom, 0)
    
    # Contraintes de max 120s de rouge
    for i,ligne in enumerate(carrefour.listeLignes):
        if ligne.couleur == 'red' and ligne.solicitee() and (not chemin.phases[0].lignesActives[i]):
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, ligne.nom)
            
            # Nombre de phases (fermées) du chemin jusqu'à l'ouverture de la ligne
            numPhases = 1
            # Somme des durées des interphases jusqu'à l'ouverture de la ligne
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree 
            # Somme des durées nominales des phases hors chemin jusqu'à l'ouverture de la ligne
            sommeNominales = 0 
            
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
    
    
    
    # RESOLUTION
    
    # Charge la matrice de contraintes
    glp_matrix.load(lp) 
    
    # Résout le problème
    parm = glp_iocp()
    glp_init_iocp(parm)
    parm.presolve = GLP_ON
    parm.msg_level = GLP_MSG_OFF
    glp_intopt(lp, parm)
    
    # Leitura variaveis
    status = glp_mip_status(lp)
    
    if status == GLP_OPT:
        for i in range(len(chemin)):
            resultat.durees[i] = round(glp_mip_col_val(lp, colX+i))
            resultat.deviations[i] = abs(resultat.durees[i] - chemin.phases[i].dureeNominale)
        

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