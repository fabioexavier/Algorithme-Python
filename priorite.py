import numpy as np
from chemins import rechercheChemins
from LP import analyseLP
from robustesse import analyseRobustesse

def cheminPrioritaire(carrefour):
    # Calcule tous les chemins possibles
    cheminsPossibles = rechercheChemins(carrefour)
    
    # Analyse chacun des chemins avec la LP
    cheminsFaisables = []
    
    for chemin in cheminsPossibles:
        analyseLP(chemin)
        if chemin.resultat:
            cheminsFaisables.append(chemin)
#        print(chemin)
#        print(chemin.resultat)
#        print('')
#    print('')
        
    # Trouve le meilleur chemin
    print("Demandes:", carrefour.demandesPriorite)
    print ('')
    print("Meilleur chemin: ")
    print('')
    cheminsFaisables.sort(key=lambda chemin: chemin.resultat.score)
    for chemin in cheminsFaisables:
    # Analyse la robustesse des chemins en ordre
#        print(chemin)
#        print(chemin.resultat)
        robuste = analyseRobustesse(chemin)
#        print("Robuste" if robuste else "Pas Robuste")
#        print('')
        if robuste:
            meilleurChemin = chemin
            break
    else:
#        print("Pas de chemin robuste")
#        print('')
        meilleurChemin = cheminsFaisables[0]
    
    print(meilleurChemin)
    print(meilleurChemin.resultat)
#    print("Chemins analyses:", len(cheminsPossibles) )
    print('')
    
    # Returns
    dureeActuelle = meilleurChemin.resultat.durees[0]
    phaseProchaine = meilleurChemin.phases[1] if len(meilleurChemin) > 1 else None
    
    return dureeActuelle, phaseProchaine



        
