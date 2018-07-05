## Exemplo 1
#ligne0 = gi.LigneDeFeu('F0', 'Voiture', 3)
#ligne1 = gi.LigneDeFeu('P1', 'Pieton', 0)
#ligne2 = gi.LigneDeFeu('F2', 'Voiture', 3)
#ligne3 = gi.LigneDeFeu('P3', 'Pieton', 0)
#ligne4 = gi.LigneDeFeu('F4', 'Voiture', 3)
#ligne5 = gi.LigneDeFeu('B5', 'Voiture', 3)
#listeLignes = [ligne0, ligne1, ligne2, ligne3, ligne4, ligne5]
#
#phase0 = gi.Phase(0, [True, True, False, False, False, False], 12, 25, 60, False, False, False)
#phase1 = gi.Phase(1, [False, False, False, False, True, False], 6, 12, 25, True, False, False)
#phase2 = gi.Phase(2, [False, False, True, True, False, True], 10, 20, 45, False, True, False)
#listePhases = [phase0, phase1, phase2]
#
#matriceSecurite = [[0, 0, 2, 1, 1, 2],
#                   [0, 0, 7, 0, 8, 7],
#                   [2, 1, 0, 0, 2, 0],
#                   [8, 0, 0, 0, 7, 0],
#                   [0, 0, 8, 0, 0, 7],
#                   [2, 1, 0, 0, 2, 0]]
#                   
#                   
#                
## Exemplo 3
#ligne0 = gi.LigneDeFeu('F0', 'Voiture', 3)
#ligne1 = gi.LigneDeFeu('P1', 'Pieton', 0)
#ligne2 = gi.LigneDeFeu('F2', 'Voiture', 3)
#ligne3 = gi.LigneDeFeu('P3', 'Pieton', 0)
#ligne4 = gi.LigneDeFeu('B4', 'Voiture', 3)
#listeLignes = [ligne0, ligne1, ligne2, ligne3, ligne4]
#
#phase0 = gi.Phase(0, [True, True, False, False, False], 15, 40, np.inf, False, False)
#phase1 = gi.Phase(1, [False, False, False, True, True], 6, 6, 20, True, True)
#phase2 = gi.Phase(2, [False, False, True, True, False], 10, 18, 18, True, False)
#phase3 = gi.Phase(3, [False, True, False, False, True], 6, 6, 20, True, True)
#listePhases = [phase0, phase1, phase2, phase3]
#
#matriceSecurite = [[0, 0, 2, 1, 2],
#                   [0, 0, 8, 0, 0],
#                   [2, 1, 0, 0, 2],
#                   [8, 0, 0, 0, 6],
#                   [2, 0, 2, 2, 0]]
#
## Dossier 1
#listeLignes = [gi.LigneDeFeu('T1', 'Voiture', 3),   \
#               gi.LigneDeFeu('P8', 'Pieton', 0),    \
#               gi.LigneDeFeu('T2', 'Voiture', 3),   \
#               gi.LigneDeFeu('P13', 'Pieton', 0),   \
#               gi.LigneDeFeu('V3', 'Voiture', 3),   \
#               gi.LigneDeFeu('P9', 'Pieton', 0),    \
#               gi.LigneDeFeu('P12', 'Pieton', 0),   \
#               gi.LigneDeFeu('V5', 'Voiture', 3),   \
#               gi.LigneDeFeu('P7', 'Pieton', 0),    \
#               gi.LigneDeFeu('V6', 'Voiture', 3),   \
#               gi.LigneDeFeu('V4', 'Voiture', 3),   \
#               gi.LigneDeFeu('P11', 'Pieton', 0),   \
#               gi.LigneDeFeu('P10', 'Pieton', 0),   \
#               gi.LigneDeFeu('P14', 'Pieton', 0)]
#
#listePhases = [gi.Phase(0, [False, True, False, True, True, False, False, True, False, False, False, True, True, True], 6, 10, 10, False, False, False),\
#               gi.Phase(1, [False, True, False, True, True, False, False, False, False, False, False, True, True, True], 6, 19, 38, False, False, False),\
#               gi.Phase(2, [True, False, True, False, False, True, True, False, True, False, False, True, True, True], 3, 3, 20, True, True, True),\
#               gi.Phase(3, [False, False, False, False, False, True, True, False, True, True, False, False, False, False], 6, 6, 6, True, False, False),\
#               gi.Phase(4, [False, False, False, False, False, True, True, False, True, True, True, False, False, False], 8, 32, 64, False, False, False),\
#               gi.Phase(5, [True, False, True, False, False, True, True, False, True, False, False, True, True, True], 3, 3, 20, True, True, True)]
#
#matriceSecurite = [[0,1,0,8,6,0,0,6,0,6,6,0,0,0],   \
#                   [7,0,1,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,8,0,1,8,0,0,8,0,8,8,0,0,0],   \
#                   [1,0,7,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [3,0,3,0,0,1,8,0,0,7,7,0,0,0],   \
#                   [0,0,0,0,4,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,1,0,0,0,0,0,0,0,0,0],   \
#                   [3,0,3,0,0,0,0,0,3,1,1,0,0,0],   \
#                   [0,0,0,0,0,0,0,2,0,0,0,0,0,0],   \
#                   [6,0,6,0,2,0,0,6,0,0,0,1,0,8],   \
#                   [6,0,6,0,2,0,0,6,0,0,0,1,0,8],   \
#                   [0,0,0,0,0,0,0,0,0,12,12,0,0,0], \
#                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0],   \
#                   [0,0,0,0,0,0,0,0,0,1,1,0,0,0]]
