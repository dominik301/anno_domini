Anno Domini
===========
### Implementazione di un gioco distribuito basato su un modello architetturale RESTful

[Sommario](#sommario)  
[Introduzione](#introduzione)  
[Aspetti progettuali](#asp_prog)  
[Aspetti implementativi](#asp_impl)  
[Valutazioni](#valutazioni)  
[Conclusioni](#conclusioni)

##Sommario
<a name="sommario"/>
Il progetto Anno Domini trae spunto da un gioco di carte omonimo che combina l'idea di base di porre in un preciso ordine una sequenza di elementi, tipica del Domino, con la successione cronologica di alcuni eventi storici. 

Il gioco non prevede nessun elemento di perno, ossia specifici ruoli ricoperti da un unico componente del gioco preso in esame (quale potrebbe essere quello del dealer nel Blackjack). Il che, evidentemente, rende Anno Domini particolarmente coniugabile con i paradigmi caratteristici dei sistemi distribuiti. 

In questa relazione descriviamo in che modo è stato ideato e progettato tale sistema distribuito, assumendo l'eventualità dei soli guasti di tipo crash dei processi, ossia dei giocatori partecipanti alla partita. Il sistema è stato implementato facendo riferimento al modello architetturale di tipo REST .

##Introduzione
<a name="sommario"/>
Anno Domini prevede la partecipazione di un minimo di quattro giocatori alla partita, ad ognuno dei quali vengono distribuite sette carte. Ogni carta rappresenta uno specifico evento storico, visibile ai giocatori anche quando questa è coperta. Quando la carta viene scoperta viene invece esternato l'anno di riferimento. Come già accennato, lo scopo del gioco è quello di mettere in ordine cronologico, dal più lontano al più recente, gli eventi storici e vince il giocatore che rimane senza carte in mano.

Inizialmente sul banco è presente una sola carta coperta. Man mano che si va avanti con il procedere del gioco, la sequenza presente sul banco si arricchisce di nuove carte, opportunamente posizionate dai giocatori rispettando i turni.

Ogni partecipante alla partita può scegliere di effettuare due tipi diversi di giocate, a seconda del fatto che egli possa ritenere corretta o errata la sequenza di carte posizionate fino a quel momento sul banco. Se ritiene che sia corretta, può giocare la prossima carta, scegliendola dalla propria mano e ponendola all'interno della sequenza nel banco. Mentre se crede che la successione delle carte comuni sia sbagliata, può dubitare: ciò determina la rivelazione delle date degli eventi storici presenti sul banco. In tal caso, se la successione risulta errata il giocatore precedente dovrà pescare tre carte e il giocatore che aveva dubitato potrà giocare una sua carta. Di contro, se la successione risulta corretta lo stesso giocatore che aveva dubitato deve pescare due carte e il turno passerà al giocatore successivo.

La partita termina nel momento in cui un giocatore rimane senza nessuna carta in mano a patto che la sequenza sul banco sia corretta. Infatti, se un giocatore esaurisce le proprie carte, ma la sequenza non risulta corretta, deve pescare due carte del mazzo; il gioco riprende quindi dal partecipante successivo.

La tecnologia REST è inizialmente nata per permettere a servizi web di rilasciare proprie API mantenendo HTTP come protocollo cardine. Solo successivamente ci si sta rendendo conto del fatto che può essere impiegato per la realizzazione dei sistemi distriubuiti. La nostra scelta è ricaduta su REST proprio per sperimentare questo nuovo modo di creare sistemi distribuiti.

Aspetti progettuali 
===================
Il primo problema che si incontra nel realizzare un sistema distribuito è fare in modo che ogni nodo sia consapevole della costituzione del sistema di cui fa parte. Per una mera questione di semplicità è stato impiegato un Registrar Server, dedicato alla registrazione dei nodi. Dunque, i vari componenti del sistema distribuito si iscrivono presso il server in qualità di giocatori, per poi prendere parte alla partita. Nel momento in cui viene raggiunto il numero di giocatori richiesto, la partita può iniziare. Da questo momento in poi il ruolo del Registrar Server non è più necessario: il sistema distribuito appena creatosi è in grado di auto-gestirsi senza più ricorrere all'ausilio del Registrar.

Nel dettaglio, la fase preliminare per poter dare il via al gioco è strutturata come segue:
I giocatori si registrano presso il server scegliendo uno username univoco;
Uno dei potenziali giocatori crea un nuovo gioco, specificando il numero di partecipanti desiderato. Ci riferiremo a tale giocatore come creator;
Gli altri nodi si iscrivono al gioco presso il Registrar Server: nel momento in cui viene raggiunto il numero desiderato di giocatori, la partita può iniziare. Quindi il server informa, tramite un apposito messaggio, tutti gli iscritti alla partita: da questo momento in poi il Registrar non sarà più utilizzato.
Per assegnare il primo turno del gioco sarebbe necessario, in teoria, l'utilizzo di un algoritmo distribuito per deciderlo, analogo a quello di elezione del leader. In realtà non c'è un concreto bisogno di tale passaggio poiché si può assumere che il primo turno spetti al creator della partita.

A questo punto, i nodi sono in grado di gestire autonomamente il gioco durante la sua evoluzione. Quando un giocatore deve effettuare una giocata (sia che essa sia un dubbio, sia che si tratti della giocata di una carta), invia un messaggio in broadcast a tutti gli altri. Quest'approccio consente a tutti i partecipanti della partita di mantenere le risorse di gioco aggiornate poiché sono dislocate in modo distribuito.

Viste le caratteristiche del gioco, l'architettura astratta del sistema distribuito è quella ad anello. I turni, così come le risorse del gioco, quali il mazzo o le carte presenti sul banco, vengono gestite in modo distribuito. Ciò vuol dire che tali informazioni sono replicate su più nodi, in modo da poter tollerare eventuali guasti dei processi senza compromettere il prosieguo del gioco.

Tolleranza ai guasti
====================

La tolleranza ai guasti del nostro sistema distribuito si occupa di capire se i nodi partecipanti ad una sessione di gioco vanno in crash; non vengono considerati eventuali mal funzionamenti del server di registrat. Si suppone inoltre che la rete sottostante sia affidabile, l'invio e la ricezione dei messaggi avviene in modo corretto ed entro un tempo ragionevole.

Il problema principale è stato quello di identificare i nodi che vanno in crash e per convenzione abbiamo stabilito che una partita può continuare fin tanto che rimangono attivi almeno 4 giocatori.

Abbiamo evitato soluzioni in cui i nodi si scambiano messaggi di liveness, i quali avrebbero aumentato la complessità del funzionamento del singolo nodo ed aumentato il numero di messaggi in circolo sulla rete.
Nella nostra soluzione al problema ogni nodo è in possesso di un timer a cui è associata una funzione di callback, che si attiva allo scadere del timer. La scadenza del timer, in un nodo, viene interpretata come il crash del giocatore da cui si aspettava una giocata (o un azione di dubbio).

Ogni nodo conosce l'esatta sequenza dei turni di una partita: istante per istante è in grado di identificare il giocatore in possesso del turno. Per cui, se si verifica un evento di timeout vuol dire che il giocatore in possesso del turno è andato in crash. La funzione di callback effettua le operazioni necessarie per la rimozione di tale nodo dalla partita e l'aggiornamento del turno, che viene assegnato al giocatore successivo.
La durara del timeout è abbastanza lunga da consentire ad un nodo sia di effettuare una giocata, completando il proprio turno, e sia di inviare un messaggio a tutti gli altri giocatori.

Vediamo ora nelle specifico il funzionamento del timeout all'interno del nodo in due casi diversi: 

1. 1. Il server comunica ai giocatori che possono iniziare la partita, i giocatori fanno partire i timer a cui associano la funzione di callback. Il giocatore a cui spetta il turno effettua una giocata (che può essere un un'azione di dubbio oppure la giocata di una carta della sua mano) ed invia a tutti gli altri partecipanti un messaggio dell'azione effettuata. Alla ricezione di tale messaggio gli altri giocatori a loro volta resettano il timeout; automaticamente il turno viene calcolato in ogni nodo ed assunto univocamente da uno dei giocatori (quello successivo a quello che ha fatto precedentemente la giocata).

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
