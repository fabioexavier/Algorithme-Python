A = np.zeros((2*len(chemin)+2*len(demandesPriorite),2*len(chemin)+len(demandesPriorite)))
b = np.zeros(2*len(chemin)+2*len(demandesPriorite))

for i,demande in enumerate(demandesPriorite):
    posPhase = [phase.prioritaire==demande[1] for phase in chemin.listePhases].index(True)
    for j in range(posPhase):
        A[2*i,j] = 1
    A[2*i,2*len(chemin)+i] = 1
    
    for j in range(posPhase+1):
        A[2*i+1,j] = -1
    A[2*i+1,2*len(chemin)+i] = -1
        
    sommeInterphases = 0
    for k in range(posPhase):
        phase1 = chemin.listePhases[k]
        phase2 = chemin.listePhases[k+1]
        sommeInterphases += carrefour.matriceInterphase[phase1.numero][phase2.numero].duree
    b[2*i] = demande[0] + carrefour.tempsPhase - sommeInterphases
    b[2*i+1] = -b[2*i] - chemin.listePhases[posPhase].dureeBus    
    

for i,phase in enumerate(chemin.listePhases):
    A[2*len(demandesPriorite)+2*i, i] = 1
    A[2*len(demandesPriorite)+2*i, i+len(chemin)] = -1
    A[2*len(demandesPriorite)+2*i+1, i] = -1
    A[2*len(demandesPriorite)+2*i+1, i+len(chemin)] = -1
    
    b[2*len(demandesPriorite)+2*i] = phase.dureeNominale
    b[2*len(demandesPriorite)+2*i+1] = -phase.dureeNominale


c = np.zeros(2*len(chemin)+len(demandesPriorite))
for i in range(len(chemin), 2*len(chemin)):
    c[i] = 1
for i in range(len(demandesPriorite)):
    c[2*len(chemin)+i]=100

bounds = [(max((chemin.listePhases[0].dureeMinimale,carrefour.tempsPhase)),chemin.listePhases[0].dureeMaximale)]
for phase in chemin.listePhases[1:]:
    bounds.append((phase.dureeMinimale, phase.dureeMaximale))
for phase in chemin.listePhases:
    bounds.append((0,None))
for demande in demandesPriorite:
    bounds.append((0,None))

print(A)


res = opt.linprog(c, A_ub=A, b_ub=b, bounds=bounds, options={'disp':True, 'tol':1e-10})

#    durees = res.x[:len(chemin)]
#    attentes = res.x[2*len(chemin):]
print(res.x)