Anno Domini
===========

Anno domini è un gioco di carte: consiste nel collocare le carte dei giocatori in una linea temporale a seconda dell'evento.

Contenuto
=========
336 carte: sul fronte è descritto un evento, e sul retro l’anno in cui è accaduto.

Regole
======
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

Quando il numero di giocatori 'n' (precedentemente stabili dal creatore della partita) viene raggiunto, allora il server notifica l'evento al giocatore che ha creato la partita informandolo che può iniziare la sessione di gioco.
La sequenza di partecipazione ad una partita determina anche i turni della sessione di gioco.

Una volta avviata una sessione di gioco si seguono le regole. 

_Continuare la descrizione del sistema mano a mano che viene implementata la parte distribuita_

Architettura del sistema
========================
* Server centrale di registrazione (scritto in python)
* Giocatori: composti da una parte server (python) e da un client (linguaggi browser)


Messaggi scambiati
==================
| Msg | SentBy | RcvBy | Type | Description |
|-----|:------:|:-----:|:----:|------------:|
| getGames() | a client | the server | unicast | un client desidera ricevere la lista di partite pubbliche disponibili sul server |
| createGames() | a client | the server | unicast | un client intende creare una nuova partita |
| joinGame() | a client | the server | unicast | un client intende partecipare ad una partita |
| startGame() | the server | some clients | broadcast | quando il server capisce che una partita può cominciare (raggiungimento del numero di giocatori prestabilito) allora fa cominciare la partita
| sendCards() | a client | all other clients partecipating in the game | broadcast | il client che ha creato la partita invia agli altri partecipanti il le carte delle loro mani e il mazzo di carte rimanenti del banco |
| playFirstCard() | a client | all other clients partecipating in the game | broadcast | il client che ha creato la partita mette sul tavolo la prima carta del gioco e la comunica a tutti gli altri giocatori |
| playCard() | a client | all other clients partecipating in the game | broadcast | un giocatore gioca una carta dalla propria mano mettendola sul banco |
| sendToken() | a client | next client in the turn | unicast | il giocatore che termina il proprio turno passa il token al giocatore del turno successivo |
| sendDoubt() | a client | all other clients partecipating in the game | broadcast | un giocatore dubita sulla sequenza degli eventi del banco e lo rende noto a tutti gli altri giocatori | 
| zeroCards() | a clent | all other clients partecipating in the game | broadcast | un giocatore comunica a tutti gli altri che non ha più carte in mano e quindi ha vinto la partita |
| createPlayer() | a client | the server | unicast | un client richiede al server la creazione del profilo di giocatore |
| sendGames() | the server | a client | unicast | il server invia al client richiedente la lista di partite disponibili |
| playerCreationResponce() | the server | a client | unicast | il server invia l'esito della creazione di un giocatore |  