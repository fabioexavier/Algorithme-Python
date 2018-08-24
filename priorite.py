import numpy as np
from chemins import rechercheChemins
from LP import analyseLP

def cheminPrioritaire(carrefour):
    # Calcule tous les chemins possibles
    cheminsPossibles = rechercheChemins(carrefour)
    
    # Analyse chacun des chemins avec la LP
    cheminsFaisables = []
    resultatsFaisables = []
    
    for chemin in cheminsPossibles:
        resultat = analyseLP(chemin)
        if resultat:
            cheminsFaisables.append(chemin)
            resultatsFaisables.append(resultat)
#        print(chemin)
#        print(resultat, end='\n\n')
#    print('')
        
    # Trouve le meilleur chemin
    index = np.argmin([resultat.score for resultat in resultatsFaisables])
    meilleurChemin = cheminsFaisables[index]
    meilleurResultat = resultatsFaisables[index]
    
    # Print
    print("Demandes:", carrefour.demandesPriorite)
    print('')
    print(meilleurChemin)
    print('')
    print(meilleurResultat)
    print('')
    print("Chemins analyses:", len(cheminsPossibles) )
    print('')
    
    # Returns
    dureeActuelle = meilleurResultat.durees[0]
    phaseProchaine = meilleurChemin.phases[1] if len(meilleurChemin) > 1 else None
    
    return dureeActuelle, phaseProchaine



        
