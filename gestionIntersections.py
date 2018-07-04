from numpy import max as npmax

class Phase:
    def __init__(self, pNumero, pLignesActives, pDuration):
        self.numero = pNumero
        self.lignesActives = pLignesActives
        self.duration = pDuration
        self.type = 'Phase'
        
class Interphase:
    def __init__(self, pOrigine, pDestination, pTempsChangement, pDuration):
        self.phaseOrigine = pOrigine
        self.phaseDestination = pDestination
        self.numero = (pOrigine, pDestination)
        self.tempsChangement = pTempsChangement
        self.duration = pDuration
        self.type = 'Interphase'

class LigneDeFeu:
    def __init__(self, pNom, pType, pTempsJaune):
        self.nom = pNom
        self.type = pType
        self.tempsJaune = pTempsJaune
        self.compteurJaune = 0
        self.couleur = 'Rouge'
        
    def changerCouleur(self):
        if (self.couleur == 'Vert'):
            if (self.type == 'Voiture'):
                self.couleur = 'Jaune'
            elif (self.type == 'Pieton'):
                self.couleur = 'Rouge'
        elif (self.couleur == 'Rouge'):
            self.couleur = 'Vert'    

    def traiterJaune(self):
        if (self.compteurJaune == self.tempsJaune):
            self.couleur = 'Rouge'
            self.compteurJaune = 0
        else:
            self.compteurJaune += 1

class Carrefour:
    def __init__(self, pListeLignes, pListePhases, pMatriceSecurite):
        self.listeLignes = pListeLignes
        self.listePhases = pListePhases
        self.matriceSecurite = pMatriceSecurite      
        
        # Inicialização
        self.matriceInterphase = self.genererInterphases()
        self.phaseActuelle = self.listePhases[0]
        self.tempsPhase = -1 # Para que seja 0 no primeiro ciclo da execuçao
    
    def calcInterphase(self,phase1,phase2):

        # Ver quais linhas abrem e quais fecham   
        fermer = []
        ouvrir = []
        
        for i in range(len(self.listeLignes)):
            if ((phase1.lignesActives[i] == True) and  (phase2.lignesActives[i] == False)):
                fermer.append(i)
            elif ((phase1.lignesActives[i] == False) and  (phase2.lignesActives[i] == True)):
                ouvrir.append(i)
                
        # Calcuar matriz especifica
        matriceReduite = [[None for i in ouvrir] for j in fermer]
        for i,x in enumerate(fermer):
            for j,y in enumerate(ouvrir):
                # Slice da matriz de segurança nas linhas que fecham e colunas que abrem
                matriceReduite[i][j] = self.matriceSecurite[x][y] 
        
                # Adiciona tempo de amarelo pras linhas de carro que fecham
                if (self.listeLignes[x].type == 'Voiture'): 
                    matriceReduite[i][j] += self.listeLignes[x].tempsJaune
                 
            
        duration = npmax(matriceReduite) # A duração da interfase é o maior dos valores dessa matriz
        
        # Inicialização do vetor com 0 para as linhas que fecham e 'duration' pras linhas que abrem (e None pras que não são envolvidas)
        tempsChangement = [None for i in self.listeLignes]
        
        for i,ligne in enumerate(self.listeLignes): 
            if i in fermer:
                tempsChangement[i] = 0
            elif i in ouvrir:
                tempsChangement[i] = duration
                
        # Calcular todos os tempos otimizados 
        for ligne in range(len(self.listeLignes)):
            if (ligne in fermer):
                i = fermer.index(ligne)
                temp = [None]*len(ouvrir)
                
                for j,y in enumerate(ouvrir):
                    temp[j] = tempsChangement[y] - matriceReduite[i][j]
                
                tempsChangement[ligne] = min(temp)
                
            elif (ligne in ouvrir):
                j = ouvrir.index(ligne)
                temp = [None]*len(fermer)
                
                for i,x in enumerate(fermer):
                    temp[i] = tempsChangement[x] + matriceReduite[i][j]
                
                tempsChangement[ligne] = max(temp)
    
        return Interphase(phase1.numero, phase2.numero, tempsChangement, duration)
    
    def genererInterphases(self):
        matriceInterphases = [[None for i in self.listePhases] for j in self.listePhases]
        for i, pi in enumerate(self.listePhases):
            for j, pj in enumerate(self.listePhases):
                if (i != j):
                    matriceInterphases[i][j] = self.calcInterphase(pi,pj)
        return matriceInterphases
        
    
    def update(self):
        ## Sequencia de fases
        self.tempsPhase += 1
            
        if (self.tempsPhase == self.phaseActuelle.duration): # Se chegou no fim da fase
            
            if (self.phaseActuelle.type == 'Phase'):
                numeroProchainePhase = self.phaseActuelle.numero + 1
                if (numeroProchainePhase == len(self.listePhases)):
                    numeroProchainePhase = 0
                
                self.phaseActuelle = self.matriceInterphase[self.phaseActuelle.numero][numeroProchainePhase]
                
            elif (self.phaseActuelle.type == 'Interphase'):
                numeroProchainePhase = self.phaseActuelle.phaseDestination
                self.phaseActuelle = self.listePhases[numeroProchainePhase]
                
            self.tempsPhase = 0
        
        ## Update cores
        if (self.phaseActuelle.type == 'Phase'):
            for i, ligne in enumerate(self.listeLignes):
                if (self.phaseActuelle.lignesActives[i] == True):
                    ligne.couleur = 'Vert'
                else:
                    ligne.couleur = 'Rouge'
            
        elif (self.phaseActuelle.type == 'Interphase'):
            for i, ligne in enumerate(self.listeLignes):
                if (self.tempsPhase == self.phaseActuelle.tempsChangement[i]):
                    ligne.changerCouleur()
                if (ligne.couleur == 'Jaune'):
                    ligne.traiterJaune()
 
        
    def output(self):
        print('\033[H\033[J') # clears screen
        
        print('Time:', self.tempsPhase)
        print('Phase:', self.phaseActuelle.numero, end='\n\n')
        
        for ligne in self.listeLignes:
            print(ligne.nom, ligne.couleur)
        
    