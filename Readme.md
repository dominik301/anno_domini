Anno Domini
===========
###Implementazione di un gioco distribuito basato su un modello architetturale RESTful

## Indice ##

- [Sommario](#sommario)
- [Introduzione](#introduzione)  
- [Aspetti progettuali](#aspetti-progettuali)  
	- [Interazione dei componenti del sistema](#interazione-dei-componenti-del-sistema)
	- [Tolleranza ai guasti](#tolleranza-ai-guasti)
- [Aspetti implementativi](#aspetti-implementativi)  
- [Valutazioni](#valutazioni)  
- [Conclusioni](#conclusioni)

##Sommario##
Il progetto Anno Domini trae spunto da un gioco di carte omonimo che combina l'idea di base di porre in un preciso ordine una sequenza di elementi, tipica del Domino, con la successione cronologica di alcuni eventi storici. 

Il gioco non prevede nessun elemento di perno, ossia specifici ruoli ricoperti da un unico componente del gioco preso in esame (quale potrebbe essere quello del dealer nel Blackjack). Il che, evidentemente, rende Anno Domini particolarmente coniugabile con i paradigmi caratteristici dei sistemi distribuiti. 

In questa relazione descriviamo in che modo è stato ideato e progettato tale sistema distribuito, assumendo l'eventualità dei soli guasti di tipo crash dei processi, ossia dei giocatori partecipanti alla partita. Il sistema è stato implementato facendo riferimento al modello architetturale di tipo REST .

##Introduzione##
Anno Domini prevede la partecipazione di un minimo di quattro giocatori alla partita, ad ognuno dei quali vengono distribuite sette carte. Ogni carta rappresenta uno specifico evento storico, visibile ai giocatori anche quando questa è coperta. Quando la carta viene scoperta viene invece esternato l'anno di riferimento. Come già accennato, lo scopo del gioco è quello di mettere in ordine cronologico, dal più lontano al più recente, gli eventi storici e vince il giocatore che rimane senza carte in mano.

Inizialmente sul banco è presente una sola carta coperta. Man mano che si va avanti con il procedere del gioco, la sequenza presente sul banco si arricchisce di nuove carte, opportunamente posizionate dai giocatori rispettando i turni.

Ogni partecipante alla partita può scegliere di effettuare due tipi diversi di giocate, a seconda del fatto che egli possa ritenere corretta o errata la sequenza di carte posizionate fino a quel momento sul banco. Se ritiene che sia corretta, può giocare la prossima carta, scegliendola dalla propria mano e ponendola all'interno della sequenza nel banco. Mentre se crede che la successione delle carte comuni sia sbagliata, può dubitare: ciò determina la rivelazione delle date degli eventi storici presenti sul banco. In tal caso, se la successione risulta errata il giocatore precedente dovrà pescare tre carte e il giocatore che aveva dubitato potrà giocare una sua carta. Di contro, se la successione risulta corretta lo stesso giocatore che aveva dubitato deve pescare due carte e il turno passerà al giocatore successivo.

La partita termina nel momento in cui un giocatore rimane senza nessuna carta in mano a patto che la sequenza sul banco sia corretta. Infatti, se un giocatore esaurisce le proprie carte, ma la sequenza non risulta corretta, deve pescare due carte del mazzo; il gioco riprende quindi dal partecipante successivo.

La tecnologia REST è inizialmente nata per permettere a servizi web di rilasciare proprie API mantenendo HTTP come protocollo cardine. Solo successivamente ci si sta rendendo conto del fatto che può essere impiegato per la realizzazione dei sistemi distriubuiti. La nostra scelta è ricaduta su REST proprio per sperimentare questo nuovo modo di creare sistemi distribuiti.

##Aspetti progettuali##
Il primo problema che si incontra nel realizzare un sistema distribuito è fare in modo che ogni nodo sia consapevole della costituzione del sistema di cui fa parte. Per una mera questione di semplicità è stato impiegato un Registrar Server, dedicato alla registrazione dei nodi. Dunque, i vari componenti del sistema distribuito si iscrivono presso il server in qualità di giocatori, per poi prendere parte alla partita. Nel momento in cui viene raggiunto il numero di giocatori richiesto, la partita può iniziare. Da questo momento in poi il ruolo del Registrar Server non è più necessario: il sistema distribuito appena creatosi è in grado di auto-gestirsi senza più ricorrere all'ausilio del Registrar.

Nel dettaglio, la fase preliminare per poter dare il via al gioco è strutturata come segue: i giocatori si registrano presso il server scegliendo uno username univoco. Uno dei potenziali giocatori crea un nuovo gioco, specificando il numero di partecipanti desiderato: ci riferiremo a tale giocatore come creator. Gli altri nodi si iscrivono al gioco presso il Registrar Server: nel momento in cui viene raggiunto il numero desiderato di giocatori, la partita può iniziare. Quindi il server informa, tramite un apposito messaggio, tutti gli iscritti alla partita: da questo momento in poi il Registrar non sarà più utilizzato.
Per assegnare il primo turno del gioco sarebbe necessario, in teoria, l'utilizzo di un algoritmo distribuito per deciderlo, analogo a quello di elezione del leader. In realtà non c'è un concreto bisogno di tale passaggio poiché si può assumere che il primo turno spetti al creator della partita.

A questo punto, i nodi sono in grado di gestire autonomamente il gioco durante la sua evoluzione. Quando un giocatore deve effettuare una giocata (sia che essa sia un dubbio, sia che si tratti della giocata di una carta), invia un messaggio in broadcast a tutti gli altri. Quest'approccio consente a tutti i partecipanti della partita di mantenere le risorse di gioco aggiornate poiché sono dislocate in modo distribuito.

Considerate le caratteristiche dello scenario, l'architettura astratta del sistema distribuito è quella ad anello. I turni, così come le risorse del gioco, quali il mazzo o le carte presenti sul banco, vengono gestite in modo distribuito. Ciò vuol dire che tali informazioni sono replicate su più nodi, in modo da poter tollerare eventuali guasti dei processi senza compromettere il prosieguo del gioco.

Come già detto, le caratteristiche del gioco consentono un'agevole realizzazione mediante un sistema distribuito. Infatti la mancanza di un componente di controllo centralizzato e l'indipendenza dei nodi costituiscono, se vogliamo, un denominatore comune per il gioco e il mondo dei sistemi distribuiti. 

La scelta della tecnologia impiegata con cui è stato realizzato il nostro sistema distribuito è ricaduta su REST. Allo stato dell'arte sembra essere molto sfruttata: basta per esempio considerare alcuni punti di riferimento in questo campo, come Amazon e Google, che stanno attualmente adottando questo modello architetturale.

###Interazione dei componenti del sistema###
Vediamo ora da un punto di vista progettuale come abbiamo deciso di realizzare la comunicazione dei vari elementi che compongono il nostro sistema. In particolare vengono descritte le fasi di registrazione, preparazione, svolgimento di una giocata e dubbio.

Prima di iniziare il gioco, il player deve registrarsi al Registrar Server. La registrazione avviene inviando un messaggio di createPlayer a quest'ultimo . Dopo la registrazione, il giocatore può creare una nuova partita specificando anche il numero di giocatori desiderato oppure unirsi ad una già esistente (se creata precedentemente da un altro giocatore) mediante il messaggio joinGame. Una volta creata una partita il server aggiorna tutti gli utenti registrati inviando il messaggio rcvGameList.

![Alt text](./documentation/img/Registrazione.png)

Nel momento in cui il numero di giocatori richiesto dal creator è raggiunto, nessun altro utente potrà più iscriversi alla partita in questione: il server invia a tutti i partecipanti il messaggio di startGame, contenente la lista dei giocatori, per comunicare l’inizio della partita.
Come già ancitipato in precedenza, a questo punto sarebbe necessario utilizzare un algoritmo analogo a quello di elezione del leader per stabilire quale giocatore tra i partecipanti avrà il turno. Poiché esiste un solo creator, per semplicità, abbiamo assunto che sia quest'ultimo il primo di mano. Dunque, quando il creator riceve il messaggio startGame, a differenza degli altri giocatori, distribuisce le carte attraverso il messaggio rcvCards, per poi distribuire la configurazione del tavolo (inizialmente è costituito da una sola carta) usando il messaggio rcvTable e il mazzo restante (messaggio rcvDeck). Precisiamo il fatto che, mentre la distribuzione delle carte e del tavolo è un'operazione fondamentale per il gioco, l'invio a tutti del mazzo viene fatta per un motivo legato alla tolleranza ai guasti. Infatti, se così non fosse, il guasto del singolo nodo che detiene il mazzo impedirebbe agli altri partecipanti di continuare il gioco.

![Alt text](./documentation/img/Preparazione.png)

Quando un giocatore gioca una carta, viene inviato un messaggio playedCard in broadcast a tutti i giocatori (viene recapitato anche a sè stesso).

![Alt text](./documentation/img/PlayCard.png)

Analogamente, quando un giocatore dubita viene inviato in broadcast un messaggio doubted. Tutti i nodi che ricevono questo messaggio eseguono la computazione del dubbio in locale, verificando se il dubbio era fondato o meno: in tal modo ogni nodo stabilisce quale giocatore deve pescare le carte di penalizzazione e assegna il turno relativo alla giocata successiva. Tale operazione consente di mantenere il sistema in uno stato coerente (ad esempio tenendo aggiornati i contatori relativi al numero di carte relativi ai vari giocatori su ogni nodo).

![Alt text](./documentation/img/Dubbio.png)

##Tolleranza ai guasti
Il tipo di guasto che tollera il nostro sistema è solo il crash, e confinato esclusivamente a partire dal momento in cui inizia la partita. Quindi, eventuali guasti che insistono sul Registrar Server non vengono gestiti poiché si assume che esso funzioni senza alcuna complicazione. Si suppone inoltre che la rete sottostante sia affidabile: l'invio e la ricezione dei messaggi avviene in modo corretto ed entro un tempo ragionevole.

Di conseguenza, risolvere il problema della tolleranza ai guasti si traduce principalmente nell'identificare i nodi che vanno in crash, per poi adottare una specifica (TODO: parlo qui della politica?) politica che permetta agli altri giocatori di continuare a giocare. Per convenzione, abbiamo stabilito che una partita può continuare finché sono presenti almeno quattro giocatori.

Abbiamo evitato soluzioni in cui i nodi si scambiano messaggi di liveness, i quali avrebbero aumentato la complessità del funzionamento del singolo nodo ed aumentato il numero di messaggi in circolo sulla rete.
Il nostro approccio, invece, fa uso di un timer, presente su ogni nodo, il quale viene avviato nel momento in cui la partita ha inizio e riavviato quando viene passato il turno. La scadenza imposta dal timer definisce il tempo limite entro il quale il giocatore di turno deve effettuare la giocata. Poiché non sono tollerati guasti di omissione (quale potrebbe essere la mancata giocata da parte del player di turno), abbiamo assunto che ogni giocata avviene prima che il timer scada. Poiché non sono tollerati nemmeno i guasti relativi alla rete, il messaggio riguardante la giocata sarà ricevuto correttamente dagli altri partecipanti. Riassumendo, la scadenza del timer su un determinato nodo inferisce la credenza in quest'ultimo che il giocatore di turno ha subito un crash.

TODO: dire che i timer non sono sincronizzati e che, per quanto possa essere affidabile la rete, i messaggi impiegheranno un certo tempo t per arrivare a destinazione. Quindi la giocata fatta nel tempo limite di scadenza del timer potrebbe arrivare in tempo per alcuni e per altri no. Parlare quindi del timer del browser.

Ogni nodo conosce l'esatta sequenza dei turni di una partita: istante per istante è in grado di identificare il giocatore in possesso del turno. Per cui, se si verifica un evento di timeout vuol dire che il giocatore in possesso del turno è andato in crash. La funzione di callback effettua le operazioni necessarie per la rimozione di tale nodo dalla partita e l'aggiornamento del turno, che viene assegnato al giocatore successivo.
La durara del timeout è abbastanza lunga da consentire ad un nodo sia di effettuare una giocata, completando il proprio turno, e sia di inviare un messaggio a tutti gli altri giocatori.

Vediamo ora nelle specifico il funzionamento del timeout all'interno del nodo in due casi diversi: 

- Il server comunica ai giocatori che possono iniziare la partita, i giocatori fanno partire i timer a cui associano la funzione di callback. Il giocatore a cui spetta il turno effettua una giocata (che può essere un un'azione di dubbio oppure la giocata di una carta della sua mano) ed invia a tutti gli altri partecipanti un messaggio dell'azione effettuata. Alla ricezione di tale messaggio gli altri giocatori a loro volta resettano il timeout; automaticamente il turno viene calcolato in ogni nodo ed assunto univocamente da uno dei giocatori (quello successivo a quello che ha fatto precedentemente la giocata).

![Alt text](./documentation/img/schemaTO_1.png)

- Il server invia la start_game ai giocatori, questi fanno partire il timer, il giocatore player_0 non effettua alcuna giocata prima dello scadere del timer, questo evento provoca lo scadere del timeout sia sul primo giocatore che sul secondo, nel quale fa funzione di callback gli permette di assumere il turno. Tutti quanti i partecipanti da questo momento considerano player_0 fuori dalla sessione di gioco.

![Alt text](./documentation/img/schemaTO_2.png)

##Aspetti implementativi##

##Valutazioni##

##Conclusioni##

Api Rest
==================
| Msg | SentBy | RcvBy | Type |Crud | Description |
|-----|:------:|:-----:|:----:|:---:|------------:|
| getGames() | a client | the server | unicast | GET |un client desidera ricevere la lista di partite pubbliche disponibili sul server |
| createGame() | a client | the server | unicast | POST |un client intende creare una nuova partita |
| joinGame() | a client | the server | unicast | PUT |un client intende partecipare ad una partita |
| startGame() | the server | some clients | broadcast | PUT | quando il server capisce che una partita può cominciare (raggiungimento del numero di giocatori prestabilito) allora fa cominciare la partita e invia a tutti la lista dei partecipanti
| sendCards() | a client | all other clients partecipating in the game | broadcast | PUT | il client che ha creato la partita invia agli altri partecipanti le carte delle loro mani e il mazzo di carte rimanenti |
| playFirstCard() | a client | all other clients partecipating in the game | broadcast | PUT | il client che ha creato la partita mette sul tavolo la prima carta del gioco e la comunica a tutti gli altri giocatori |
| playCard() | a client | all other clients partecipating in the game | broadcast | PUT | un giocatore gioca una carta dalla propria mano mettendola sul banco |
| sendToken() | a client | next client in the turn | unicast | PUT | il giocatore che termina il proprio turno passa il token al giocatore del turno successivo |
| sendDoubt() | a client | all other clients partecipating in the game | broadcast | ? | un giocatore dubita sulla sequenza degli eventi del banco e lo rende noto a tutti gli altri giocatori | 
| zeroCards() | a clent | all other clients partecipating in the game | broadcast | POST | un giocatore comunica a tutti gli altri che non ha più carte in mano e quindi ha vinto la partita |
| createPlayer() | a client | the server | unicast | POST | un client richiede al server la creazione del profilo di giocatore |
| sendGames() | the server | a client | unicast | POST | il server invia al client richiedente la lista di partite disponibili |
| playerCreationResponce() | the server | a client | unicast | ? | il server invia l'esito della creazione di un giocatore |  
| cancelSubscription() | a client | the server | unicast | DELETE | il client invia un messaggio al server di uscita dalla partita |
