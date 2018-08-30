from timeit import default_timer as timer

from chemins import rechercheChemins
from LP import analyseAttentes, analyseRobustesse, repartitionDurees

def cheminPrioritaire(carrefour):
    begin = timer()
    
    # Calcule tous les chemins possibles
    cheminsPossibles = rechercheChemins(carrefour)
    
    # Analyse chacun des chemins avec la LP
    cheminsFaisables = []
    
    for chemin in cheminsPossibles:
        analyseAttentes(chemin)
        if chemin.resultat:
            cheminsFaisables.append(chemin)
        
    # Trouve le meilleur chemin
    cheminsFaisables.sort(key=lambda chemin: chemin.resultat.score)
    for chemin in cheminsFaisables:
        analyseRobustesse(chemin)
        if all(retard >= 0.2*demande.delaiApproche for retard,demande in zip(chemin.resultat.retards, carrefour.demandesPriorite) ):
            meilleurChemin = chemin
            break
    else:
        cheminsFaisables.sort(key=lambda chemin: min(chemin.resultat.retards) )
        meilleurChemin = cheminsFaisables[0]
    
    # Derniere repartition des durees pour garder les proportions le plus possible
    repartitionDurees(meilleurChemin)
    
    end = timer()
    
    print("Demandes:", carrefour.demandesPriorite, '\n')
    for chemin in cheminsFaisables:
        print(chemin, '\n')
        print(chemin.resultat, '\n')
    print("Meilleur chemin:", '\n')
    print(meilleurChemin, '\n')
    print(meilleurChemin.resultat, '\n')
    print("Chemins analyses:", len(cheminsPossibles) )
    print("Temps:", 1000*(end-begin), "ms", '\n\n\n\n')
    
    # Returns
    dureeActuelle = meilleurChemin.resultat.durees[0]
    phaseProchaine = meilleurChemin.phases[1] if len(meilleurChemin) > 1 else None
    
    return dureeActuelle, phaseProchaine
