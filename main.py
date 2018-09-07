import tkinter as tk
import gestionIntersections as gi
import guiCarrefour as gc
import numpy as np


# Dossier Reunion
listeLignes = [gi.LigneDeFeu(0, 'B2',  'voiture', 3, True,  True,  3, 1), \
               gi.LigneDeFeu(1, 'P3',  'pieton',  0, False, False, 3, 5), \
               gi.LigneDeFeu(2, 'P4',  'pieton',  0, False, False, 3, 5), \
               gi.LigneDeFeu(3, 'P5',  'pieton',  0, False, False, 3, 5), \
               gi.LigneDeFeu(4, 'L6',  'voiture', 3, False, True,  3, 1), \
               gi.LigneDeFeu(5, 'P7',  'pieton',  0, False, False, 3, 5), \
               gi.LigneDeFeu(6, 'L8',  'voiture', 3, False, False, 3, 1), \
               gi.LigneDeFeu(7, 'P9',  'pieton',  0, False, False, 3, 5), \
               gi.LigneDeFeu(8, 'L10', 'voiture', 3, False, False, 3, 1), \
               gi.LigneDeFeu(9, 'P11', 'pieton',  0, False, False, 3, 1)]
               
listePhases = [gi.Phase(0, [False, False, False, True,  True,  False, False, True,  True,  False], 15, 54, 80, False, False, -1), \
               gi.Phase(1, [True,  True,  False, False, False, False, False, False, False, True ],  3,  4, 30, True,  True,  15), \
               gi.Phase(2, [False, True,  True,  False, False, True,  True,  False, False, True ], 10, 17, 35, False, False, -1), \
               gi.Phase(3, [True,  False, False, True,  False, False, False, True,  False, False],  3,  4, 30, True,  True,  15)  ]
               

matriceSecurite = [[0,0,1,0,2,4,2,0,2,0],   \
                   [0,0,0,0,8,0,0,0,0,0],   \
                   [8,0,0,0,6,0,0,0,0,0],   \
                   [0,0,0,0,0,0,2,0,0,0],   \
                   [2,1,4,0,0,0,1,0,0,4],   \
                   [5,0,0,0,0,0,0,0,5,0],   \
                   [2,0,0,4,2,0,0,1,1,0],   \
                   [0,0,0,0,0,0,7,0,0,0],   \
                   [1,0,0,0,0,3,1,0,0,1],   \
                   [0,0,0,0,6,0,0,0,8,0]]

# Dossier 6
#listeLignes = [gi.LigneDeFeu(0, 'T1', 'voiture', 3, 1),   \
#               gi.LigneDeFeu(1, 'T2', 'voiture', 3, 1),   \
#               gi.LigneDeFeu(2, 'P8', 'pieton', 0, 0),   \
#               gi.LigneDeFeu(3, 'F5', 'voiture', 3, 0),  \
#               gi.LigneDeFeu(4, 'P7', 'pieton', 0, 0),   \
#               gi.LigneDeFeu(5, 'F3', 'voiture', 3, 0),  \
#               gi.LigneDeFeu(6, 'P9', 'pieton', 0, 0),   \
#               gi.LigneDeFeu(7, 'F6', 'voiture', 3, 0),  \
#               gi.LigneDeFeu(8, 'P12', 'pieton', 0, 0),  \
#               gi.LigneDeFeu(9, 'P11', 'pieton', 0, 0),  \
#               gi.LigneDeFeu(10, 'F4', 'voiture', 3, 0), \
#               gi.LigneDeFeu(11, 'P10', 'pieton', 0, 0)]
#
#listePhases = [gi.Phase(0, [False, False, True, True, False, True, False, False, True, True, False, True], 10, 54, 70, False, 0, False, 0, -1), \
#               gi.Phase(1, [True, True, False, False, True, False, True, False, True, True, False, True], 3, 3, 30, True, 1, True, 3, 15),      \
#               gi.Phase(2, [False, False, True, False, True, False, True, False, False, False, True, False], 6, 6, 30, True, 0, False, 0, -1),    \
#               gi.Phase(3, [True, True, False, False, True, False, True, False, True, True, False, True], 3, 3, 30, True, 1, True, 3, 15),      \
#               gi.Phase(4, [False, False, True, False, True, False, True, True, False, False, False, True], 10, 17, 40, False, 0, False, 0, -1),\
#               gi.Phase(5, [True, True, False, False, True, False, True, False, True, True, False, True], 3, 3, 30, True, 1, True, 3, 15)]
#
#matriceSecurite = [[0,0,5,0,0,2,0,0,0,0,2,0],   \
#                   [0,0,1,0,0,2,0,0,0,0,2,0],   \
#                   [4,7,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,5,0,0,3,0,0,1,0],   \
#                   [0,0,0,3,0,0,0,0,0,0,0,0],   \
#                   [4,4,0,0,0,0,1,5,0,0,2,0],   \
#                   [0,0,0,0,0,6,0,0,0,0,0,0],   \
#                   [0,0,0,2,0,2,0,0,1,0,2,0],   \
#                   [0,0,0,0,0,0,0,9,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,0,4,0],   \
#                   [3,3,0,5,0,1,0,4,0,6,0,1],   \
#                   [0,0,0,0,0,0,0,0,0,0,9,0]]
    
carrefour = gi.Carrefour(listeLignes, listePhases, matriceSecurite)

#nPhases = len(carrefour.listePhases)
#MDI = np.zeros((nPhases,nPhases))
#for i in range(nPhases):
#    for j in range(nPhases):
#        if i != j:
#            MDI[i,j] = carrefour.matriceInterphase[i][j].duree
#
#print(MDI)

# Criação da interface grafica
mainWindow = tk.Tk()
mainWindow.title("Simulateur de Carrefour")
app = gc.AppIntersection(mainWindow, carrefour)
mainWindow.mainloop()
        
