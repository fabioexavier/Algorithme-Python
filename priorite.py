from swiglpk import *
from LP import MatriceLP, suivant

from copy import deepcopy
from math import ceil
import numpy as np

from timeit import default_timer as timer

from chemins import rechercheChemins
from LP import analyseLP

def cheminPrioritaire(carrefour):
    begin = timer()
    
    # Calcule tous les chemins possibles
    cheminsPossibles = rechercheChemins(carrefour)
    
    # Analyse chacun des chemins avec la LP
    cheminsFaisables = []
    
    for chemin in cheminsPossibles:
        analyseLP(chemin)
        if chemin.resultat:
            cheminsFaisables.append(chemin)
#        print(chemin, '\n')
        
    # Trouve le meilleur chemin
    cheminsFaisables.sort(key=lambda chemin: chemin.resultat.score)
    for chemin in cheminsFaisables:
    # Analyse la robustesse des chemins en ordre
        robuste = analyseRobustesse(chemin)
#        print("Robuste" if robuste else "Pas Robuste", '\n')
        if robuste:
            meilleurChemin = chemin
            break
    else:
        print("Pas de chemin robuste", '\n')
        meilleurChemin = cheminsFaisables[0]
    
    # Fait la repartition des duréees pour garder la proportion
    repartitionDurees(meilleurChemin)
    
    end = timer()
    
    print("Demandes:", carrefour.demandesPriorite, '\n')
    print("Meilleur chemin:", '\n')
    print(meilleurChemin, '\n')
    print(meilleurChemin.resultat, '\n')
    print("Chemins analyses:", len(cheminsPossibles) )
    print("Temps:", 1000*(end-begin), "ms", '\n\n')
    
    # Returns
    dureeActuelle = meilleurChemin.resultat.durees[0]
    phaseProchaine = meilleurChemin.phases[1] if len(meilleurChemin) > 1 else None
    
    return dureeActuelle, phaseProchaine



def analyseRobustesse(chemin):
    demandesOriginales = chemin.carrefour.demandesPriorite
    
    # Pour toutes les possibles combinaisons de véhicules en retard
    for mask in range(1, 2**len(demandesOriginales) ):
        demandesRetard = deepcopy(demandesOriginales)
    
        for i,(demandeO,demandeR) in enumerate(zip(demandesOriginales, demandesRetard) ):
            if (1 << i) & mask:
#                demandeR.delaiApproche = ceil(demandeO.delaiApproche*1.2)
                demandeR.delaiApproche = ceil(demandeO.delaiApproche + 10)
#        print('')
#        print("Demandes avec Retard:", demandesRetard)
        cheminRetard = chemin.copy()
        analyseLP(cheminRetard, demandesRetard)
#        print(chemin.resultat)
        if not cheminRetard.resultat:
            return False

    return True


def repartitionDurees(chemin):
    carrefour = chemin.carrefour
    resultat = chemin.resultat
    
    
    if resultat.premierPassage > 1:
        # Calcule la deviation (signée) prévue pour les phases avant le premier passage d'un véhicule prioritaire
        deviationTotale = 0
        for i in range(resultat.premierPassage):
            deviationTotale += (resultat.durees[i] - chemin.phases[i].dureeNominale)
        
        
        # Modo 1: nao checa nem max/min, nem 120s das linhas
        
#        dureesNom = [phase.dureeNominale for phase in chemin.phases[:resultat.premierPassage] ] 
#        sommeNom = sum(dureesNom)
#        for i,duree in enumerate(dureesNom):
#            resultat.durees[i] = round(duree +  (duree/sommeNom)*deviationTotale)
#            resultat.deviations[i] = abs(resultat.durees[i] - chemin.phases[i].dureeNominale)
        
        
        
        # Modo 2: cuida max/min mas nao os 120s
        
#        dureesMin = [phase.dureeMinimale for phase in chemin.phases[:resultat.premierPassage] ]
#        if dureesMin:
#            dureesMin[0] = min( (dureesMin[0], chemin.carrefour.tempsPhase) )
#        dureesNom = [phase.dureeNominale for phase in chemin.phases[:resultat.premierPassage] ]    
#        dureesMax = [phase.dureeMaximale for phase in chemin.phases[:resultat.premierPassage] ]
#        
#        durees = dureesNom.copy()
#        
#        # Distribue les secondes de déviations en respectant les min/max et en guardant la proportion des durées nominales
#        if deviationTotale > 0:
#            rapports = [nomi/(duree+1) if duree < maxi else 0 for duree,nomi,maxi in zip(durees, dureesNom, dureesMax)]
#            for i in range(deviationTotale):
#                index = np.argmax(rapports)
#                durees[index] += 1
#                rapports[index] = dureesNom[index]/(durees[index]+1) if durees[index] < dureesMax[index] else 0
#        
#        if deviationTotale < 0:
#            rapports = [(duree-1)/nomi if duree > mini else 0 for duree,nomi,mini in zip(durees, dureesNom, dureesMin)]
#            for i in range(-deviationTotale):
#                index = np.argmax(rapports)
#                durees[index] -= 1
#                rapports[index] = (durees[index]-1)/dureesNom[index] if durees[index] > dureesMin[index] else 0
#                
#        for i,duree in enumerate(durees):
#            resultat.durees[i] = duree
#            resultat.deviations[i] = abs(duree - chemin.phases[i].dureeNominale)
            
        
        
        
        # Modo 3: Simplex
        
        # INITIALISATION
        
        # Création du problème
        lp = glp_create_prob()
    
        # Minimise l'objective
        glp_set_obj_dir(lp, GLP_MIN)
          
        # Variables X
        colX = glp_add_cols(lp, resultat.premierPassage)
        for i,phase in enumerate(chemin.phases[:resultat.premierPassage]):
            glp_set_col_name(lp, colX+i, 'x'+str(i+1))
            glp_set_col_bnds(lp, colX+i, GLP_DB, phase.dureeMinimale, phase.dureeMaximale)
            glp_set_col_kind(lp, colX+i, GLP_IV)
        
        phase0 = chemin.phases[0]
        if carrefour.tempsPhase > phase0.dureeMinimale:
            if carrefour.tempsPhase < phase0.dureeMaximale:
                glp_set_col_bnds(lp, colX,GLP_DB, carrefour.tempsPhase, phase0.dureeMaximale)
            else:
                glp_set_col_bnds(lp, colX,GLP_FX, carrefour.tempsPhase, carrefour.tempsPhase)
            
        # Variables U
        colU = glp_add_cols(lp, resultat.premierPassage)
        for i,phase in enumerate(chemin.phases[:resultat.premierPassage]):
            glp_set_col_name(lp, colU+i, 'u'+str(i+1))
            glp_set_col_bnds(lp, colU+i, GLP_LO, 0, 0)
            
            # Fonction Objective
            glp_set_obj_coef(lp, colU+i, 1)
        
            
        # CONTRAINTES    
        
        glp_matrix = MatriceLP()
        
        # Somme des durees
        sommeNom = sum([phase.dureeNominale for phase in chemin.phases[:resultat.premierPassage] ] )
        sommeX = sommeNom + deviationTotale
        
        row = glp_add_rows(lp, 1)
        glp_set_row_name(lp, row,'somme')
        for i in range(resultat.premierPassage):
            glp_matrix.add(row, colX+i, 1)
        glp_set_row_bnds(lp, row, GLP_FX, sommeX, sommeX)
        
        # Contraintes de variables U
        for i,phase in enumerate(chemin.phases[:resultat.premierPassage]):
            # Equation 1
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row,'u'+str(i+1)+'eq1')
            glp_matrix.add(row, colX+i, 1)
            glp_matrix.add(row, colU+i, -sommeX)
            glp_set_row_bnds(lp, row, GLP_UP, 0, phase.dureeNominale*sommeX/sommeNom)
            
            # Equation 2
            row = glp_add_rows(lp, 1)
            glp_set_row_name(lp, row,'u'+str(i+1)+'eq2')
            glp_matrix.add(row, colX+i, 1)
            glp_matrix.add(row, colU+i, sommeX)
            glp_set_row_bnds(lp, row, GLP_LO, phase.dureeNominale*sommeX/sommeNom, 0)
        
        # Contraintes de max 120s de rouge
        for i,ligne in enumerate(carrefour.listeLignes):
            if ligne.couleur == 'red' and ligne.solicitee():
                row = glp_add_rows(lp, 1)
                glp_set_row_name(lp, row, ligne.nom)
                
                numPhases = 1 # Nombre de phases (fermées) du chemin jusqu'à l'ouverture de la ligne ou le premier passage de véhicule
                sommeInterphases = 0 # Somme des durées des interphases jusqu'à l'ouverture de la ligne
                sommeNominales = 0 # Somme des durées nominales des phases hors chemin jusqu'à l'ouverture de la ligne
                sommeXFixes = 0 # Somme des durées des phases à partir du premier passage de véhicule jusqu'à l'ouverture de la ligne
                
                # Analyse les phases dans le chemin
                for j in range(1, len(chemin) ):
                    sommeInterphases += carrefour.interphase(chemin.phases[j-1], chemin.phases[j]).duree
                    if chemin.phases[j].lignesActives[i]:
                        break
                    else:
                        if numPhases <  resultat.premierPassage:
                            numPhases += 1  
                        else:
                            sommeXFixes += resultat.durees[j]
                        
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
                
                rhs = 120 - ligne.compteurRouge + carrefour.tempsPhase - sommeXFixes - sommeInterphases - sommeNominales;
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
            for i in range(resultat.premierPassage):
                resultat.durees[i] = round(glp_mip_col_val(lp, colX+i))
                resultat.deviations[i] = abs(resultat.durees[i] - chemin.phases[i].dureeNominale)