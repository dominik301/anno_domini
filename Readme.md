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
Il progetto, realizzato dagli studenti Vincenzo Gambale, Stefano Bettinelli e Roberto De Santis è l'implementazione di un gioco da tavolo (Anno Domini) con tecnologie Web che si basano su un modello architetturale di tipo RESTful.

Intrisecamente il Web si basa su un'interazione di tipo Client-Server, mentre l'obiettivo principale del progetto (in linea con il corso di Sistemi Distribuiti) è stato quello realizzare un'implementazione distribuita del gioco. La gestione e l'esecuzione di una partita avvengono in modo distribuito, senza il supporto di alcun server centrale, fatta eccezione di una prima fase di registrazione, necessaria per raccogliere la partecipazione del giusto numero di persone ad una sessione di gioco.

Anno domini è un gioco di carte: consiste nel collocare le carte dei giocatori in una linea temporale a seconda dell'evento.

##Introduzione
<a name="sommario"/>
Il progetto, realizzato dagli studenti Vincenzo Gambale, Stefano Bettinelli e Roberto De Santis è l'implementazione di un gioco da tavolo (Anno Domini) con tecnologie Web che si basano su un modello architetturale di tipo RESTful.

Intrisecamente il Web si basa su un'interazione di tipo Client-Server, mentre l'obiettivo principale del progetto (in linea con il corso di Sistemi Distribuiti) è stato quello realizzare un'implementazione distribuita del gioco. La gestione e l'esecuzione di una partita avvengono in modo distribuito, senza il supporto di alcun server centrale, fatta eccezione di una prima fase di registrazione, necessaria per raccogliere la partecipazione del giusto numero di persone ad una sessione di gioco.

####Regole del gioco
Anno domini, come detto in precedenza, è un gioco di carte e consiste nel collocare le carte dei giocatori in una linea temporale in accordo all'evento storico scritto sulle carte dei giocatori.

Sono a disposizione un totale di 336 carte: sul fronte è descritto un evento, e sul retro l’anno in cui è accaduto.

* Ogni giocatore inizia con 7 carte in mano.
* Il gioco termina quando uno dei giocatori rimane senza carte in mano e si considera quindi il vincitore
* L'obiettivo del gioco è di posizionare in ordine cronologico le carte di eventi partendo da una carta di riferimento iniziale posta sul tavolo da gioco.
* Ogni turno di un giocatore è composto da due fasi: la prima fase è opzionale e permette di dubitare della sequenza di carte sul tavolo, secondoa invece è obbligatoria e costringe il giocate a posizionare una delle carte della sua mano sulla linea temporale del tavolo. 
* Nel caso in cui un giocatore dubita della sequenza ed ha ragione il giocatore del turno precedente prende 3 carte nella sua mano pescandole dal mazzo, altrimenti il giocatore che ha dubitato (erroneamente) prende 2 carte dal mazzo.
* Dopo un evento di dubbio vengono rivelate le date sulle carte presenti sul tavolo. Il tavolo viene quindi ripulito ed inizializzato con una nuova carta di riferimento. Il giocatore che ha dubitato correttamente inizia il turno, altrimenti inizia il giocatore successivo.
* Se un giocatore nel proprio turno ha una sola carta in mano e anche sul tavolo da gioco è presente solo una carta di riferimento, allora deve pescare una carta dal mazzo e posizionare le due le carte in mano sul tavolo; il giocatore nel turno successivo è obbligato a dubitare della sequenza (altrimenti il giocatore che è rimasto senza carte vince banalmente la partita).

Funzionamento generale del sistema
==================================
Un server di registrazione permette sia la creazione che la partecipazione a partite da parte dei giocatori (che devono esserci precedentemente iscritti).

Il server gestisce più di una partita e ogni giocatore può iscriversi ad una sola partita.

Dopo che un giocare ha creato una partita, gli altri giocatori possono prendere parte a quella partita iscrivendosi ad essa.
La sequenza di partecipazione ad una partita determina anche i turni della sessione di gioco.
Quando il numero di giocatori 'n' (precedentemente stabili dal creatore della partita) viene raggiunto, allora il server invia a tutti i partecipanti della partita una lista contenente username e ip di tutti i giocatori per notificare l'inizio della partita.

Il creatore della partita,dopo aver ricevuto la lista dei giocatori,crea il mazzo,distribuisce 7 carte ad ogni giocatore,mette una carta sul banco per iniziare il gioco,invia il banco in broadcast e infine fa il broadcast del mazzo.

Una volta avviata una sessione di gioco si seguono le regole. 

Architettura del sistema
========================
* Server centrale di registrazione (scritto in python)
* Giocatori: composti da una parte server (python) e da un client (linguaggi browser)


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
