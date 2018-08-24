from copy import deepcopy
from math import ceil

from LP import analyseLP

def analyseRobustesse(chemin):
    demandesOriginales = chemin.carrefour.demandesPriorite
    
    # Pour toutes les possibles combinaisons de véhicules en retard
    for mask in range(1, 2**len(demandesOriginales) ):
        demandesRetard = deepcopy(demandesOriginales)
    
        for i,(demandeO,demandeR) in enumerate(zip(demandesOriginales, demandesRetard) ):
            if (1 << i) & mask:
                demandeR.delaiApproche = ceil(demandeO.delaiApproche*1.2)
#        print('')
#        print("Demandes avec Retard:", demandesRetard)
        cheminRetard = chemin.copy()
        analyseLP(cheminRetard, demandesRetard)
#        print(chemin.resultat)
        if not cheminRetard.resultat:
            return False

    return True