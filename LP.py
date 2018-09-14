from swiglpk import *
import numpy as np

def suivant(element, liste):
    return liste[(liste.index(element) + 1) % len(liste)]

class ResultatLP:
    def __init__(self):
        self.durees = []
        self.deviations = []
        self.attentes = []
        self.passages = []
        self.vehiculesDebut = []
        self.vehiculesFin = []
        self.retards = []
        self.score = None
    
    def __bool__(self):
        return not (self.score is None)
    
    def __str__(self):

        return "Durees : "              + str(self.durees)              + "\n" + \
               "Deviations : "          + str(self.deviations)          + "\n" + \
               "Attentes : "            + str(self.attentes)            + "\n" + \
               "Retards : "             + str(self.retards)             + "\n" 
#               "Vehicules Debut: "      + str(self.vehiculesDebut)      + "\n" + \
#               "Vehicules Fin: "        + str(self.vehiculesFin)        + "\n" + \
#               "Retards Individuels: "  + str(self.retardsIndividuels)  + "\n" + \
#               "Durees Retard: "        + str(self.dureesRetard)
#               "Score: "                + str(self.score)               + "\n" + \
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




def analyseAttentes(chemin, verbose=False):   
    carrefour = chemin.carrefour
    demandesPriorite = carrefour.demandesPriorite
    
    chemin.resultat = ResultatLP()
    resultat = chemin.resultat
    
    # INITIALISATION
    
    # Création du problème
    lp = glp_create_prob()
    
    M = 1000 # Big M
    glp_matrix = MatriceLP()  

    # Minimise l'objective
    glp_set_obj_dir(lp, GLP_MIN)
      
    # Variables X
    colX = glp_add_cols(lp, len(chemin))
    for k,phase in enumerate(chemin):
        glp_set_col_name(lp, colX+k, 'x'+str(k) )
        glp_set_col_bnds(lp, colX+k, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
    
    # x0 >= T
    if carrefour.phaseActuelle.type == 'phase':
        phase0 = chemin.phases[0]
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'x0')
        glp_matrix.add(row, colX+0, 1)
        rhs = carrefour.tempsEcoule
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
        
        
    # Variables U
    colU = glp_add_cols(lp, len(chemin))
    for k,phase in enumerate(chemin):
        glp_set_col_name(lp, colU+k, 'u'+str(k) )
        glp_set_col_bnds(lp, colU+k, GLP_LO, 0, 0)
        
    # Contraintes des variables U
    for k,phase in enumerate(chemin):
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(k)+'eq1')
        glp_matrix.add(row, colX+k, 1)
        glp_matrix.add(row, colU+k, -1)
        rhs = phase.dureeNominale
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(k)+'eq2')
        glp_matrix.add(row, colX+k, 1)
        glp_matrix.add(row, colU+k, 1)
        rhs = phase.dureeNominale
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
    
    # Variables A
    colA = glp_add_cols(lp, len(demandesPriorite))
    for i,demande in enumerate(demandesPriorite):
        glp_set_col_name(lp, colA+i, 'a'+str(i) )
        glp_set_col_bnds(lp, colA+i, GLP_LO, 0, 0)
        
    # Position des phases ouvertes à chaque ligne
    K = dict()
    for demande in demandesPriorite:
        l = demande.ligne
        if not l in K:
            K[l] = [k for k,phase in enumerate(chemin) if phase.lignesActives[l] == True]
            
    # Variables H
    colH = []
    for i,demande in enumerate(demandesPriorite):
        l = demande.ligne
        colH.append(glp_add_cols(lp, len(K[l]) ) )
        for j in range(len(K[l]) ):
            glp_set_col_name(lp, colH[i]+j, 'h'+str(i)+str(j) )
            glp_set_col_kind(lp, colH[i]+j, GLP_BV)

    
    # Véhicules qui peuvent passer dans chaque phase spécifique et variables Y, Z et W
    phasesSpecifiques = [p for p,phase in enumerate(chemin.phases) if phase.specifique]
    V = dict()
    
    colY = []
    colZ = []
    for m,k in enumerate(phasesSpecifiques):
        phase = chemin.phases[k]
        V[m] = [i for i,demande in enumerate(demandesPriorite) if phase.lignesActives[demande.ligne] ]
        if V[m]:
            colY.append(glp_add_cols(lp, len(V[m]) ) )
            colZ.append(glp_add_cols(lp, len(V[m]) ) )
            for j,v in enumerate(V[m]):
                glp_set_col_name(lp, colY[m]+j, 'y'+str(m)+str(j) )
                glp_set_col_kind(lp, colY[m]+j, GLP_BV)
                
                glp_set_col_name(lp, colZ[m]+j, 'z'+str(m)+str(j) )
                glp_set_col_kind(lp, colZ[m]+j, GLP_BV)
    
    colW = glp_add_cols(lp, 1)
    glp_set_col_name(lp, colW, 'w')
    glp_set_col_kind(lp, colW, GLP_BV)

    # FONCTION OBJECTIVE
    paramExpObjective = 0.0693 # ln(2)/10 : Divise par 2 à chaque 10 s de différence
    
    for k,phase in enumerate(chemin):
        glp_set_obj_coef(lp, colU+k, 1)
    
    maxDelai = max([demande.delaiApproche for demande in demandesPriorite])
    for i,demande in enumerate(demandesPriorite):
        glp_set_obj_coef(lp, colA+i, 100*np.exp(-paramExpObjective*(demande.delaiApproche - maxDelai) ) )
    
    
    # CONTRAINTES     
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(demandesPriorite):
        l = demande.ligne
        ligne = carrefour.listeLignes[l]
        
        # Pour chaque possible position de phase de passage
        for j,k in enumerate(K[l]):
            phase = chemin.phases[k]
            
            # Somme des durées des interphases
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
            for n in range(k):
                sommeInterphases += carrefour.interphase(chemin.phases[n], chemin.phases[n+1]).duree
            
            # Marge Fin
            margeFin = ligne.margeFin
            if k == 0 and carrefour.phaseActuelle.type == 'phase' and phase.lignesActives[l]:
                epsilon = min((-demande.delaiApproche, carrefour.tempsEcoule))
                if epsilon >= margeFin:
                    margeFin = epsilon+1
                
            # Equation 1
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'v'+str(i)+str(j)+'eq1')
            for n in range(k):
                glp_matrix.add(row, colX+n, 1)
            glp_matrix.add(row, colA+i, -1)
            glp_matrix.add(row, colH[i]+j, M)
            rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases + M - ligne.margeDebut
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
            
            # Equation 2
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'v'+str(i)+str(j)+'eq2')
            for n in range(k+1):
                glp_matrix.add(row, colX+n, 1)
            glp_matrix.add(row, colA+i, -1)
            glp_matrix.add(row, colH[i]+j, -M)
            rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases - M + margeFin
            glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
            
        # Equation finale
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i)+'sum')
        for j in range(len(K[l]) ):
            glp_matrix.add(row, colH[i]+j, 1)
        glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
    
    
    # Contrainte de au moins un véhicule dans la dernière phase (rédundant si elle est spécifique)
    phase = chemin.phases[-1]
    k = len(chemin)-1
    if not phase.specifique:
        row = glp_add_rows(lp, 1)
        glp_set_row_name (lp, row, 'derniere_phase')
        for i,demande in enumerate(demandesPriorite):
            l = demande.ligne
            if phase.lignesActives[l]:
                j = K[l].index(k)
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
            for k in range(1, len(chemin) ):
                sommeInterphases += carrefour.interphase(chemin.phases[k-1], chemin.phases[k]).duree
                if chemin.phases[k].lignesActives[i]:
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
            
            rhs = 120 - ligne.compteurRouge + carrefour.tempsEcoule - sommeInterphases - sommeNominales;
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
     
    # Contraintes des phases spécifiques

    # Un véhicule au début et fin de chaque phase spécifique (sauf si elle est la première phase du chemin)
    for m,k in enumerate(phasesSpecifiques):
        if k != 0:
            for j in range(len(V[m]) ):
                i = V[m][j]
                demande = demandesPriorite[i]
                ligne = carrefour.listeLignes[demande.ligne]
                
                # Somme des durées des interphases
                sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
                for n in range(k):
                    sommeInterphases += carrefour.interphase(chemin.phases[n], chemin.phases[n+1]).duree
                
                # Equations Y
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'y'+str(m)+str(j)+'eq1')
                for n in range(k):
                    glp_matrix.add(row, colX+n, 1)
                glp_matrix.add(row, colA+i, -1)
                glp_matrix.add(row, colY[m]+j, M)
                rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases + M - ligne.margeDebut
                glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
                
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'y'+str(m)+str(j)+'eq2')
                for n in range(k):
                    glp_matrix.add(row, colX+n, 1)
                glp_matrix.add(row, colA+i, -1)
                glp_matrix.add(row, colY[m]+j, -M)
                rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases - M - ligne.margeDebut
                glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
                
                # Equations Z
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'z'+str(m)+str(j)+'eq1')
                for n in range(k+1):
                    glp_matrix.add(row, colX+n, 1)
                glp_matrix.add(row, colA+i, -1)
                glp_matrix.add(row, colZ[m]+j, M)
                rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases + M + ligne.margeFin
                glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
                
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'z'+str(m)+str(j)+'eq2')
                for n in range(k+1):
                    glp_matrix.add(row, colX+n, 1)
                glp_matrix.add(row, colA+i, -1)
                glp_matrix.add(row, colZ[m]+j, -M)
                rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases - M + ligne.margeFin
                glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
                
            # Equations finales
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'y'+str(m)+'sum')
            for j in range(len(V[m]) ):
                glp_matrix.add(row, colY[m]+j, 1)
            glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
            
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'z'+str(m)+'sum')
            for j in range(len(V[m]) ):
                glp_matrix.add(row, colZ[m]+j, 1)
            glp_set_row_bnds(lp, row, GLP_FX, 1, 1)
            
        
    # Traitement du véhicule à la fin de la première phase dans le cas où elle est spécifique
    phase0 = chemin.phases[0]
    if phase0.specifique:
        
        # Equation de aucun vehicule dans la phase
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'somme_h_w')
        for i in V[0]:
            glp_matrix.add(row, colH[i]+0, 1)        
        glp_matrix.add(row, colW, -M)
        rhs = 0
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        # Equation max x0 si aucun vehicule dans la phase
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'max_x0_w')
        glp_matrix.add(row, colX+0, 1)
        glp_matrix.add(row, colW, -M)
        rhs = max((chemin.phases[0].dureeMinimale, carrefour.tempsEcoule))
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        for j,i in enumerate(V[0]):
            demande = demandesPriorite[i]
            ligne = carrefour.listeLignes[demande.ligne]
            
            # Somme des durées des interphases
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
            
            # Marge Fin
            margeFin = ligne.margeFin
            if carrefour.phaseActuelle.type == 'phase':
                epsilon = min((-demande.delaiApproche, carrefour.tempsEcoule))
                if epsilon >= ligne.margeFin:
                    margeFin = epsilon+1
            
            
            # Equations Z
            
            # Equation 1
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'z'+str(0)+str(j)+'eq1')
            
            glp_matrix.add(row, colX+0, 1)
            glp_matrix.add(row, colA+i, -1)
            glp_matrix.add(row, colZ[0]+j, M)
            glp_matrix.add(row, colW, M)
            
            rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases + 2*M + margeFin
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
            
            # Equation 2
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 'z'+str(0)+str(j)+'eq2')
            
            glp_matrix.add(row, colX+0, 1)
            glp_matrix.add(row, colA+i, -1)
            glp_matrix.add(row, colZ[0]+j, -M)
            glp_matrix.add(row, colW, -M)
            
            rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases - 2*M + margeFin
            glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
            
        # Equations finales
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'z'+str(0)+'sum1')
        for j in range(len(V[0]) ):
            glp_matrix.add(row, colZ[0]+j, 1)
        glp_matrix.add(row, colW, M)
        rhs = 1+M
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'z'+str(1)+'sum2')
        for j in range(len(V[0]) ):
            glp_matrix.add(row, colZ[0]+j, 1)
        glp_matrix.add(row, colW, -M)
        rhs = 1-M
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
    
    
    
    
    # Contraintes d'intervalle entre véhicules dans la même phase spécifique
    for m,k in enumerate(phasesSpecifiques):
        phase = chemin.phases[k]
        if phase.intervalle >= 0:
            for i,demandeI in enumerate(demandesPriorite[:-1]):
                for j,demandeJ in enumerate(demandesPriorite[i+1:],i+1):
                    if phase.lignesActives[demandeI.ligne] and phase.lignesActives[demandeJ.ligne]:
                        q = K[demandeI.ligne].index(k)
                        r = K[demandeJ.ligne].index(k)
                        
                        ligneI = carrefour.listeLignes[demandeI.ligne]
                        ligneJ = carrefour.listeLignes[demandeJ.ligne]
                        
                        # Marges Fin
                        margeFinI = ligneI.margeFin
                        if k == 0 and carrefour.phaseActuelle.type == 'phase' and phase.lignesActives[demandeI.ligne]:
                            epsilonI = min((-demandeI.delaiApproche, carrefour.tempsEcoule))
                            if epsilonI >= margeFin:
                                margeFinI = epsilonI + 1
                                
                        margeFinJ = ligneJ.margeFin
                        if k == 0 and carrefour.phaseActuelle.type == 'phase' and phase.lignesActives[demandeJ.ligne]:
                            epsilonJ = min((-demandeJ.delaiApproche, carrefour.tempsEcoule))
                            if epsilonJ >= margeFin:
                                margeFinJ = epsilonJ + 1
                        
                        # Equation 1
                        row = glp_add_rows(lp, 1)
                        glp_set_row_name(lp, row, 'int_p'+str(k)+'_v'+str(i)+'_v'+str(j)+'_eq1')
                        glp_matrix.add(row, colA+i, 1)
                        glp_matrix.add(row, colA+j, -1)
                        glp_matrix.add(row, colH[i]+q, M)
                        glp_matrix.add(row, colH[j]+r, M)
                        rhs = -demandeI.delaiApproche + demandeJ.delaiApproche + margeFinJ + phase.intervalle + 2*M 
                        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
                        
                        # Equation 2
                        row = glp_add_rows(lp, 1)
                        glp_set_row_name(lp, row, 'int_p'+str(k)+'_v'+str(i)+'_v'+str(j)+'_eq2')
                        glp_matrix.add(row, colA+i, -1)
                        glp_matrix.add(row, colA+j, 1)
                        glp_matrix.add(row, colH[i]+r, M)
                        glp_matrix.add(row, colH[j]+q, M)
                        rhs = demandeI.delaiApproche - demandeJ.delaiApproche + margeFinI + phase.intervalle + 2*M 
                        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
                    
                    
    # Comparaison avec les véhicules qui ont déjà franchi
    for ligne in carrefour.listeLignes:
        if ligne.compteurFranchissement >= 0 and ligne.compteurFranchissement <= 1:
            for i,demande in enumerate(demandesPriorite):
                if carrefour.phaseActuelle.type == 'phase' and carrefour.phaseActuelle.lignesActives[demande.ligne]:
                    row = glp_add_rows(lp, 1)
                    glp_set_row_name(lp, row, 'int_p'+str(0)+'_v'+str(i))
                    glp_matrix.add(row, colA+i, 1)
                    glp_matrix.add(row, colH[i]+0, M)
                    rhs = -demande.delaiApproche -ligne.compteurFranchissement + phase.intervalle + M
                    glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )


    # Equation suiveurs
    
    for demande in demandesPriorite:
        l = demande.ligne
        ligne = carrefour.listeLignes[l]
        if not ligne.suiveurs:
            for m,k in enumerate(phasesSpecifiques):
                j = K[l].index(k)
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, 'suiveurs_'+ligne.nom)
                for i in V[m]:
                    glp_matrix.add(row, colH[i]+j, 1)
                if k == 0 and ligne.compteurFranchissement >= 0:
                    rhs = 0
                else:
                    rhs = 1
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
    
    if verbose:
        for j in range(glp_get_num_cols(lp)):
            glp_print_col(lp, j+1)
        for i in range(glp_get_num_rows(lp)):
            glp_print_row(lp, i+1)
        print('')
    
    # Leitura variaveis
    status = glp_mip_status(lp)

    if status == GLP_OPT:
        resultat.durees = [round(glp_mip_col_val(lp, colX+k)) for k in range(len(chemin))]
        resultat.deviations = [round(glp_mip_col_val(lp, colU+k)) for k in range(len(chemin))]
        resultat.attentes = [round(glp_mip_col_val(lp, colA+i)) for i in range(len(demandesPriorite))]
        
        # Calcule les phases où passent les véhicules prioritaires
        for i,demande in enumerate(demandesPriorite):
            l = demande.ligne
            varsH = [glp_mip_col_val(lp, colH[i]+j) for j in range(len(K[l]) )]
            for j,Hij in enumerate(varsH):
                if Hij == 1:
                    resultat.passages.append(K[l][j])
                    break
                
        # Identifie le véhicule qui passe au debut et à la fin de chaque phase spécifique
        for m,k in enumerate(phasesSpecifiques):
            varsY = [glp_mip_col_val(lp, colY[m]+j) for j in range(len(V[m]) )]
            for j,Ymj in enumerate(varsY):
                if Ymj == 1:
                    resultat.vehiculesDebut.append(j)
                    break
            else:
                resultat.vehiculesDebut.append(None)
                
            varsZ = [glp_mip_col_val(lp, colZ[m]+j) for j in range(len(V[m]) )]
            for j,Zmj in enumerate(varsZ):
                if Zmj == 1:
                    resultat.vehiculesFin.append(j)
                    break
            else:
                resultat.vehiculesFin.append(None)
        
        
        # Score du chemin
        resultat.score = glp_mip_obj_val(lp)
            
    # Fin
    glp_delete_prob(lp)








def analyseRobustesse(chemin):
    carrefour = chemin.carrefour
    demandesPriorite = carrefour.demandesPriorite
    resultat = chemin.resultat        
        
    # INITIALISATION
    
    # Création du problème
    lp = glp_create_prob()
    glp_matrix = MatriceLP()   

    # Maximise l'objective
    glp_set_obj_dir(lp, GLP_MAX)
      
    # Variables X
    colX = glp_add_cols(lp, len(chemin))
    for k,phase in enumerate(chemin):
        glp_set_col_name(lp, colX+k, 'x'+str(k))
        glp_set_col_bnds(lp, colX+k, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
        glp_set_col_kind(lp, colX+k, GLP_IV)
    
    # x0 >= T
    if carrefour.phaseActuelle.type == 'phase':
        phase0 = chemin.phases[0]
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'x0')
        glp_matrix.add(row, colX+0, 1)
        rhs = carrefour.tempsEcoule
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
    
    # Variables R
    colR = glp_add_cols(lp, len(demandesPriorite))
    for i,demande in enumerate(demandesPriorite):
        glp_set_col_name(lp, colR+i, 'r'+str(i))
        glp_set_col_bnds(lp, colR+i, GLP_LO, resultat.attentes[i], 1000)


    # FONCTION OBJECTIVE
    
    for i,demande in enumerate(demandesPriorite):
        glp_set_obj_coef(lp, colR+i, 1)
    
    # CONTRAINTES    
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(demandesPriorite):
        ligne = carrefour.listeLignes[demande.ligne]
        
        # Somme des durées des interphases
        sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
        for n in range(resultat.passages[i]):
            sommeInterphases += carrefour.interphase(chemin.phases[n], chemin.phases[n+1]).duree
        
        # Marge Fin
        margeFin = ligne.margeFin
        if resultat.passages[i] == 0 and carrefour.phaseActuelle.type == 'phase':
            epsilon = min((-demande.delaiApproche, carrefour.tempsEcoule))
            if epsilon >= margeFin:
                margeFin = epsilon+1
        
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i)+'eq1')
        for n in range(resultat.passages[i]):
            glp_matrix.add(row, colX+n, 1)
        glp_matrix.add(row, colR+i, -1)
        rhs = demande.delaiApproche + carrefour.tempsEcoule - sommeInterphases - ligne.margeDebut
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i)+'eq2')
        for n in range(resultat.passages[i]+1):
            glp_matrix.add(row, colX+n, 1)
        glp_matrix.add(row, colR+i, -1)
        rhs = demande.delaiApproche + carrefour.tempsEcoule - sommeInterphases + margeFin
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
        
                         
    # Contraintes de max 120s de rouge
    for l,ligne in enumerate(carrefour.listeLignes):
        if ligne.couleur == 'red' and ligne.solicitee() and (not chemin.phases[0].lignesActives[l]):
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, ligne.nom)
            
            # Nombre de phases (fermées) du chemin jusqu'à l'ouverture de la ligne
            numPhases = 1
            # Somme des durées des interphases jusqu'à l'ouverture de la ligne
            sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree 
            # Somme des durées nominales des phases hors chemin jusqu'à l'ouverture de la ligne
            sommeNominales = 0 
            
            # Analyse les phases dans le chemin
            for k in range(1, len(chemin) ):
                sommeInterphases += carrefour.interphase(chemin.phases[k-1], chemin.phases[k]).duree
                if chemin.phases[k].lignesActives[l]:
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
                while not phase2.lignesActives[l]:
                    phase1 = phase2
                    phase2 = suivant(phase1, carrefour.listePhases)
                    while not phase2.solicitee:
                        phase2 = suivant(phase2, carrefour.listePhases)

                    sommeInterphases += carrefour.interphase(phase1, phase2).duree
                    sommeNominales += phase1.dureeNominale
            
            # Ecrit la contrainte
            for k in range(numPhases):
                glp_matrix.add(row, colX+k, 1)
            
            rhs = 120 - ligne.compteurRouge + carrefour.tempsEcoule - sommeInterphases - sommeNominales;
            glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
                
            
    # Un véhicule au début et fin de chaque phase spécifique
    phasesSpecifiques = [k for k,phase in enumerate(chemin) if phase.specifique]
    for m,k in enumerate(phasesSpecifiques):
        # Somme des durées des interphases
        sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
        for n in range(k):
            sommeInterphases += carrefour.interphase(chemin.phases[n], chemin.phases[n+1]).duree
        
        # Equation debut
        i = resultat.vehiculesDebut[m]
        if i != None:
            demande = demandesPriorite[i]
            ligne = carrefour.listeLignes[demande.ligne]
            
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 's'+str(m)+'debut')
            for n in range(k):
                glp_matrix.add(row, colX+n, 1)
            glp_matrix.add(row, colR+i, -1)
            rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases - ligne.margeDebut
            glp_set_row_bnds(lp, row, GLP_FX, float(rhs), float(rhs))
        
        # Equation fin
        i = resultat.vehiculesFin[m]
        if i != None:
            demande = demandesPriorite[i]
            ligne = carrefour.listeLignes[demande.ligne]
            
            # Marge Fin
            margeFin = ligne.margeFin
            if k == 0 and carrefour.phaseActuelle.type == 'phase':
                epsilon = min((-demande.delaiApproche, carrefour.tempsEcoule))
                if epsilon >= margeFin:
                    margeFin = epsilon+1
            
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row, 's'+str(m)+'fin')
            for n in range(k+1):
                glp_matrix.add(row, colX+n, 1)
            glp_matrix.add(row, colR+i, -1)
            rhs = carrefour.tempsEcoule + demande.delaiApproche - sommeInterphases + margeFin
            glp_set_row_bnds(lp, row, GLP_FX, float(rhs), float(rhs))
               
    
    # Contraintes d'intervalle entre véhicules dans la même phase spécifique
    for i,demandeI in enumerate(demandesPriorite[:-1]):
        for j,demandeJ in enumerate(demandesPriorite[i+1:],i+1):
            k = resultat.passages[i]
            if k > 0 and resultat.passages[j] == k:
                phase = chemin.phases[k]
                if phase.intervalle >= 0:
                    
                    ligneI = carrefour.listeLignes[demandeI.ligne]
                    ligneJ = carrefour.listeLignes[demandeJ.ligne]
                    
                    # Marges Fin
                    margeFinI = ligneI.margeFin
                    if k == 0 and carrefour.phaseActuelle.type == 'phase' and phase.lignesActives[demandeI.ligne]:
                        epsilonI = min((-demandeI.delaiApproche, carrefour.tempsEcoule))
                        if epsilonI >= margeFin:
                            margeFinI = epsilonI + 1
                            
                    margeFinJ = ligneJ.margeFin
                    if k == 0 and carrefour.phaseActuelle.type == 'phase' and phase.lignesActives[demandeJ.ligne]:
                        epsilonJ = min((-demandeJ.delaiApproche, carrefour.tempsEcoule))
                        if epsilonJ >= margeFin:
                            margeFinJ = epsilonJ + 1
                    
                    # Equation 1
                    row = glp_add_rows(lp, 1)
                    glp_set_row_name(lp, row, 'int_p'+str(k)+'_v'+str(i)+'_v'+str(j)+'_eq1')
                    glp_matrix.add(row, colR+i, 1)
                    glp_matrix.add(row, colR+j, -1)
                    rhs = -demandeI.delaiApproche + demandeJ.delaiApproche + margeFinJ + phase.intervalle
                    glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs) )
                    
                    # Equation 2
                    row = glp_add_rows(lp, 1)
                    glp_set_row_name(lp, row, 'int_p'+str(k)+'_v'+str(i)+'_v'+str(j)+'eq2')
                    glp_matrix.add(row, colR+i, -1)
                    glp_matrix.add(row, colR+j, 1)
                    rhs = demandeI.delaiApproche - demandeJ.delaiApproche + margeFinI + phase.intervalle
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
        resultat.retards = [round(glp_mip_col_val(lp, colR+i)) for i in range(len(demandesPriorite))]
            
    # Fin
    glp_delete_prob(lp)
      
    
    
    
    
    
    
    
    
    
        
def repartitionDurees(chemin):
    carrefour = chemin.carrefour
    resultat = chemin.resultat
    demandesPriorite = carrefour.demandesPriorite
    
    # INITIALISATION
    
    # Création du problème
    lp = glp_create_prob()
    glp_matrix = MatriceLP()

    # Minimise l'objective
    glp_set_obj_dir(lp, GLP_MIN)
      
    # Variables X
    colX = glp_add_cols(lp, len(chemin))
    for k,phase in enumerate(chemin.phases):
        glp_set_col_name(lp, colX+k, 'x'+str(k))
        glp_set_col_bnds(lp, colX+k, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
        glp_set_col_kind(lp, colX+k, GLP_IV)
    
    # x0 >= T
    if carrefour.phaseActuelle.type == 'phase':
        phase0 = chemin.phases[0]
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'x0')
        glp_matrix.add(row, colX+0, 1)
        rhs = carrefour.tempsEcoule
        glp_set_row_bnds(lp, row, GLP_LO, float(rhs), 0)
        
    # Variables U
    colU = glp_add_cols(lp, len(chemin))
    for k,phase in enumerate(chemin):
        glp_set_col_name(lp, colU+k, 'u'+str(k+1) )
        glp_set_col_bnds(lp, colU+k, GLP_LO, 0, 0)
        
    # Contraintes des variables U
    for k,phase in enumerate(chemin):
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(k)+'eq1')
        glp_matrix.add(row, colX+k, 1)
        glp_matrix.add(row, colU+k, -1)
        glp_set_row_bnds(lp, row, GLP_UP, 0, phase.dureeNominale)
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'u'+str(k)+'eq2')
        glp_matrix.add(row, colX+k, 1)
        glp_matrix.add(row, colU+k, 1)
        glp_set_row_bnds(lp, row, GLP_LO, phase.dureeNominale, 0)
    
    # Variables D
    colD = glp_add_cols(lp, len(chemin))
    for k,phase in enumerate(chemin.phases):
        glp_set_col_name(lp, colD+k, 'd'+str(k))
        glp_set_col_bnds(lp, colD+k, GLP_LO, 0, 0)
        
        # Fonction Objective
        glp_set_obj_coef(lp, colD+k, 1)
        
    # Contraintes de variables D
    
    # Somme des durees et deviations
    sommeNom = sum([phase.dureeNominale for phase in chemin.phases])
    sommeX = sum([x for x in chemin.resultat.durees])
    sommeU = sum([u for u in chemin.resultat.deviations])
    
    for k,phase in enumerate(chemin.phases):
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'d'+str(k)+'eq1')
        glp_matrix.add(row, colX+k, 1)
        glp_matrix.add(row, colD+k, -sommeX)
        glp_set_row_bnds(lp, row, GLP_UP, 0, phase.dureeNominale*sommeX/sommeNom)
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'d'+str(k)+'eq2')
        glp_matrix.add(row, colX+k, 1)
        glp_matrix.add(row, colD+k, sommeX)
        glp_set_row_bnds(lp, row, GLP_LO, phase.dureeNominale*sommeX/sommeNom, 0)
    
        
    # CONTRAINTES    
    
    row = glp_add_rows(lp, 1)
    glp_set_row_name(lp, row,'sommeX')
    for k in range(len(chemin) ):
        glp_matrix.add(row, colX+k, 1)
    glp_set_row_bnds(lp, row, GLP_FX, sommeX, sommeX)
    
    row = glp_add_rows(lp, 1)
    glp_set_row_name(lp, row,'sommeU')
    for k in range(len(chemin) ):
        glp_matrix.add(row, colU+k, 1)
    glp_set_row_bnds(lp, row, GLP_FX, sommeU, sommeU)
    
    # Fixe les durées des phases spécifiques
    for k,phase in enumerate(chemin):
        if phase.specifique:
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row,'duree '+str(k) )
            glp_matrix.add(row, colX+k, 1)
            glp_set_row_bnds(lp, row, GLP_FX, resultat.durees[k], resultat.durees[k])
    
    
    # Contraintes de délai d'approche
    
    # Pour chaque véhicule
    for i,demande in enumerate(demandesPriorite):
        ligne = carrefour.listeLignes[demande.ligne]
        
        # Somme des durées des interphases
        sommeInterphases = 0 if carrefour.phaseActuelle.type == 'phase' else carrefour.phaseActuelle.duree
        for n in range(resultat.passages[i]):
            sommeInterphases += carrefour.interphase(chemin.phases[n], chemin.phases[n+1]).duree
            
        # Marge Fin
        margeFin = ligne.margeFin
        if resultat.passages[i] == 0 and carrefour.phaseActuelle.type == 'phase':
            epsilon = min((-demande.delaiApproche, carrefour.tempsEcoule))
            if epsilon >= margeFin:
                margeFin = epsilon+1
        
        # Equation 1
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i)+'eq1')
        for n in range(resultat.passages[i]):
            glp_matrix.add(row, colX+n, 1)
        rhs = demande.delaiApproche + resultat.attentes[i] + carrefour.tempsEcoule - sommeInterphases - ligne.margeDebut
        glp_set_row_bnds(lp, row, GLP_UP, 0, float(rhs))
        
        # Equation 2
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row, 'v'+str(i)+'eq2')
        for n in range(resultat.passages[i]+1):
            glp_matrix.add(row, colX+n, 1)
        rhs = demande.delaiApproche + resultat.attentes[i] + carrefour.tempsEcoule - sommeInterphases + margeFin
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
            for k in range(1, len(chemin) ):
                sommeInterphases += carrefour.interphase(chemin.phases[k-1], chemin.phases[k]).duree
                if chemin.phases[k].lignesActives[i]:
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
            
            rhs = 120 - ligne.compteurRouge + carrefour.tempsEcoule - sommeInterphases - sommeNominales;
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
        for k in range(len(chemin)):
            resultat.durees[k] = round(glp_mip_col_val(lp, colX+k))
            resultat.deviations[k] =  round(glp_mip_col_val(lp, colU+k))
        

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