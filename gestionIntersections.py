import numpy as np
import priorite as pri

def suivant(element, liste):
    index = liste.index(element) + 1
    if index == len(liste):
        index = 0
    return liste[index]

class Phase:
    dureeBus = 3
    dureeMaxBus = 6
    
    def __init__(self, pNumero, pLignesActives, pMin, pNom, pMax, pEscamotable, pPrioritaire, pExclusive):
        self.numero = pNumero
        self.lignesActives = pLignesActives
        
        self.dureeMinimale = pMin # Ne change jamais
        self.dureeNominale = pNom # Ne change jamais
        self.dureeMaximale = pMax # Ne change jamais
        self.duree = self.dureeNominale # Peut varier au cours de l'execution
        
        self.escamotable = pEscamotable
        self.solicitee = not pEscamotable # pas solicitee ssi la phase est escamotable
        self.prioritaire = pPrioritaire
        self.exclusive = pExclusive
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
    def __init__(self, pNumero, pNom, pType, pTempsJaune, pPrioritaire):
        self.numero = pNumero
        self.nom = pNom
        self.type = pType
        self.tempsJaune = pTempsJaune
        self.compteurJaune = 0
        self.prioritaire = pPrioritaire
        
        self.compteurRouge = 0
        self.phasesAssociees = [] # Fases escamotaveis ligadas a essa linha
        self.solicitee = not self.prioritaire # Linhas prioritarias inicializam nao solicitadas (falta desativar solicitacao das linhas escamotaveis)
        
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

    def __str__(self):
        return self.nom

class Carrefour:
    def __init__(self, pListeLignes, pListePhases, pMatriceSecurite):
        self.listeLignes = pListeLignes
        self.listePhases = pListePhases
        self.matriceSecurite = np.array(pMatriceSecurite)
        
        # Identificaçao das linhas escamotaveis (dentre as nao prioritarias)
        for ligne in self.listeLignes:
            if not ligne.prioritaire:
                phases = [phase for phase in self.listePhases if phase.lignesActives[ligne.numero] == True]
                if all(phase.escamotable for phase in phases):
                    ligne.phasesAssociees = [phase for phase in phases if not phase.prioritaire]
                    ligne.solicitee = False
#                    print(ligne.nom, ligne.phasesAssociees)
                
        self.matriceGraphe = self.calcGraphe()
        self.matriceInterphase = self.genererInterphases()
        self.cycleBase = [phase for phase in self.listePhases if phase.solicitee]
        self.plan = self.cycleBase
        
        self.phaseActuelle = self.plan[0]
        self.tempsPhase = 0
        
        self.codesPriorite = {phase.prioritaire for phase in pListePhases if phase.prioritaire != 0}
        self.modePriorite = False
        self.delaiApproche = -1
        
    def calcGraphe(self):
        matrice = np.zeros((len(self.listePhases),len(self.listePhases)))
        
        for phaseActuelle in self.listePhases:
            phaseSuivante = suivant(phaseActuelle, self.listePhases)
            matrice[phaseActuelle.numero][phaseSuivante.numero] = 1
            
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
        
        for ligne in self.listeLignes:
            if phase1.lignesActives[ligne.numero] and not phase2.lignesActives[ligne.numero]:
                fermer.append(ligne)
            elif not phase1.lignesActives[ligne.numero] and phase2.lignesActives[ligne.numero]:
                ouvrir.append(ligne)
        
        # Se nenhuma fechar, nao existe interfase
        if not fermer:
            return Interphase(phase1, phase2, [None for i in self.listeLignes], 0)
        
        # Se alguma fechar mas nenuma abrir, fazer a interfase apenas para dar os amarelos
        if not ouvrir:
            duree = max([ligne.tempsJaune for ligne in self.listeLignes if ligne in fermer])
            tempsChangement = [0 if ligne in fermer else None for ligne in self.listeLignes]
            return Interphase(phase1, phase2, tempsChangement, duree)
        
        
        # Calcular matriz especifica
        indexesOuvrir = [ligne.numero for ligne in ouvrir]
        indexesFermer = [ligne.numero for ligne in fermer]
        matriceReduite = self.matriceSecurite.copy()[indexesFermer,:][:,indexesOuvrir]
        for i,ligne in enumerate(fermer):
            matriceReduite[i,:] += ligne.tempsJaune
        
        duree = np.max(matriceReduite) # A duração da interfase é o maior dos valores dessa matriz
        
        # Calculo dos instantes em que as linhas abrem/fecham
        tempsChangement = [None for i in self.listeLignes]
        
        for j,ligneO in enumerate(ouvrir):
            tempsChangement[ligneO.numero] = max(matriceReduite[:,j])
        
        for i,ligneF in enumerate(fermer):
            tempsChangement[ligneF.numero] = min([tempsChangement[ligneO.numero] - matriceReduite[i,j] for j,ligneO in enumerate(ouvrir)])
        
        return Interphase(phase1, phase2, tempsChangement, duree)
    
    def update(self):
        ## Update do plano
        self.cycleBase = [phase for phase in self.listePhases if phase.solicitee]
        
        self.updateLignesSolicitees()
        
        if self.delaiApproche >= 0:
            self.modePriorite = True
            self.plan = self.planPriorite()
        
        if not self.modePriorite:
            self.plan = self.planStandard()
        
        transition = False
        if self.tempsPhase >= self.phaseActuelle.duree: # Se chegou no fim da fase/interfase
            transition = self.transition() # Falso se passar de uma fase pra ela mesma
            
        self.updateCouleurs()
        self.updateCompteursRouge()
        
         # Atualiza contadores
        self.tempsPhase += 1
        if self.delaiApproche >= 0:
            self.delaiApproche -= 1
        
        return ([ligne for ligne in self.listeLignes], transition)
    
    def updateLignesSolicitees(self):
        for ligne in self.listeLignes:
            if ligne.phasesAssociees: # Se a linha for escamotavel
                ligne.solicitee = any(phase.solicitee for phase in ligne.phasesAssociees)
                
            elif ligne.prioritaire:
                if self.delaiApproche == 0:
                    ligne.solicitee = True
                elif ligne.couleur == 'green':
                    ligne.solicitee = False  
    
    def transition(self):
        if (self.phaseActuelle.type == 'Phase'):
            if self.phaseActuelle.escamotable:
                self.phaseActuelle.solicitee = False # Reset de la solicitation
            
            if self.delaiApproche < 0 and self.phaseActuelle.prioritaire:
                self.modePriorite = False
                self.plan = self.planStandard()
            
            if self.phaseActuelle in self.plan:
                prochainePhase = suivant(self.phaseActuelle, self.plan)
            else:
                prochainePhase = suivant(self.phaseActuelle, self.listePhases)
                while not prochainePhase.solicitee:
                    prochainePhase = suivant(prochainePhase, self.listePhases)
            
            if self.phaseActuelle == prochainePhase:
                return False
            
            self.phaseActuelle = self.matriceInterphase[self.phaseActuelle.numero][prochainePhase.numero]   
            if self.phaseActuelle.duree == 0:
                self.phaseActuelle = self.phaseActuelle.phaseDestination
            
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
                    ligne.compteurJaune = 0
            
        elif (self.phaseActuelle.type == 'Interphase'):
            for i, ligne in enumerate(self.listeLignes):
                if (self.tempsPhase == self.phaseActuelle.tempsChangement[i]):
                    ligne.changerCouleur()
                if (ligne.couleur == 'yellow'):
                    ligne.traiterJaune()
    
    def updateCompteursRouge(self):
        for ligne in self.listeLignes:
#            if ligne.phasesAssociees: # Se a linha for escamotavel
#                ligne.solicitee = any(phase.solicitee for phase in ligne.phasesAssociees)
#                
#            elif ligne.prioritaire:
#                if self.delaiApproche == 0:
#                    ligne.solicitee = True
#                elif ligne.couleur == 'green':
#                    ligne.solicitee = False            
            
            if ligne.couleur == 'red' and ligne.solicitee:
                ligne.compteurRouge += 1
                
            elif ligne.couleur == 'green':
                ligne.compteurRouge = 0
    
    def planStandard(self):
        for phase in self.listePhases:
            phase.duree = phase.dureeNominale
        return self.cycleBase
    
    def planPriorite(self):
        print('Bus arrive dans', self.delaiApproche, end='\n\n')
        chemin = pri.meilleurChemin(self)
        plan = chemin.getPlan()
        
        print('Chemin choisi')
        print(chemin)
        print('\n')
        
        return plan
        
    def soliciterPhase(self,n):
        self.listePhases[n].solicitee = True
    
    def nomLignes(self):
        return [ligne.nom for ligne in self.listeLignes]
    
    
