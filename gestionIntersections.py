import numpy as np

def suivant(element, liste):
    index = liste.index(element) + 1
    if index == len(liste):
        index = 0
    return liste[index]

class Phase:   
    def __init__(self, pNumero, pLignesActives, pMin, pNom, pMax, pEscamotable, pCodePriorite, pExclusive, pDureeBus):
        self.numero = pNumero
        self.lignesActives = pLignesActives
        
        self.dureeMinimale = pMin
        self.dureeNominale = pNom
        self.dureeMaximale = pMax
        self.duree = self.dureeNominale # Varia ao longo da execuçao
        
        self.escamotable = pEscamotable
        self.solicitee = not pEscamotable # Inicializa todas as fases escamotaveis como nao solicitadas
        self.codePriorite = pCodePriorite
        self.exclusive = pExclusive
        self.dureeBus = pDureeBus
        
        self.type = 'phase'
    
    def __str__(self):
        return 'Phase '+str(self.numero)            
    __repr__ = __str__

class Interphase:
    def __init__(self, pOrigine, pDestination, pTempsChangement, pDuree):
        self.phaseOrigine = pOrigine
        self.phaseDestination = pDestination
        self.tempsChangement = pTempsChangement
        self.duree = pDuree
        self.type = 'interphase'
        
    def __str__(self):
        return 'Interphase '+str((self.phaseOrigine, self.phaseDestination))        
    __repr__ = __str__

class LigneDeFeu:
    def __init__(self, pNumero, pNom, pType, pTempsJaune, pCodePriorite):
        self.numero = pNumero
        self.nom = pNom
        self.type = pType
        self.tempsJaune = pTempsJaune
        self.codePriorite = pCodePriorite
        
        self.compteurJaune = 0
        self.compteurRouge = 0
        self.phasesAssociees = [] # Fases escamotaveis ligadas a essa linha
        self.solicitee = not self.codePriorite # Linhas prioritarias inicializam nao solicitadas
        # Falta desativar solicitacao das linhas escamotaveis, o que é feito no construtor de Carrefour pq é necessario conhecer as fases escamotaveis
        
        self.couleur = 'red'
        
    def __str__(self):
        return self.nom

class DemandePriorite:
    def __init__(self, pDelaiApproche, pCodePriorite, pCodeVehicule):
        self.delaiApproche = pDelaiApproche
        self.codePriorite = pCodePriorite
        self.codeVehicule = pCodeVehicule

class Carrefour:
    def __init__(self, pListeLignes, pListePhases, pMatriceSecurite):
        self.listeLignes = pListeLignes
        self.listePhases = pListePhases
        self.matriceSecurite = np.array(pMatriceSecurite)
        
        # Identificaçao das linhas escamotaveis (dentre as nao prioritarias)
        for ligne in self.listeLignes:
            if not ligne.codePriorite:
                phases = [phase for phase in self.listePhases if phase.lignesActives[ligne.numero] == True]
                if all(phase.escamotable for phase in phases):
                    ligne.phasesAssociees = [phase for phase in phases if not phase.codePriorite]
                    ligne.solicitee = False
                
        self.matriceGraphe = self.calcGraphe()
        self.matriceInterphase = self.genererInterphases()
        
        # Decide a fase inicial
        for phase in self.listePhases:
            self.phaseActuelle = phase
            if not self.phaseActuelle.escamotable:
                break
        self.tempsPhase = 0
        
        self.transition = False # Indica se fez uma transicao no segundo atual
        
        # Variaveis de prioridade
        self.codesPriorite = {phase.codePriorite for phase in pListePhases}
        self.modePriorite = False
        self.demandesPriorite = []
        
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
        # Atualiza quais linhas foram solicitadas
        for ligne in self.listeLignes:
            # Se a linha for escamotavel
            if ligne.phasesAssociees: 
                ligne.solicitee = any(phase.solicitee for phase in ligne.phasesAssociees)
                
            # Se a linha for prioritaria
            elif ligne.codePriorite:
                # Linha solicitada se existir algum veiculo com o mesmo codigo esperando
                demandesEnAttente = [demande for demande in self.demandesPriorite if demande.delaiApproche <= 0 and demande.codePriorite == ligne.codePriorite]
                if demandesEnAttente:
                    ligne.solicitee = True
                # Linha deixa de ser solicitada quando abrir
                elif ligne.couleur == 'green':
                    ligne.solicitee = False 
        
        # Modo prioritario sse houver alguma demanda
        self.modePriorite = True if self.demandesPriorite else False
        
        # Transicao de fases
        self.transition = False
        
        # Decide a duracao da fase atual e qual sera a proxima fase
        if self.modePriorite:
            pass
        else:
            if self.phaseActuelle.type == 'phase':
                self.phaseActuelle.duree = self.phaseActuelle.dureeNominale
                
                # Avança na lista de fases ate achar uma fase solicitada
                self.phaseProchaine = suivant(self.phaseActuelle, self.listePhases)
                while not self.phaseProchaine.solicitee:
                    self.phaseProchaine = suivant(self.phaseProchaine, self.listePhases)
        
        # Se chegou no fim da fase
        if self.tempsPhase >= self.phaseActuelle.duree: # Se chegou no fim da fase/interfase
            if self.phaseActuelle.type == 'phase':
                # Reset da solicitaçao se a fase for escamotavel
                if self.phaseActuelle.escamotable:
                    self.phaseActuelle.solicitee = False
                
                # Troca de fase
                if self.phaseProchaine != self.phaseActuelle:
                    self.phaseActuelle = self.interphase(self.phaseActuelle, self.phaseProchaine)
                    self.tempsPhase = 0
                    self.transition = True
                    
            elif self.phaseActuelle.type == 'interphase':
                self.phaseActuelle = self.phaseActuelle.phaseDestination
                self.tempsPhase = 0
                self.transition = True
        
        # Remove as demandas de prioridade que foram atendidas
        # Considera-se a demanda atendida quando a fase atual permite que o veiculo passe E
        #   o veiculo ja passou dureeBus segundos na fase
        if self.phaseActuelle.type == 'phase':
            for demande in self.demandesPriorite:
                if demande.codePriorite == self.phaseActuelle.codePriorite:
                    if min((self.tempsPhase, -demande.delaiApproche)) >= self.phaseActuelle.dureeBus:
                        demande.codePriorite = 0
            self.demandesPriorite = [demande for demande in self.demandesPriorite if demande.codePriorite > 0]
        
        # Atualiza a cor de cada linha
        for i,ligne in enumerate(self.listeLignes):
            if self.phaseActuelle.type == 'phase':
                ligne.couleur = 'green' if self.phaseActuelle.lignesActives[i] else 'red'
            
            elif self.phaseActuelle.type == 'interphase':
                if self.phaseActuelle.tempsChangement[i] == self.tempsPhase:
                    if ligne.couleur == 'red':
                        ligne.couleur = 'green'
                    elif ligne.couleur == 'green':
                        if ligne.type == 'pieton':
                            ligne.couleur = 'red'
                        elif ligne.type == 'voiture':
                            ligne.couleur = 'yellow'
                            ligne.compteurJaune = 0
                            
            if ligne.couleur == 'yellow':
                if ligne.compteurJaune == ligne.tempsJaune:
                    ligne.couleur = 'red'
                else:
                    ligne.compteurJaune += 1
        
        # Atualiza contadores
        self.tempsPhase += 1
        
        for ligne in self.listeLignes:          
            if ligne.couleur == 'red' and ligne.solicitee:
                ligne.compteurRouge += 1
                
            elif ligne.couleur == 'green':
                ligne.compteurRouge = 0
        
        for demande in self.demandesPriorite:
            demande.delaiApproche -= 1
        
    def interphase(self, phase1, phase2):
        return self.matriceInterphase[phase1.numero][phase2.numero]
        
    def soliciterPhase(self, n):
        self.listePhases[n].solicitee = True
    
    def demanderPriorite(self, delaiApproche, codePriorite, codeVehicule):
        for demande in self.demandesPriorite:
            if demande.codeVehicule == codeVehicule:
                demande.delaiApproche = delaiApproche
                break
        else:
            self.demandesPriorite.append(DemandePriorite(delaiApproche, codePriorite, codeVehicule))
    
    
