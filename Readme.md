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

Nel dettaglio, la fase preliminare per poter dare il via al gioco è strutturata come segue:
I giocatori si registrano presso il server scegliendo uno username univoco;
Uno dei potenziali giocatori crea un nuovo gioco, specificando il numero di partecipanti desiderato. Ci riferiremo a tale giocatore come creator;
Gli altri nodi si iscrivono al gioco presso il Registrar Server: nel momento in cui viene raggiunto il numero desiderato di giocatori, la partita può iniziare. Quindi il server informa, tramite un apposito messaggio, tutti gli iscritti alla partita: da questo momento in poi il Registrar non sarà più utilizzato.
Per assegnare il primo turno del gioco sarebbe necessario, in teoria, l'utilizzo di un algoritmo distribuito per deciderlo, analogo a quello di elezione del leader. In realtà non c'è un concreto bisogno di tale passaggio poiché si può assumere che il primo turno spetti al creator della partita.

A questo punto, i nodi sono in grado di gestire autonomamente il gioco durante la sua evoluzione. Quando un giocatore deve effettuare una giocata (sia che essa sia un dubbio, sia che si tratti della giocata di una carta), invia un messaggio in broadcast a tutti gli altri. Quest'approccio consente a tutti i partecipanti della partita di mantenere le risorse di gioco aggiornate poiché sono dislocate in modo distribuito.

Viste le caratteristiche del gioco, l'architettura astratta del sistema distribuito è quella ad anello. I turni, così come le risorse del gioco, quali il mazzo o le carte presenti sul banco, vengono gestite in modo distribuito. Ciò vuol dire che tali informazioni sono replicate su più nodi, in modo da poter tollerare eventuali guasti dei processi senza compromettere il prosieguo del gioco.

Come già detto, le caratteristiche del gioco consentono un'agevole realizzazione mediante un sistema distribuito. Infatti la mancanza di un componente di controllo centralizzato e l'indipendenza dei nodi costituiscono, se vogliamo, un denominatore comune per il gioco e il mondo dei sistemi distribuiti. 

La scelta della tecnologia impiegata con cui è stato realizzato il nostro sistema distribuito è ricaduta su REST. Allo stato dell'arte sembra essere molto sfruttata: basta per esempio considerare alcuni punti di riferimento in questo campo, come Amazon e Google, che stanno attualmente sfruttando questo modello architetturale.

###Interazione dei componenti del sistema###
Vediamo ora da un punto di vista progettuale come abbiamo deciso di realizzare la comunicazione dei vari elementi che compongono i nostro sistema. In particolare vengono descritte le fasi di: registrazione, preparazione, lo svolgimento di una giocata e di un dubbio.

Prima di iniziare il gioco, il player deve registrarsi al server registrar. La registrazione avviene inviando un messaggio di createPlayer() al server . Dopo la registrazione, il giocatore può creare una nuova partita oppure, se già stata creata una partita, può fare la join ad una partita esistente con un messaggio joinGame(). Una volta creata una partita il server invia a tutti i giocatori la lista delle partite disponibili con il messaggio rcvGameList().

![Alt text](./documentation/img/Registrazione.png)

Quando l'ultimo giocatore fa la join() ad una partita creata in precedenza, il server invia a tutti i giocatori registrati a quella partita, il messaggio di start_g() , contenente la lista dei giocatori, per comunicare l’inizio della partita a tutti. Quando il messaggio viene ricevuto dal creatore, egli stesso crea la propria mano, il tavolo dopodiché distribuisce le carte a tutti i partecipanti con un messaggio rcvCards(), distribuisce il tavolo che ha creato con un messaggio rcvTable() e infine distribuisce il mazzo risultante in modo tale che esso sia distribuito a tutti i giocatori.

![Alt text](./documentation/img/Preparazione.png)

Quando un giocatore gioca una carta, viene inviata a tutti i giocatori  anche al giocatore stesso con li messaggio playedCard().

![Alt text](./documentation/img/PlayCard.png)

Quando un giocatore dubita viene inviato a tutti i giocatori, anche a se stesso un messaggio doubted(). Tutti i nodi che ricevono questo messaggio eseguono la computazione del dubbio in locale, verificando se il dubbio era fondato o meno stabilendo il passaggio del turno e chi deve pescare le carte per la penalità.

![Alt text](./documentation/img/Dubbio.png)

##Tolleranza ai guasti
La tolleranza ai guasti del nostro sistema distribuito si occupa di capire se i nodi partecipanti ad una sessione di gioco vanno in crash; non vengono considerati eventuali mal funzionamenti del server di registrat. Si suppone inoltre che la rete sottostante sia affidabile, l'invio e la ricezione dei messaggi avviene in modo corretto ed entro un tempo ragionevole.

Il problema principale è stato quello di identificare i nodi che vanno in crash e per convenzione abbiamo stabilito che una partita può continuare fin tanto che rimangono attivi almeno 4 giocatori.

Abbiamo evitato soluzioni in cui i nodi si scambiano messaggi di liveness, i quali avrebbero aumentato la complessità del funzionamento del singolo nodo ed aumentato il numero di messaggi in circolo sulla rete.
Nella nostra soluzione al problema ogni nodo è in possesso di un timer a cui è associata una funzione di callback, che si attiva allo scadere del timer. La scadenza del timer, in un nodo, viene interpretata come il crash del giocatore da cui si aspettava una giocata (o un'azione di dubbio).

Ogni nodo conosce l'esatta sequenza dei turni di una partita: istante per istante è in grado di identificare il giocatore in possesso del turno. Per cui, se si verifica un evento di timeout vuol dire che il giocatore in possesso del turno è andato in crash. La funzione di callback effettua le operazioni necessarie per la rimozione di tale nodo dalla partita e l'aggiornamento del turno, che viene assegnato al giocatore successivo.
La durara del timeout è abbastanza lunga da consentire ad un nodo sia di effettuare una giocata, completando il proprio turno, e sia di inviare un messaggio a tutti gli altri giocatori.

Vediamo ora nelle specifico il funzionamento del timeout all'interno del nodo in due casi diversi: 

- Il server comunica ai giocatori che possono iniziare la partita, i giocatori fanno partire i timer a cui associano la funzione di callback. Il giocatore a cui spetta il turno effettua una giocata (che può essere un un'azione di dubbio oppure la giocata di una carta della sua mano) ed invia a tutti gli altri partecipanti un messaggio dell'azione effettuata. Alla ricezione di tale messaggio gli altri giocatori a loro volta resettano il timeout; automaticamente il turno viene calcolato in ogni nodo ed assunto univocamente da uno dei giocatori (quello successivo a quello che ha fatto precedentemente la giocata).

![Alt text](./documentation/img/schemaTO_1.png)

- Il server invia la start_game ai giocatori, questi fanno partire il timer, il giocatore player_0 non effettua alcuna giocata prima dello scadere del timer, questo evento provoca lo scadere del timeout sia sul primo giocatore che sul secondo, nel quale fa funzione di callback gli permette di assumere il turno. Tutti quanti i partecipanti da questo momento considerano player_0 fuori dalla sessione di gioco.

![Alt text](./documentation/img/schemaTO_2.png)

##Aspetti implementativi##

Linguaggi usati

lato server:

- python	2.7

lato client:

- javascript
- html
- css

Il sistema si compone di tre elementi principali

- Il Server di Registrar, implementato nel file server.py,  offre i seguenti servizi REST al player_server.

| Metodo | HTTP Request | Descrizione servizio |
|--------|:------------:|---------------------:|
| get_players() | GET /playerList | Restituisce la lista dei giocatori iscritti al server |
| get_games() | GET /gameList | Restituisce la partita attiva sul server |
| create_p(username, porta) | POST /createPlayer/<string:username>/<int:porta> | Crea un nuovo giocatore all'interno del sistema  |
| create_g(username, n_players) | POST /createGame/<string:username>/<int:n_players> | Restituisce la lista dei giocatori iscritti al server |
| join_g(username, game_id) | PUT /joinGame/<string:username>/<int:game_id> | Permette ad un player la partecipazione ad una partita esistente se non è stato già 	raggiunto il numero di giocatori impostato al momento della creazione della partita |

- Il Player server è implementato nel file player_server.py ed implementa la logica di un singolo giocatore. Offre i seguenti servizi REST.

| Metodo | HTTP Request | Descrizione servizio |
|--------|:------------:|---------------------:|
| game_status() | GET /gameStatus | Permette di conoscere lo stato del gioco, cioè se la partita è iniziata oppure no |
| doubt_status() | POST /createPlayer/<string:username> | Permette di controllare se è stato sollevato un dubbio |
| create_p() | GET /playerList | Richiede la creazione di un nuovo giocatore sul server |
| gameList() | GET /gameList | Restituisce la lista delle partite |
| create_g(n_players) | POST /createGame/<int:n_players> | Crea una partita sul server |
| join_g() | PUT /joinGame/<int:id_game> | Effettua la join in una partita del server |
| start_g() | GET /startGame | Servizio richiamato dal Server di Registrar per iniziare una nuova partita |
| rcvGamesList() | POST /rcvGamesList | servizio richiamato dal Server di Registrar per ricevere la lista dei giocatori |
| rcvCards() | POST /receiveCards | Permette di ricevere le carte da gioco |
| rcvTable() | POST /receiveTable | permette di ricevere le carte sul banco |
| rcvDeck() | POST /receiveDeck | Permette di ricevere il mazzo |
| playedCard(username, year, event, card_id, position) | PUT /playedCard/<string:username>/<int:year>/<string:event>/<int:card_id>/<int:position> | permette di ricevere la giocata di uno dei partecipanti |
| doubted(username) | PUT /doubted/<string:username> | permette di ricevere un'azione di dubbio sollevata da uno dei giocatori |

La GUI è implementata nel file gui.html. L'interfaccia grafica per il suo funzionamento ha bisogno dei servizi implementati nel player_server.py ed utilizza tecniche di polling standard per poter ricevere i cambiamenti di stato di una sessione di gioco. Ad esempio, si effettua polling per monitorare stato del turno oppure un possibile stato di dubbio sulla sequenza di carte del banco; l'obiettivo del progetto non era quello di creare un'interfaccia grafica sofisticata e anche questa descrizione è sufficiente.

##Valutazioni##

##Conclusioni##
