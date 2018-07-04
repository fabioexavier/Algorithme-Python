from numpy import max as npmax

# "Enums"

PHASE = 0 # Tipo de fase
INTERPHASE = 1

VOITURE = 0 # Tipo de linha
PIETON = 1

class Phase:
    def __init__(self, pNumber, pStatusLignes, pDuration):
        self.number = pNumber
        self.statusLignes = pStatusLignes
        self.duration = pDuration
        self.kind = PHASE
        
class Interphase:
    def __init__(self, pOrigin, pDestination, pChangeTime, pDuration):
        self.originPhase = pOrigin
        self.destinationPhase = pDestination
        self.number = (pOrigin, pDestination)
        self.changeTime = pChangeTime
        self.duration = pDuration
        self.kind = INTERPHASE
        
class LigneDeFeu:
    def __init__(self, pName, pType, pYellow):
        self.name = pName
        self.type = pType
        self.yellowTime = pYellow
        self.yellowCounter = 0
        self.output = 'Vermelho'
        
    def changeOutput(self):
        if (self.output == 'Verde'):
            if (self.type == VOITURE):
                self.output = 'Amarelo'
            elif (self.type == PIETON):
                self.output = 'Vermelho'
        elif (self.output == 'Vermelho'):
            self.output = 'Verde'    

    def processYellow(self):
        if (self.yellowCounter == self.yellowTime):
            self.output = 'Vermelho'
            self.yellowCounter = 0
        else:
            self.yellowCounter += 1

class Carrefour:
    def __init__(self):
        
        # Dados
#        ligne0 = LigneDeFeu('F0', VOITURE, 3)
#        ligne1 = LigneDeFeu('F1', VOITURE, 3)
#        ligne2 = LigneDeFeu('P2', PIETON, 0)
#        self.listLignes = [ligne0, ligne1, ligne2]
#        
#        phase0 = Phase(0, [True, False, False], 8)
#        phase1 = Phase(1, [False, True, True], 8)
#        self.listPhases = [phase0, phase1]
#        
#        self.matrizSeguranca = [[0, 2, 3],[2, 0, 0],[6, 0, 0]]
        ligne0 = LigneDeFeu('F0', VOITURE, 3)
        ligne1 = LigneDeFeu('P1', PIETON, 0)
        ligne2 = LigneDeFeu('F2', VOITURE, 3)
        ligne3 = LigneDeFeu('F3', VOITURE, 3)
        ligne4 = LigneDeFeu('P4', PIETON, 0)
        ligne5 = LigneDeFeu('F5', VOITURE, 3)
        self.listLignes = [ligne0, ligne1, ligne2, ligne3, ligne4, ligne5]
        
        phase0 = Phase(0, [True, False, False, True, True, False], 8)
        phase1 = Phase(1, [False, True, True, False, False, False], 8)
        phase2 = Phase(2, [False, False, False, False, False, True], 8)
        
        self.listPhases = [phase0, phase1, phase2]
        
        self.matrizSeguranca = [[0, 1, 2, 0, 0, 1],[8, 0, 0, 6, 0, 8],[2, 0, 0, 1, 2, 1],[0, 2, 3, 0, 0, 0],[0, 0, 8, 0, 0, 7],[1, 1, 2, 0, 3, 0]]
        
        
        # Inicialização
        self.matrixInterphase = self.generateInterphases()
        self.currentPhase = self.listPhases[0]
        self.currentTime = -1 # Para que seja 0 no primeiro ciclo da execuçao
    
    def calcInterphase(self,phase1,phase2):

        # Ver quais linhas abrem e quais fecham   
        fechar = []
        abrir = []
        
        for i in range(len(self.listLignes)):
            if ((phase1.statusLignes[i] == True) and  (phase2.statusLignes[i] == False)):
                fechar.append(i)
            elif ((phase1.statusLignes[i] == False) and  (phase2.statusLignes[i] == True)):
                abrir.append(i)
                
        # Calcuar matriz especifica
        matriz = [[None for i in abrir] for j in fechar]
        for i,x in enumerate(fechar):
            for j,y in enumerate(abrir):
                # Slice da matriz de segurança nas linhas que fecham e colunas que abrem
                matriz[i][j] = self.matrizSeguranca[x][y] 
        
                # Adiciona tempo de amarelo pras linhas de carro que fecham
                if (self.listLignes[x].type == VOITURE): 
                    matriz[i][j] += self.listLignes[x].yellowTime
                 
            
        duration = npmax(matriz) # A duração da interfase é o maior dos valores dessa matriz
        
        # Inicialização do vetor com 0 para as linhas que fecham e 'duration' pras linhas que abrem (e None pras que não são envolvidas)
        changeTime = [None for i in self.listLignes]
        
        for i,ligne in enumerate(self.listLignes): 
            if i in fechar:
                changeTime[i] = 0
            elif i in abrir:
                changeTime[i] = duration
                
        # Calcular todos os tempos otimizados 
        for ligne in range(len(self.listLignes)):
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
    
        return Interphase(phase1.number, phase2.number, changeTime, duration)
    
    def generateInterphases(self):
        matrixInterphases = [[None for i in self.listPhases] for j in self.listPhases]
        for i, pi in enumerate(self.listPhases):
            for j, pj in enumerate(self.listPhases):
                if (i != j):
                    matrixInterphases[i][j] = self.calcInterphase(pi,pj)
        return matrixInterphases
        
    
    def update(self):
        self.currentTime += 1
            
        if (self.currentTime == self.currentPhase.duration): # Se chegou no fim da fase
            
            if (self.currentPhase.kind == PHASE):
                nextPhaseNumber = self.currentPhase.number + 1
                if (nextPhaseNumber == len(self.listPhases)):
                    nextPhaseNumber = 0
                
                self.currentPhase = self.matrixInterphase[self.currentPhase.number][nextPhaseNumber]
                
            elif (self.currentPhase.kind == INTERPHASE):
                nextPhaseNumber = self.currentPhase.destinationPhase
                self.currentPhase = self.listPhases[nextPhaseNumber]
                
            self.currentTime = 0
        
        self.updateOutputLignes()

    def updateOutputLignes(self):
        if (self.currentPhase.kind == PHASE):
            for i, ligne in enumerate(self.listLignes):
                if (self.currentPhase.statusLignes[i] == True):
                    ligne.output = 'Verde'
                else:
                    ligne.output = 'Vermelho'
            
        elif (self.currentPhase.kind == INTERPHASE):
            for i, ligne in enumerate(self.listLignes):
                if (self.currentTime == self.currentPhase.changeTime[i]):
                    ligne.changeOutput()
                if (ligne.output == 'Amarelo'):
                    ligne.processYellow()
 
        
    def output(self):
        print('\033[H\033[J') # clears screen
        
        print('Time:', self.currentTime)
        print('Phase:', self.currentPhase.number, end='\n\n')
        
        for ligne in self.listLignes:
            print(ligne.name, ligne.output)
        
    