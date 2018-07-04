import numpy as np
import priorite as pri

def suivant(element, liste):
    index = liste.index(element) + 1
    if index == len(liste):
        index = 0
    return liste[index]

class Phase:
    dureeBus = 3
    dureeMaxBus = 10
    
    def __init__(self, pNumero, pLignesActives, pMin, pNom, pMax, pEscamotable, pPrioritaire):
        self.numero = pNumero
        self.lignesActives = pLignesActives
        
        self.dureeMinimale = pMin # Ne change jamais
        self.dureeNominale = pNom # Ne change jamais
        self.dureeMaximale = pMax # Ne change jamais
        self.duree = self.dureeNominale # Peut varier au cours de l'execution
        
        self.escamotable = pEscamotable
        self.solicitee = not pEscamotable # pas solicitee ssi la phase est escamotable
        self.prioritaire = pPrioritaire
        self.type = 'Phase'
    
    
    def __str__(self):
        return 'Phase '+str(self.numero)            
    __repr__ = __str__

class Interphase:
    def __init__(self, pOrigine, pDestination, pTempsChangement, pDuree):
        self.phaseOrigine = pOrigine
        self.phaseDestination = pDestination
        self.tempsChangement = pTempsChangement
        self.duree = pDuree
        self.type = 'Interphase'
        
    def __str__(self):
        return 'Interphase '+str((self.phaseOrigine, self.phaseDestination))        
    __repr__ = __str__

class LigneDeFeu:
    def __init__(self, pNom, pType, pTempsJaune):
        self.nom = pNom
        self.type = pType
        self.tempsJaune = pTempsJaune
        self.compteurJaune = 0
        self.couleur = 'red'
        
    def changerCouleur(self):
        if (self.couleur == 'green'):
            if (self.type == 'Voiture'):
                self.couleur = 'yellow'
            elif (self.type == 'Pieton'):
                self.couleur = 'red'
        elif (self.couleur == 'red'):
            self.couleur = 'green'    

    def traiterJaune(self):
        if (self.compteurJaune == self.tempsJaune):
            self.couleur = 'red'
            self.compteurJaune = 0
        else:
            self.compteurJaune += 1

class Carrefour:
    def __init__(self, pListeLignes, pListePhases, pMatriceSecurite):
        self.listeLignes = pListeLignes
        self.listePhases = pListePhases
        self.matriceSecurite = pMatriceSecurite      
        
        # Inicialização
        self.matriceGraphe = self.calcGraphe()
        self.matriceInterphase = self.genererInterphases()
        self.cycleBase = [phase for phase in self.listePhases if phase.solicitee]
        self.plan = self.cycleBase
        
        self.phaseActuelle = self.plan[0]
        self.tempsPhase = 0
        
        self.modePriorite = False
        self.delaiApproche = -1
    
    def calcGraphe(self):
        matrice = np.zeros((len(self.listePhases),len(self.listePhases)))
        
        for phaseActuelle in self.listePhases:
            phaseSuivante = suivant(phaseActuelle, self.listePhases)
            matrice[phaseActuelle.numero][phaseSuivante.numero] = 1
            
            if not (phaseActuelle.escamotable and phaseActuelle.prioritaire):
                while phaseSuivante.escamotable and suivant(phaseSuivante, self.listePhases) != phaseActuelle:
                    phaseSuivante = suivant(phaseSuivante, self.listePhases)
                    matrice[phaseActuelle.numero][phaseSuivante.numero] = 1
                    
        return matrice
    
    def genererInterphases(self):
        matriceInterphases = [[None for i in self.listePhases] for j in self.listePhases]
        for i, pi in enumerate(self.listePhases):
            for j, pj in enumerate(self.listePhases):
                if (i != j):
                    matriceInterphases[i][j] = self.calcInterphase(pi,pj)
        return matriceInterphases
    
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
                 
            
        duree = np.max(matriceReduite) # A duração da interfase é o maior dos valores dessa matriz
        
        # Inicialização do vetor com 0 para as linhas que fecham e 'duree' pras linhas que abrem (e None pras que não são envolvidas)
        tempsChangement = [None for i in self.listeLignes]
        
        for i,ligne in enumerate(self.listeLignes): 
            if i in fermer:
                tempsChangement[i] = 0
            elif i in ouvrir:
                tempsChangement[i] = duree
                
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
    
        return Interphase(phase1, phase2, tempsChangement, duree)
    
    def update(self):
        ## Update do plano
        self.cycleBase = [phase for phase in self.listePhases if phase.solicitee]
        
        if self.delaiApproche >= 0:
            self.modePriorite = True
            self.plan = self.planPriorite()
        
        if not self.modePriorite:
            self.plan = self.planStandard()
        
        transition = False
        if self.tempsPhase >= self.phaseActuelle.duree: # Se chegou no fim da fase/interfase
            transition = self.transition() # Falso se passar de uma fase pra ela mesma
            
        self.updateCouleurs()
        
         # Atualiza contadores
        self.tempsPhase += 1
        if self.delaiApproche >= 0:
            self.delaiApproche -= 1
        
        return ([ligne for ligne in self.listeLignes], transition)
    
    def transition(self):
        if (self.phaseActuelle.type == 'Phase'):
            if self.phaseActuelle.escamotable:
                self.phaseActuelle.solicitee = False # Reset de la solicitation
            
            if self.delaiApproche < 0 and self.phaseActuelle.prioritaire:
                self.modePriorite = False
                self.plan = self.planStandard()
            
            if self.phaseActuelle in self.plan:
                prochainePhase = suivant(self.phaseActuelle, self.plan)
            elif self.phaseActuelle in self.cycleBase:
                prochainePhase = suivant(self.phaseActuelle, self.cycleBase)
            else:
                prochainePhase = suivant(self.phaseActuelle, self.listePhases)
            
            if self.phaseActuelle == prochainePhase:
                return False
            
            self.phaseActuelle = self.matriceInterphase[self.phaseActuelle.numero][prochainePhase.numero]   
                
        elif (self.phaseActuelle.type == 'Interphase'):
            self.phaseActuelle = self.phaseActuelle.phaseDestination
        
        self.tempsPhase = 0
        
        return True
        
    
    def updateCouleurs(self):
        if (self.phaseActuelle.type == 'Phase'):
            for i, ligne in enumerate(self.listeLignes):
                if (self.phaseActuelle.lignesActives[i] == True):
                    ligne.couleur = 'green'
                else:
                    ligne.couleur = 'red'
            
        elif (self.phaseActuelle.type == 'Interphase'):
            for i, ligne in enumerate(self.listeLignes):
                if (self.tempsPhase == self.phaseActuelle.tempsChangement[i]):
                    ligne.changerCouleur()
                if (ligne.couleur == 'yellow'):
                    ligne.traiterJaune()
    
    def planStandard(self):
        for phase in self.listePhases:
            phase.duree = phase.dureeNominale
        return self.cycleBase
    
    def planPriorite(self):
        chemin = pri.meilleurChemin(self)
        durees = chemin.dureesIdeales(self.delaiApproche)
        plan = chemin.getPlan(durees)
        
        print('Bus arrive en', self.delaiApproche)
        print(chemin)
        print(durees, end='\n\n')
        
        return plan
        
    def soliciterPhase(self,n):
        self.listePhases[n].solicitee = True
    
    def nomLignes(self):
        return [ligne.nom for ligne in self.listeLignes]
    
    
