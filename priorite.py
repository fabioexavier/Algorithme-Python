import numpy as np
from chemins import rechercheChemins
from LP import analyseLP

def cheminPrioritaire(carrefour):
    print("Demandes:", carrefour.demandesPriorite, end='\n\n')
    
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
        print(chemin)
        print(resultat, end='\n\n')
    print('')
        
    # Trouve le meilleur chemin
    index = np.argmin([resultat.score for resultat in resultatsFaisables])
    meilleurChemin = cheminsFaisables[index]
    meilleurResultat = resultatsFaisables[index]
    
    # Print
    print('Meilleur Chemin:')
    print(meilleurChemin)
    print(meilleurResultat)
    print("Chemins analysés:", len(cheminsPossibles) )
    
    # Returns
    dureeActuelle = meilleurResultat.durees[0]
    phaseProchaine = meilleurChemin.phases[1] if len(meilleurChemin) > 1 else None
    
    return dureeActuelle, phaseProchaine



        
