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
    def __init__(self, pOrigin, pDestination, pChangeTime):
        self.originPhase = pOrigin
        self.destinationPhase = pDestination
        self.number = (pOrigin, pDestination)
        self.changeTime = pChangeTime
        self.duration = max(self.changeTime)
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
        
        ligne0 = LigneDeFeu('F0', VOITURE, 3)
        ligne1 = LigneDeFeu('F1', VOITURE, 3)
        ligne2 = LigneDeFeu('P2', PIETON, 0)
        self.listLignes = [ligne0, ligne1, ligne2]
        
        phase0 = Phase(0, [True, False, False], 8)
        phase1 = Phase(1, [False, True, True], 8)
        self.listPhases = [phase0, phase1]
        
        interphase01 = Interphase(0, 1, [0, 5, 6])
        interphase10 = Interphase(1, 0, [6, 1, 0])
        self.matrixInterphase = [[None, interphase01],[interphase10, None]]
        
        self.currentPhase = self.listPhases[0]
        self.currentTime = -1 # Para que seja 0 no primeiro ciclo da execuçao
        
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
        
    