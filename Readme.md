Anno Domini
===========

*Stefano Bettinelli*, *Roberto De Santis*, *Vincenzo Gambale*


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
Il progetto Anno Domini trae spunto da un gioco di carte omonimo che combina l'idea di base di ordinare una sequenza di elementi, tipica del Domino, con la successione cronologica di alcuni eventi storici. 

Il gioco non prevede nessun elemento di perno, ossia specifici ruoli ricoperti da un unico componente del gioco preso in esame (quale potrebbe essere quello del dealer nel Blackjack). Il che, evidentemente, rende Anno Domini particolarmente coniugabile con i paradigmi caratteristici dei sistemi distribuiti. 

In questa relazione descriviamo in che modo &egrave; stato ideato e progettato tale sistema distribuito, assumendo l'eventualit&agrave; dei soli guasti di tipo crash dei processi, ossia dei giocatori partecipanti alla partita. Il sistema &egrave; stato implementato facendo riferimento al modello architetturale di tipo REST .

##Introduzione##
Anno Domini prevede la partecipazione di un minimo di quattro giocatori alla partita, ad ognuno dei quali vengono distribuite sette carte. Ogni carta rappresenta uno specifico evento storico, visibile ai giocatori anche quando questa &egrave; coperta. Quando la carta viene scoperta, viene invece esternato l'anno di riferimento. Come gi&agrave; accennato, lo scopo del gioco &egrave; quello di mettere in ordine cronologico, dal pi&ugrave; lontano al pi&ugrave; recente, gli eventi storici e vince il giocatore che rimane senza carte in mano.

Inizialmente sul banco &egrave; presente una sola carta coperta. Man mano che si va avanti con il procedere del gioco, la sequenza presente sul banco si arricchisce di nuove carte, opportunamente posizionate dai giocatori rispettando i turni.

Ogni partecipante alla partita pu&ograve; scegliere di effettuare due tipi diversi di giocate, a seconda del fatto che egli possa ritenere corretta o errata la sequenza di carte posizionate fino a quel momento sul banco. Se ritiene che sia corretta, pu&ograve; giocare la prossima carta, scegliendola dalla propria mano e ponendola all'interno della sequenza nel banco. Mentre se crede che la successione delle carte comuni sia sbagliata, pu&ograve; dubitare: ci&ograve; determina la rivelazione delle date degli eventi storici presenti sul banco. In tal caso, se la successione risulta errata il giocatore precedente dovr&agrave; pescare tre carte e il giocatore che aveva dubitato potr&agrave; giocare una sua carta. Di contro, se la successione risulta corretta lo stesso giocatore che aveva dubitato deve pescare due carte e il turno passer&agrave; al giocatore successivo.

La partita termina nel momento in cui un giocatore rimane senza nessuna carta in mano a patto che la sequenza sul banco sia corretta. Infatti, se un giocatore esaurisce le proprie carte, ma la sequenza non risulta corretta, deve pescare due carte del mazzo; il gioco riprende quindi dal partecipante successivo.

La tecnologia REST &egrave; inizialmente nata per permettere a servizi web di rilasciare proprie API mantenendo HTTP come protocollo cardine. Solo successivamente ci si sta rendendo conto del fatto che pu&ograve; essere impiegato per la realizzazione dei sistemi distribuiti. La nostra scelta &egrave; ricaduta su REST proprio per sperimentare questo nuovo modo di creare sistemi distribuiti.

##Aspetti progettuali##
Il primo problema che si incontra nel realizzare un sistema distribuito &egrave; fare in modo che ogni nodo sia consapevole della costituzione del sistema di cui fa parte. Per una mera questione di semplicit&agrave; &egrave; stato impiegato un *Registrar Server*, dedicato alla registrazione dei nodi. Dunque, i vari componenti del sistema distribuito si iscrivono presso il server in qualit&agrave; di giocatori, per poi prendere parte alla partita. Nel momento in cui viene raggiunto il numero di giocatori richiesto, la partita pu&ograve; iniziare. Da questo momento in poi il Registrar Server non &egrave; pi&ugrave; necessario: il sistema distribuito appena creatosi &egrave; in grado di auto-gestirsi senza pi&ugrave; ricorrere all'ausilio del Registrar.

Nel dettaglio, la fase preliminare per poter dare il via al gioco &egrave; strutturata come segue: i giocatori si registrano presso il server scegliendo uno username univoco. Uno dei potenziali giocatori crea un nuovo gioco, specificando il numero di partecipanti desiderato: ci riferiremo a tale giocatore come *creator*. Gli altri nodi si iscrivono al gioco presso il Registrar Server: nel momento in cui viene raggiunto il numero desiderato di giocatori, la partita pu&ograve; iniziare. Quindi il server informa, tramite un apposito messaggio, tutti gli iscritti alla partita: da questo momento in poi il Registrar non sar&agrave; pi&ugrave; utilizzato.
Per assegnare il primo turno del gioco sarebbe necessario, in teoria, l'utilizzo di un algoritmo distribuito per deciderlo, analogo a quello di elezione del leader. In realt&agrave; non c'&egrave; un concreto bisogno di tale passaggio poich&egrave; si pu&ograve; assumere che il primo turno spetti al creator della partita.

A questo punto, i nodi sono in grado di gestire autonomamente il gioco durante la sua evoluzione. Quando un giocatore deve effettuare una giocata (sia che essa sia un dubbio, sia che si tratti della giocata di una carta), invia un messaggio in broadcast a tutti gli altri. Quest'approccio consente a tutti i partecipanti della partita di mantenere le risorse di gioco aggiornate poich&egrave; sono dislocate in modo distribuito.

Considerate le caratteristiche dello scenario, l'architettura astratta del sistema distribuito &egrave; quella ad anello. I turni, cos&igrave; come le risorse del gioco, quali il mazzo o le carte presenti sul banco, vengono gestite in modo distribuito. Ci&ograve; vuol dire che tali informazioni sono replicate su pi&ugrave; nodi, in modo da poter tollerare eventuali guasti dei processi senza compromettere il prosieguo del gioco.

Come gi&agrave; detto, le caratteristiche del gioco consentono un'agevole realizzazione mediante un sistema distribuito. Infatti la mancanza di un componente di controllo centralizzato e l'indipendenza dei nodi costituiscono, se vogliamo, un denominatore comune per il gioco e il mondo dei sistemi distribuiti. 

La scelta della tecnologia impiegata con cui &egrave; stato realizzato il nostro sistema distribuito &egrave; ricaduta su REST. Allo stato dell'arte sembra essere molto sfruttata: basta per esempio considerare alcuni punti di riferimento in questo campo, come Amazon e Google, che stanno attualmente adottando questo modello architetturale.

###Interazione dei componenti del sistema###
Vediamo ora da un punto di vista progettuale come abbiamo deciso di realizzare la comunicazione dei vari elementi che compongono il sistema. In particolare vengono descritte le fasi di registrazione, preparazione, svolgimento di una giocata e di dubbio.

Prima di iniziare il gioco, il player deve registrarsi al Registrar Server. La registrazione avviene inviando un messaggio di createPlayer a quest'ultimo . Dopo la registrazione, il giocatore pu&ograve; creare una nuova partita specificando anche il numero di giocatori desiderato oppure unirsi ad una gi&agrave; esistente (se creata precedentemente da un altro giocatore) mediante il messaggio joinGame. Una volta creata una partita il server aggiorna tutti gli utenti registrati inviando il messaggio rcvGameList.

![Alt text](./documentation/img/Registrazione.png)

Nel momento in cui il numero di giocatori richiesto dal creatore &egrave; raggiunto, nessun altro utente potr&agrave; pi&ugrave; iscriversi alla partita in questione: il server invia a tutti i partecipanti il messaggio di startGame, contenente la lista dei giocatori, per comunicare l'inizio della partita.
Come gi&agrave; ancitipato in precedenza, sarebbe necessario utilizzare un algoritmo analogo a quello di elezione del leader per stabilire quale giocatore tra i partecipanti avr&agrave; il turno. Poich&egrave; esiste un solo creatore, per semplicit&agrave;, abbiamo assunto che sia quest'ultimo il primo di mano. Dunque, quando il creatore riceve il messaggio startGame, a differenza degli altri giocatori, distribuisce le carte attraverso il messaggio rcvCards, per poi distribuire la configurazione del tavolo (inizialmente costituito da una sola carta) usando il messaggio rcvTable e il mazzo restante (messaggio rcvDeck). Precisiamo il fatto che, mentre la distribuzione delle carte e del tavolo &egrave; un'operazione fondamentale per il gioco, l'invio a tutti del mazzo viene fatta per un motivo legato alla tolleranza ai guasti. Infatti, se cos&igrave; non fosse, il guasto del singolo nodo che detiene il mazzo impedirebbe agli altri partecipanti di continuare il gioco.In ogni caso,questa scelta ha un risvolto positivo anche dal punto di vista prestazionale. Infatti, cos&igrave; facendo non &egrave; necessario usare ulteriori messaggi per inviare la carta estratta dal mazzo (che quindi risulterebbe centralizzato).

![Alt text](./documentation/img/Preparazione.png)

Quando un giocatore gioca una carta viene inviato un messaggio playedCard in broadcast a tutti i giocatori (compreso s&egrave; stesso).

![Alt text](./documentation/img/PlayCard.png)

Analogamente, quando un giocatore dubita viene inviato in broadcast un messaggio doubted. Tutti i nodi che ricevono questo messaggio eseguono la computazione del dubbio in locale, verificando se il dubbio era fondato o meno: in tal modo ogni nodo stabilisce quale giocatore deve pescare le carte di penalizzazione e assegna il turno relativo alla giocata successiva. Tale operazione consente di mantenere il sistema in uno stato coerente (ad esempio tenendo aggiornati i contatori relativi al numero di carte dei vari giocatori su ogni nodo).

![Alt text](./documentation/img/Dubbio.png)

##Tolleranza ai guasti
Il tipo di guasto che tollera il nostro sistema &egrave; solo il crash, e confinato esclusivamente a partire dal momento in cui inizia la partita. Quindi, eventuali guasti che insistono sul Registrar Server non vengono gestiti poich&egrave; si assume che esso funzioni senza alcuna complicazione. Si suppone inoltre che la rete sottostante sia affidabile: l'invio e la ricezione dei messaggi avviene in modo corretto ed entro un tempo ragionevole.

Di conseguenza, risolvere il problema della tolleranza ai guasti si traduce principalmente nell'identificare i nodi che vanno in crash, per poi adottare una specifica politica che permetta agli altri giocatori di continuare a giocare. Per convenzione, abbiamo stabilito che una partita pu&ograve; continuare finch&egrave; sono presenti almeno quattro giocatori.

Abbiamo evitato soluzioni in cui i nodi si scambiano messaggi di liveness, i quali avrebbero aumentato la complessit&agrave; del funzionamento del singolo nodo ed aumentato il numero di messaggi in circolo sulla rete. Il nostro approccio, invece, fa uso di un timer, presente su ogni nodo, il quale viene avviato nel momento in cui la partita ha inizio e riavviato quando viene passato il turno. La scadenza imposta dal timer definisce il tempo limite entro cui il giocatore in possesso del turno deve effettuare la giocata. Poich&egrave; non sono tollerati guasti di omissione (quale potrebbe essere la mancata giocata da parte del player di turno), abbiamo assunto che ogni giocata avviene prima che il timer scada. Inoltre, non tollerando nemmeno guasti relativi alla rete, il messaggio riguardante la giocata sar&agrave; ricevuto correttamente dagli altri partecipanti. Riassumendo, con la scadenza del timer su un determinato nodo, si inferisce che il giocatore da cui ci si aspettava una giocata ha subito un crash. Ovviamente, tutti i nodi sono a conoscenza del giocatore a cui &egrave; assegnato il turno in ogni momento.

La politica adottata nel caso in cui viene rilevato un crash permette agli altri nodi rimasti di continuare il gioco. Per il momento, ipotizziamo che tutti i nodi abbiano i timer sincronizzati (cosa che, in realt&agrave;, non &egrave;). Nel momento in cui il timer scade, tutti i nodi rimuovono dalla propria lista dei partecipanti il giocatore da cui ci si aspettava la giocata. Tale rimozione, comunque,&egrave; trasparente rispetto al passaggio del turno: subito dopo il rilevamento del crash, il turno sar&agrave; assegnato al giocatore successivo. Dunque, il sistema distribuito non risente di alcun effetto negativo derivante dal crash, se non il fatto che le carte che il nodo eliminato aveva in mano, prima che si manifestasse il malfunzionamento, vengono perse. &Egrave; importante notare che il crash di un nodo viene rilevato soltanto nel momento in cui il turno sar&agrave; ad esso assegnato. Infatti, se un nodo facesse crash quando non detiene il token, la mancata rilevazione istantanea da parte degli altri nodi non compromette nemmeno in minima parte il funzionamento del sistema. Dunque, soltanto quando arriver&agrave; il turno di tale nodo verr&agrave; attivato il relativo timer, che scadr&agrave;: la mancata giocata permetter&agrave; agli altri nodi del sistema di rilevare il crash. Ovviamente, se a causa di uno o pi&ugrave; crash, il numero di nodi dovesse risultare minore del minimo consentito (4), il gioco verr&agrave; interrotto.

Come gi&agrave; anticipato, in realt&agrave; i timer che permettono di rilevare un'eventuale malfunzionamento del giocatore di turno non sono sincronizzati. Infatti, nonostante la rete sia affidabile, non &egrave; possibile assumere che un messaggio relativo ad una giocata effettuata arrivi nello stesso istante ai vari destinatari. Di conseguenza, il timer relativo al prossimo player di turno partir&agrave; in istanti lievemente distanziati uno dall'altro sui vari nodi. Ma in uno scenario del genere, se il giocatore che detiene il token effettua la giocata allo scadere del tempo limite, si rischia che alcuni nodi accettino correttamente tale giocata, mentre in altri &egrave; gi&agrave; scaduto il timer, sfociando in una situazione di inconsistenza del sistema: qualcuno ha rilevato un crash che non si &egrave; manifestato. Per risolvere tale problema, abbiamo adottato un timer aggiuntivo, attivo esclusivamente sul giocatore di turno, il quale ha una scadenza pi&ugrave; breve (di 5 secondi, ad esempio), oltre cui non &egrave; pi&ugrave; consentito effettuare una giocata. Cos&igrave; facendo, la differenza di tempo tra il timer relativo alla possibilit&agrave; di giocare installata sul giocatore di turno e quello relativo al crash detection, consente, in virt&ugrave; del corretto funzionamento della rete, che i messaggi arrivino prima di un eventuale rilevamento fittizio di crash. 

Vediamo ora nelle specifico il funzionamento del timeout relativo al crash all'interno del nodo in due casi diversi: 

- Il server comunica ai giocatori che possono iniziare la partita: essi fanno partire il timer di crash detection. Il giocatore a cui spetta il turno effettua una giocata (che pu&ograve; essere un'azione di dubbio oppure la giocata di una carta della sua mano) entro il tempo limite dettato dal proprio timer relativo alla giocata, ed invia a tutti gli altri partecipanti un messaggio dell'azione effettuata. Alla ricezione di tale messaggio gli altri giocatori, a loro volta, resettano il timeout; automaticamente il turno viene calcolato in ogni nodo ed assunto univocamente da uno dei giocatori (quello successivo a quello che ha fatto precedentemente la giocata).

![Alt text](./documentation/img/schemaTO_1.png)

- Il server invia la start_game ai nodi, i quali fanno partire il timer. Poich&egrave; ha subito un crash, il giocatore player_0 non effettua alcuna giocata entro il tempo limite. Questo evento provoca lo scadere del timeout sugli altri nodi che, in tal modo, rilevano il malfunzionamento ed eliminano il giocatore in questione della lista dei partecipanti. Il turno, quindi, passer&agrave; automaticamente al giocatore successivo.

![Alt text](./documentation/img/schemaTO_2.png)

##Aspetti implementativi##

Linguaggi usati

lato server:

- python	2.7
- Flask: un microframework che permette la creazione di applicazione web con Python. Flask permette di fornire un servizio   richiamabile attraverso una specifica URL, secondo i metodi http specificati. Di default, i servizi vengono erogati       secondo una politica sequenziale, ovvero non sono richiamabili contemporaneamente. Purtroppo ciò rappresenta un limite    per la nostra implementazione. Ad esempio, all'interno del metodo playCard, richiamato dalla GUI per effettuare la        giocata di una carta, viene inviato in broadcast (incluso a sè stesso) il messaggio playedCard. Il che, in termini        implementativi, si traduce nell'invocazione di un servizio REST. Ma ciò non può avvenire se prima non termina             l'esecuzione del metodo playCard. Per risolvere tale problema abbiamo fatto ricorso al multithreading: ogni servizio      REST viene eseguito in un thread apposito. Flask mette a disposizione un'opzione in virtù della quale viene adottata      proprio questa idea.

lato client:

- javascript
- html
- css

Il sistema si compone di tre elementi principali

- Il Server di Registrar, implementato nel file server.py,  offre i seguenti servizi REST al player_server.

| Metodo | HTTP Request | Descrizione servizio |
|--------|:------------:|---------------------:|
| `get_players()` | GET `/playerList` | Restituisce la lista dei giocatori iscritti al server |
| `get_games()` | GET `/gameList` | Restituisce la partita attiva sul server |
| `create_p(username, porta)` | POST `/createPlayer/<string:username>/`<br/>`<int:porta>` | Crea un nuovo giocatore all'interno del sistema  |
| `create_g(username, n_players)` | POST `/createGame/<string:username>/`<br/>`<int:n_players>` | Restituisce la lista dei giocatori iscritti al server |
| `join_g(username, game_id)` | PUT `/joinGame/<string:username>/`<br/>`<int:game_id>` | Permette ad un player la partecipazione ad una partita esistente se non &egrave; stato gi&agrave; 	raggiunto il numero di giocatori impostato al momento della creazione della partita |

- Il Player server &egrave; implementato nel file player_server.py ed implementa la logica di un singolo giocatore. Offre i seguenti servizi REST.

| Metodo | HTTP Request | Descrizione servizio |
|--------|:------------:|---------------------:|
| `game_status()` | GET `/gameStatus` | Permette di conoscere lo stato del gioco, cio&egrave; se la partita &egrave; iniziata oppure no |
| `doubt_status()` | POST `/doubtStatus` | Permette di controllare se &egrave; stato sollevato un dubbio |
| `create_p()` | GET `/createPlayer/<string:username>` | Richiede la creazione di un nuovo giocatore sul server |
| `gameList()` | GET `/gameList` | Restituisce la lista delle partite |
| `create_g(n_players)` | POST `/createGame/<int:n_players>` | Crea una partita sul server |
| `join_g()` | PUT `/joinGame/<int:id_game>` | Effettua la join in una partita del server |
| `start_g()` | GET `/startGame` | Servizio richiamato dal Server di Registrar per iniziare una nuova partita |
| `rcvCards()` | POST `/receiveCards` | Permette di ricevere le carte da gioco |
| `rcvTable()` | POST `/receiveTable` | permette di ricevere le carte sul banco |
| `rcvDeck()` | POST `/receiveDeck` | Permette di ricevere il mazzo |
| `playedCard(username, year,`<br/>` event, card_id, position)` | PUT `/playedCard/<string:username>/`<br/>`<int:year>/<string:event>`<br/>`/<int:card_id>/<int:position>` | permette di ricevere la giocata di uno dei partecipanti |
| `doubted(username)` | PUT `/doubted/<string:username>` | permette di ricevere un'azione di dubbio sollevata da uno dei giocatori |

La GUI &egrave; implementata nel file gui.html. L'interfaccia grafica per il suo funzionamento ha bisogno dei servizi implementati nel player_server.py ed utilizza tecniche di polling per poter ricevere i cambiamenti di stato di una sessione di gioco. Ad esempio, si effettua polling per monitorare lo stato del turno oppure un possibile stato di dubbio sulla sequenza di carte del banco.

##Valutazioni##
Lo stato dell'arte attuale propone l'alternativa dei web services, la quale, oltre ad HTTP, impiega tecnologie supplementari, quali SOAP, WSDL e UDDI. La nuova tecnologia REST semplifica sensibilmente l'approccio con cui realizzare servizi, pur mantenendo vantaggi tipici quali il supporto all'eterogeneità e l'interoperabilità. Inoltre, REST si presta decisamente meglio nella realizzazione di sistemi distribuiti.

##Conclusioni##
