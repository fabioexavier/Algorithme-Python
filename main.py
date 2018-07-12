import tkinter as tk
import gestionIntersections as gi
import guiCarrefour as gc
#import numpy as np


## Dossier 3
#listeLignes = [gi.LigneDeFeu(0, 'T1', 'Voiture', 3, True),   \
#               gi.LigneDeFeu(1, 'T2', 'Voiture', 3, True),    \
#               gi.LigneDeFeu(2, 'P10', 'Pieton', 0, False),   \
#               gi.LigneDeFeu(3, 'F4', 'Voiture', 3, False),   \
#               gi.LigneDeFeu(4, 'P6', 'Pieton', 0, False),   \
#               gi.LigneDeFeu(5, 'F3', 'Voiture', 3, False),    \
#               gi.LigneDeFeu(6, 'P7', 'Pieton', 0, False),   \
#               gi.LigneDeFeu(7, 'F5', 'Voiture', 3, False),   \
#               gi.LigneDeFeu(8, 'P9', 'Pieton', 0, False),    \
#               gi.LigneDeFeu(9, 'P8', 'Pieton', 0, False),   \
#               gi.LigneDeFeu(10, 'F11', 'Voiture', 3, False),  \
#               gi.LigneDeFeu(11, 'P15', 'Pieton', 0, False),  \
#               gi.LigneDeFeu(12, 'P17', 'Pieton', 0, False),  \
#               gi.LigneDeFeu(13, 'F13', 'Voiture', 3, False),  \
#               gi.LigneDeFeu(14, 'P18', 'Pieton', 0, False),  \
#               gi.LigneDeFeu(15, 'P14', 'Pieton', 0, False),  \
#               gi.LigneDeFeu(16, 'F12', 'Voiture', 3, False),  \
#               gi.LigneDeFeu(17, 'P16', 'Pieton', 0, False),  \
#               gi.LigneDeFeu(18, 'F19', 'Voiture', 3, False)]
#
#listePhases = [gi.Phase(0, [False, False, True, True, False, True, False, False, True, True, True, False, False, True, False, False, False, True, True], 10, 30, 60, False, False, False),\
#               gi.Phase(1, [False, False, True, False, False, True, False, False, False, False, False, False, False, True, False, False, False, False, False], 1, 2, 10, False, False, False),\
#               gi.Phase(2, [True, True, False, False, True, False, True, False, False, False, False, True, True, False, True, True, True, False, False], 8, 17, 40, False, True, False),\
#               gi.Phase(3, [False, False, True, False, True, False, True, True, False, False, True, False, False, False, False, False, False, True, False], 8, 16, 40, False, False, False),\
#               gi.Phase(4, [True, True, False, False, True, False, True, False, True, True, True, False, False, True, False, False, False, True, False], 3, 3, 20, True, True, True)]
#
#matriceSecurite = [[0,0,3,2,0,2,0,2,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,1,2,0,2,0,2,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [6,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [3,3,0,0,4,0,0,2,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [4,4,0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,6,0,0,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [2,2,0,3,0,3,0,0,1,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,6,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,1,4,0,0,0,2,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,6,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,1,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,1,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

# Dossier 6
listeLignes = [gi.LigneDeFeu(0, 'T1', 'Voiture', 3, True),   \
               gi.LigneDeFeu(1, 'T2', 'Voiture', 3, True),    \
               gi.LigneDeFeu(2, 'P8', 'Pieton', 0, False),   \
               gi.LigneDeFeu(3, 'F5', 'Voiture', 3, False),   \
               gi.LigneDeFeu(4, 'P7', 'Pieton', 0, False),   \
               gi.LigneDeFeu(5, 'F3', 'Voiture', 3, False),    \
               gi.LigneDeFeu(6, 'P9', 'Pieton', 0, False),   \
               gi.LigneDeFeu(7, 'F6', 'Voiture', 3, False),   \
               gi.LigneDeFeu(8, 'P12', 'Pieton', 0, False),    \
               gi.LigneDeFeu(9, 'P11', 'Pieton', 0, False),   \
               gi.LigneDeFeu(10, 'F4', 'Voiture', 3, False),  \
               gi.LigneDeFeu(11, 'P10', 'Pieton', 0, False)]

listePhases = [gi.Phase(0, [False, False, True, True, False, True, False, False, True, True, False, True], 10, 54, 80, False, False, False),\
               gi.Phase(1, [True, True, False, False, True, False, True, False, True, True, False, True], 3, 3, 20, True, True, True),\
               gi.Phase(2, [False, False, True, False, True, False, True, True, False, False, True, True], 6, 6, 20, True, False, False),\
               gi.Phase(3, [True, True, False, False, True, False, True, False, True, True, False, True], 3, 3, 20, True, True, True),\
               gi.Phase(4, [False, False, True, False, True, False, True, True, False, False, False, True], 10, 17, 40, False, False, False),\
               gi.Phase(5, [True, True, False, False, True, False, True, False, True, True, False, True], 3, 3, 20, True, True, True)]

matriceSecurite = [[0,0,5,0,0,2,0,0,0,0,2,0],   \
                   [0,0,1,0,0,2,0,0,0,0,2,0],   \
                   [4,7,0,0,0,0,0,0,0,0,0,0],   \
                   [0,0,0,0,5,0,0,3,0,0,1,0],   \
                   [0,0,0,3,0,0,0,0,0,0,0,0],   \
                   [4,4,0,0,0,0,1,5,0,0,2,0],   \
                   [0,0,0,0,0,6,0,0,0,0,0,0],   \
                   [0,0,0,2,0,2,0,0,1,0,2,0],   \
                   [0,0,0,0,0,0,0,9,0,0,0,0],   \
                   [0,0,0,0,0,0,0,0,0,0,4,0],   \
                   [3,3,0,5,0,1,0,4,0,6,0,1],   \
                   [0,0,0,0,0,0,0,0,0,0,9,0]]
    
carrefour = gi.Carrefour(listeLignes, listePhases, matriceSecurite)

# Criação da interface grafica
mainWindow = tk.Tk()
mainWindow.title("Simulateur de Carrefour")
app = gc.AppIntersection(mainWindow, carrefour)
mainWindow.mainloop()

