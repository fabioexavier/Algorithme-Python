#import time
import tkinter as tk
import gestionIntersections as gi
import guiCarrefour as gc

#ligne0 = gi.LigneDeFeu('F0', 'Voiture', 3)
#ligne1 = gi.LigneDeFeu('P1', 'Pieton', 0)
#ligne2 = gi.LigneDeFeu('F2', 'Voiture', 3)
#ligne3 = gi.LigneDeFeu('P3', 'Pieton', 0)
#ligne4 = gi.LigneDeFeu('B4', 'Voiture', 3)
#listeLignes = [ligne0, ligne1, ligne2, ligne3, ligne4]
#
#phase0 = gi.Phase(0, [True, True, False, False, False], 12, 25, 50, False, False)
#phase1 = gi.Phase(1, [False, False, False, True, True], 6, 10, 20, True, True)
#phase2 = gi.Phase(2, [False, False, True, True, False], 10, 18, 35, False, False)
#phase3 = gi.Phase(3, [False, True, False, False, True], 6, 10, 20, True, True)
#listePhases = [phase0, phase1, phase2, phase3]
#
#matriceSecurite = [[0, 0, 2, 1, 2],
#                   [0, 0, 8, 0, 0],
#                   [2, 1, 0, 0, 2],
#                   [8, 0, 0, 0, 6],
#                   [2, 0, 2, 2, 0]]

# Exemplo 3
ligne0 = gi.LigneDeFeu('F0', 'Voiture', 3)
ligne1 = gi.LigneDeFeu('P1', 'Pieton', 0)
ligne2 = gi.LigneDeFeu('F2', 'Voiture', 3)
ligne3 = gi.LigneDeFeu('P3', 'Pieton', 0)
ligne4 = gi.LigneDeFeu('B4', 'Voiture', 3)
listeLignes = [ligne0, ligne1, ligne2, ligne3, ligne4]

phase0 = gi.Phase(0, [True, True, False, False, False], 15, 40, 99999, False, False)
phase1 = gi.Phase(1, [False, False, False, True, True], 6, 10, 20, True, True)
phase2 = gi.Phase(2, [False, False, True, True, False], 10, 18, 18, True, False)
phase3 = gi.Phase(3, [False, True, False, False, True], 6, 10, 20, True, True)
listePhases = [phase0, phase1, phase2, phase3]

matriceSecurite = [[0, 0, 2, 1, 2],
                   [0, 0, 8, 0, 0],
                   [2, 1, 0, 0, 2],
                   [8, 0, 0, 0, 6],
                   [2, 0, 2, 2, 0]]


carrefour = gi.Carrefour(listeLignes, listePhases, matriceSecurite)

# Criação da interface grafica
mainWindow = tk.Tk()
mainWindow.title("Simulateur de Carrefour")
app = gc.AppIntersection(mainWindow, carrefour)
mainWindow.mainloop()

