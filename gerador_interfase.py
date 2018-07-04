# Dados

from numpy import max as npmax

VOITURE = 0 # Tipo de linha
PIETON = 1

class LigneDeFeu:
    def __init__(self, pName, pType, pYellow):
        self.name = pName
        self.type = pType
        self.yellowTime = pYellow
        self.yellowCounter = 0
        self.output = 'Vermelho'

class Phase:
    def __init__(self, pNumber, pStatusLignes, pDuration):
        self.number = pNumber
        self.statusLignes = pStatusLignes
        self.duration = pDuration


ligne0 = LigneDeFeu('F0', VOITURE, 3)
ligne1 = LigneDeFeu('P1', PIETON, 0)
ligne2 = LigneDeFeu('F2', VOITURE, 3)
ligne3 = LigneDeFeu('F3', VOITURE, 3)
ligne4 = LigneDeFeu('P4', PIETON, 0)
ligne5 = LigneDeFeu('F5', VOITURE, 3)
listLignes = [ligne0, ligne1, ligne2, ligne3, ligne4, ligne5]

phase0 = Phase(0, [True, False, False, True, True, False], 8)
phase1 = Phase(1, [False, True, True, False, False, False], 8)
phase2 = Phase(2, [False, False, False, False, False, True], 8)

phase = [phase0, phase1, phase2]

matrizSeguranca = [[0, 1, 2, 0, 0, 1],[8, 0, 0, 6, 0, 8],[2, 0, 0, 1, 2, 1],[0, 2, 3, 0, 0, 0],[0, 0, 8, 0, 0, 7],[1, 1, 2, 0, 3, 0]]



def calcInterphase(p1,p2):

    # i) Ver quais linhas abrem e quais fecham
    
    fechar = []
    abrir = []
    
    for i in range(len(listLignes)):
        if ((phase[p1].statusLignes[i] == True) and  (phase[p2].statusLignes[i] == False)):
            fechar.append(i)
        elif ((phase[p1].statusLignes[i] == False) and  (phase[p2].statusLignes[i] == True)):
            abrir.append(i)
            
    # ii) Calcuar matriz especifica
    
    matriz = [[None for i in abrir] for j in fechar]
    for i,x in enumerate(fechar):
        for j,y in enumerate(abrir):
            # Slice da matriz de segurança nas linhas que fecham e colunas que abrem
            matriz[i][j] = matrizSeguranca[x][y] 
    
            # Adiciona tempo de amarelo pras linhas de carro que fecham
            if (listLignes[x].type == VOITURE): 
                matriz[i][j] += listLignes[x].yellowTime
             
        
    duration = npmax(matriz) # A duração da interfase é o maior dos valores dessa matriz
    
    # iii) Calcular tempos base change times
    
    changeTime = [None for i in listLignes]
    
    # Inicialização do vetor com 0 para as linhas que fecham e 'duration' pras linhas que abrem (e None pras que não são envolvidas)
    for i,ligne in enumerate(listLignes): 
        if i in fechar:
            changeTime[i] = 0
        elif i in abrir:
            changeTime[i] = duration
            
    # iv) Iterar até calcular todos os tempos otimizados 
           
    for ligne in range(len(listLignes)):
        if (ligne in fechar):
            i = fechar.index(ligne)
            temp = [None]*len(abrir)
            
            for j,y in enumerate(abrir):
                temp[j] = changeTime[y] - matriz[i][j]
            
            changeTime[ligne] = min(temp)
            
        elif (ligne in abrir):
            j = abrir.index(ligne)
            temp = [None]*len(fechar)
            
            for i,x in enumerate(fechar):
                temp[i] = changeTime[x] + matriz[i][j]
            
            changeTime[ligne] = max(temp)

    return changeTime









        
        