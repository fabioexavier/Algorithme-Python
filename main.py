import time
import gestionIntersections as gi


# Dados
        
#ligne0 = LigneDeFeu('F0', 'Voiture', 3)
#ligne1 = LigneDeFeu('F1', 'Voiture', 3)
#ligne2 = LigneDeFeu('P2', 'Pieton', 0)
#self.listeLignes = [ligne0, ligne1, ligne2]
#
#phase0 = Phase(0, [True, False, False], 8)
#phase1 = Phase(1, [False, True, True], 8)
#self.listePhases = [phase0, phase1]
#
#self.matriceSecurite = [[0, 2, 3],[2, 0, 0],[6, 0, 0]]


ligne0 = gi.LigneDeFeu('F0', 'Voiture', 3)
ligne1 = gi.LigneDeFeu('P1', 'Pieton', 0)
ligne2 = gi.LigneDeFeu('F2', 'Voiture', 3)
ligne3 = gi.LigneDeFeu('F3', 'Voiture', 3)
ligne4 = gi.LigneDeFeu('P4', 'Pieton', 0)
ligne5 = gi.LigneDeFeu('F5', 'Voiture', 3)
listeLignes = [ligne0, ligne1, ligne2, ligne3, ligne4, ligne5]

phase0 = gi.Phase(0, [True, False, False, True, True, False], 8)
phase1 = gi.Phase(1, [False, True, True, False, False, False], 8)
phase2 = gi.Phase(2, [False, False, False, False, False, True], 8)
listePhases = [phase0, phase1, phase2]

matriceSecurite = [[0, 1, 2, 0, 0, 1],[8, 0, 0, 6, 0, 8],[2, 0, 0, 1, 2, 1],[0, 2, 3, 0, 0, 0],[0, 0, 8, 0, 0, 7],[1, 1, 2, 0, 3, 0]]

carrefour = gi.Carrefour(listeLignes, listePhases, matriceSecurite)

while(True):
    carrefour.update()
    carrefour.output()
    time.sleep(1)