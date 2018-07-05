#import time
import tkinter as tk
import gestionIntersections as gi
import guiCarrefour as gc
#import numpy as np


# Dossier 1
listeLignes = [gi.LigneDeFeu('T1', 'Voiture', 3),   \
               gi.LigneDeFeu('P8', 'Pieton', 0),    \
               gi.LigneDeFeu('T2', 'Voiture', 3),   \
               gi.LigneDeFeu('P13', 'Pieton', 0),   \
               gi.LigneDeFeu('V3', 'Voiture', 3),   \
               gi.LigneDeFeu('P9', 'Pieton', 0),    \
               gi.LigneDeFeu('P12', 'Pieton', 0),   \
               gi.LigneDeFeu('V5', 'Voiture', 3),   \
               gi.LigneDeFeu('P7', 'Pieton', 0),    \
               gi.LigneDeFeu('V6', 'Voiture', 3),   \
               gi.LigneDeFeu('V4', 'Voiture', 3),   \
               gi.LigneDeFeu('P11', 'Pieton', 0),   \
               gi.LigneDeFeu('P10', 'Pieton', 0),   \
               gi.LigneDeFeu('P14', 'Pieton', 0)]

listePhases = [gi.Phase(0, [False, True, False, True, True, False, False, True, False, False, False, True, True, True], 6, 10, 10, False, False, False),\
               gi.Phase(1, [False, True, False, True, True, False, False, False, False, False, False, True, True, True], 6, 19, 38, False, False, False),\
               gi.Phase(2, [True, False, True, False, False, True, True, False, True, False, False, True, True, True], 3, 3, 20, True, True, True),\
               gi.Phase(3, [False, False, False, False, False, True, True, False, True, True, False, False, False, False], 6, 6, 6, True, False, False),\
               gi.Phase(4, [False, False, False, False, False, True, True, False, True, True, True, False, False, False], 8, 32, 64, False, False, False),\
               gi.Phase(5, [True, False, True, False, False, True, True, False, True, False, False, True, True, True], 3, 3, 20, True, True, True)]

matriceSecurite = [[0,1,0,8,6,0,0,6,0,6,6,0,0,0],   \
                   [7,0,1,0,0,0,0,0,0,0,0,0,0,0],   \
                   [0,8,0,1,8,0,0,8,0,8,8,0,0,0],   \
                   [1,0,7,0,0,0,0,0,0,0,0,0,0,0],   \
                   [3,0,3,0,0,1,8,0,0,7,7,0,0,0],   \
                   [0,0,0,0,4,0,0,0,0,0,0,0,0,0],   \
                   [0,0,0,0,1,0,0,0,0,0,0,0,0,0],   \
                   [3,0,3,0,0,0,0,0,3,1,1,0,0,0],   \
                   [0,0,0,0,0,0,0,2,0,0,0,0,0,0],   \
                   [6,0,6,0,2,0,0,6,0,0,0,1,0,8],   \
                   [6,0,6,0,2,0,0,6,0,0,0,1,0,8],   \
                   [0,0,0,0,0,0,0,0,0,12,12,0,0,0], \
                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0],   \
                   [0,0,0,0,0,0,0,0,0,1,1,0,0,0]]


carrefour = gi.Carrefour(listeLignes, listePhases, matriceSecurite)

# Criação da interface grafica
mainWindow = tk.Tk()
mainWindow.title("Simulateur de Carrefour")
app = gc.AppIntersection(mainWindow, carrefour)
mainWindow.mainloop()

