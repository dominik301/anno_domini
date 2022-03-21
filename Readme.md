Anno Domini
===========

*Stefano Bettinelli*, *Roberto De Santis*, *Vincenzo Gambale*


### Implementierung eines verteilten Spiels auf der Grundlage eines RESTful-Architekturmodells

## Inhaltsverzeichnis ##

- [Zusammenfassung](#zusammenfassung)
- [Einführung](#einführung)  
- [Gestalterische Aspekte](#gestalterische-aspekte)  
	- [Interaktion der Systemkomponenten](#interaktion-der-systemkomponenten)
	- [Fehlertoleranz](#fehlertoleranz)
- [Aspekte der Umsetzung](#aspekte-der-umsetzung)  
- [Beurteilungen](#beurteilungen)  
- [Schlussfolgerungen](#schlussfolgerungen)

## Zusammenfassung ##
Das Projekt Anno Domini wurde durch das gleichnamige Kartenspiel inspiriert, das die für Domino typische Grundidee der Abfolge von Elementen mit der chronologischen Abfolge bestimmter historischer Ereignisse verbindet.

Das Spiel hat keine Pivot-Elemente, d. h. spezifische Rollen, die von einer einzelnen Komponente des betrachteten Spiels gespielt werden (wie z. B. der Dealer beim Blackjack). Dies macht Anno Domini offensichtlich besonders anschlussfähig an die für verteilte Systeme charakteristischen Paradigmen.

In diesem Bericht beschreiben wir, wie ein solches verteiltes System konzipiert und entworfen wurde, wobei wir von der Möglichkeit ausgehen, dass es nur zu crashartigen Ausfällen der Prozesse, d. h. der am Spiel beteiligten Spieler, kommt. Das System wurde auf der Grundlage des REST-Architekturmodells implementiert.

## Einführung ##
Anno Domini erfordert eine Mindestanzahl von vier Spielern, die jeweils sieben Karten erhalten. Jede Karte stellt ein bestimmtes historisches Ereignis dar, das für die Spieler sichtbar ist, auch wenn es verdeckt ist. Wenn die Karte aufgedeckt wird, wird das entsprechende Jahr angezeigt. Wie bereits erwähnt, besteht das Ziel des Spiels darin, die historischen Ereignisse in eine chronologische Reihenfolge zu bringen, von den am weitesten zurückliegenden bis zu den jüngsten, und der Spieler, der keine Karten auf der Hand hat, gewinnt.

Zu Beginn befindet sich nur eine verdeckte Karte im Stapel. Im Laufe des Spiels wird die Abfolge auf dem Spielbrett mit neuen Karten angereichert, die von den Spielern entsprechend ihrer Spielzüge abgelegt werden.

Jeder Spielteilnehmer kann zwischen zwei verschiedenen Arten von Einsätzen wählen, je nachdem, ob er die Reihenfolge der bis zu diesem Zeitpunkt auf der Bank abgelegten Karten für richtig oder falsch hält. Wenn er glaubt, dass sie richtig ist, kann er die nächste Karte ausspielen, indem er sie aus seiner Hand auswählt und in der Reihenfolge in der Bank ablegt. Glaubt er hingegen, dass die Reihenfolge der Gemeinschaftskarten falsch ist, kann er sie anzweifeln: Dies führt dazu, dass die Daten der historischen Ereignisse auf der Bank offengelegt werden. Wenn die Reihenfolge falsch ist, muss der vorherige Spieler drei Karten ziehen und der Spieler, der gezweifelt hat, darf seine eigene Karte ausspielen. Ist die Reihenfolge hingegen richtig, muss der zweifelnde Spieler zwei Karten ziehen und der nächste Spieler ist an der Reihe.

Das Spiel endet, sobald ein Spieler keine Karten mehr auf der Hand hat, vorausgesetzt, die Reihenfolge auf dem Tisch ist korrekt. Wenn einem Spieler die Karten ausgehen, aber die Reihenfolge nicht stimmt, muss er zwei Karten vom Stapel ziehen; das Spiel wird dann mit dem nächsten Spieler fortgesetzt.

Die REST-Technologie wurde ursprünglich entwickelt, um es Webdiensten zu ermöglichen, ihre eigenen APIs zu veröffentlichen, wobei HTTP als Kernprotokoll beibehalten wurde. Erst später wird erkannt, dass sie auch für die Implementierung verteilter Systeme verwendet werden kann. Wir haben uns für REST entschieden, um mit dieser neuen Art der Erstellung verteilter Systeme zu experimentieren.

## Gestalterische Aspekte ##
Das erste Problem bei der Einrichtung eines verteilten Systems besteht darin, sicherzustellen, dass jeder Knoten über die Struktur des Systems, zu dem er gehört, informiert ist. Der Einfachheit halber wurde ein Registrar Server verwendet, der für die Registrierung von Knoten zuständig ist. So melden sich die verschiedenen Komponenten des verteilten Systems beim Server als Spieler an und nehmen dann am Spiel teil. Sobald die erforderliche Anzahl von Spielern erreicht ist, kann das Spiel beginnen. Von diesem Moment an ist der Registrar Server nicht mehr notwendig: Das neu geschaffene verteilte System ist in der Lage, sich selbst ohne die Hilfe des Registrars zu verwalten.

Die Vorbereitungsphase für den Start des Spiels ist wie folgt aufgebaut: Die Spieler registrieren sich beim Server, indem sie einen eindeutigen Benutzernamen wählen. Einer der potenziellen Mitspieler erstellt ein neues Spiel und gibt die gewünschte Teilnehmerzahl an: Wir bezeichnen diesen Spieler als Ersteller. Die anderen Knotenpunkte melden sich beim Registrar Server für das Spiel an: Sobald die gewünschte Anzahl von Spielern erreicht ist, kann das Spiel beginnen. Der Server informiert dann alle registrierten Spieler des Spiels mit einer Nachricht: Von nun an wird der Registrar nicht mehr verwendet. Theoretisch wäre ein verteilter Algorithmus erforderlich, um die erste Runde des Spiels zu entscheiden, ähnlich dem, der für die Wahl des Anführers verwendet wird. In Wirklichkeit ist ein solcher Schritt gar nicht nötig, da davon ausgegangen werden kann, dass die erste Runde dem Ersteller des Spiels gehört.

Zu diesem Zeitpunkt sind die Knotenpunkte in der Lage, das Spiel autonom zu verwalten, während es sich weiterentwickelt. Wenn ein Spieler ein Spiel machen muss (egal ob es sich um einen Zweifel oder ein Kartenspiel handelt), sendet er eine Nachricht an alle anderen. Auf diese Weise können alle Spielteilnehmer ihre Spielressourcen auf dem neuesten Stand halten, während sie verteilt werden.

Angesichts der Merkmale des Szenarios ist die abstrakte Architektur des verteilten Systems die eines Rings. Die Spielzüge sowie die Spielressourcen, wie z. B. der Kartenstapel oder die Karten auf dem Spieltisch, werden auf verteilte Weise verwaltet. Das bedeutet, dass diese Informationen auf mehreren Knoten repliziert werden, so dass eventuelle Prozessausfälle toleriert werden können, ohne dass die Fortsetzung des Spiels beeinträchtigt wird.

Wie bereits erwähnt, lässt sich das Spiel aufgrund seiner Eigenschaften problemlos mit einem verteilten System umsetzen. Das Fehlen einer zentralen Steuerungskomponente und die Unabhängigkeit der Knotenpunkte sind, wenn man so will, ein gemeinsamer Nenner für das Spiel und die Welt der verteilten Systeme.

Die Wahl der Technologie für unser verteiltes System fiel auf REST. Beim gegenwärtigen Stand der Technik scheint es sehr stark genutzt zu werden: Es genügt beispielsweise, einige Referenzpunkte in diesem Bereich zu betrachten, wie Amazon und Google, die dieses Architekturmodell derzeit anwenden.

### Interaktion der Systemkomponenten ###
Schauen wir uns nun an, wie wir die Kommunikation zwischen den verschiedenen Elementen, aus denen das System besteht, geplant haben. Insbesondere werden die Phasen Anmeldung, Vorbereitung, Spiel und Zweifel beschrieben.

Bevor das Spiel beginnt, muss sich der Spieler beim Registrar Server anmelden. Die Registrierung erfolgt durch Senden einer createPlayer-Nachricht an den Registrar-Server. Nach der Registrierung kann der Spieler entweder ein neues Spiel erstellen, indem er die gewünschte Anzahl von Spielern angibt, oder einem bestehenden Spiel beitreten (wenn es zuvor von einem anderen Spieler erstellt wurde), indem er die Nachricht joinGame verwendet. Sobald ein Spiel erstellt wurde, aktualisiert der Server alle registrierten Benutzer durch Senden der Nachricht rcvGameList.

![Alt text](./documentation/img/Registrazione.png)

Sobald die vom Ersteller geforderte Anzahl von Spielern erreicht ist, kann kein anderer Benutzer mehr dem betreffenden Spiel beitreten: Der Server sendet die startGame-Nachricht mit der Liste der Spieler an alle Teilnehmer, um sie über den Beginn des Spiels zu informieren. Wie bereits oben erwähnt, müsste ein ähnlicher Algorithmus wie bei der Wahl des Anführers verwendet werden, um zu bestimmen, welcher der Teilnehmer an der Reihe ist. Da es nur einen Schöpfer gibt, haben wir der Einfachheit halber angenommen, dass dieser der erste der Hand ist. Wenn der Ersteller also die startGame-Nachricht erhält, teilt er im Gegensatz zu den anderen Spielern die Karten über die rcvCards-Nachricht aus und gibt dann die Tischkonfiguration (die anfänglich nur aus einer Karte besteht) über die rcvTable-Nachricht und den verbleibenden Stapel (rcvDeck-Nachricht) aus. Wir möchten darauf hinweisen, dass die Verteilung der Karten und des Tisches zwar ein grundlegender Vorgang für das Spiel ist, das Versenden des Decks an alle jedoch aus Gründen der Fehlertoleranz erfolgt. Wäre dies nicht der Fall, würde der Ausfall des einzigen Knotens, der die Karten hält, die anderen Teilnehmer daran hindern, das Spiel fortzusetzen. Auf jeden Fall wirkt sich diese Wahl auch positiv auf die Leistung aus. In jedem Fall wirkt sich diese Wahl auch positiv auf die Leistung aus, da keine zusätzlichen Nachrichten für die Übermittlung der gezogenen Karte aus dem Stapel (die dann zentralisiert werden würde) verwendet werden müssen.

![Alt text](./documentation/img/Preparazione.png)

Wenn ein Spieler eine Karte ausspielt, wird eine playedCard-Nachricht an alle Spieler (einschließlich ihm selbst) gesendet.

![Alt text](./documentation/img/PlayCard.png)

Ebenso wird bei Zweifeln eines Spielers eine Zweifelnachricht gesendet. Alle Knoten, die diese Nachricht erhalten, führen die Zweifelberechnung lokal durch und prüfen, ob der Zweifel begründet war oder nicht: Auf diese Weise bestimmt jeder Knoten, welcher Spieler die Strafkarten ziehen muss, und vergibt den Zug für das nächste Spiel. Dieser Vorgang hält das System in einem konsistenten Zustand (z.B. indem die Zähler für die Anzahl der Karten der verschiedenen Spieler auf jedem Knotenpunkt aktualisiert werden).

![Alt text](./documentation/img/Dubbio.png)

## Fehlertoleranz
Die Art von Fehlern, die unser System toleriert, ist nur der Absturz und beschränkt sich ausschließlich auf den Moment des Spielbeginns. Daher werden Fehler, die auf dem Registrar Server bestehen, nicht behandelt, da davon ausgegangen wird, dass dieser ohne Komplikationen funktioniert. Außerdem wird davon ausgegangen, dass das zugrunde liegende Netz zuverlässig ist: Nachrichten werden korrekt und innerhalb einer angemessenen Zeit gesendet und empfangen.

Folglich besteht die Lösung des Problems der Fehlertoleranz hauptsächlich darin, die Knoten zu identifizieren, die abstürzen, und dann eine bestimmte Strategie zu verfolgen, die es anderen Spielern ermöglicht, weiterzuspielen. Wir haben uns darauf geeinigt, dass ein Spiel fortgesetzt werden kann, solange mindestens vier Spieler anwesend sind.

Wir haben Lösungen vermieden, bei denen die einzelnen Knoten Liveness-Nachrichten austauschen, was die Komplexität des Betriebs der einzelnen Knoten erhöht und die Anzahl der im Netz zirkulierenden Nachrichten vergrößert hätte. Stattdessen verwendet unser Ansatz einen Timer, der auf jedem Knotenpunkt vorhanden ist und zu Beginn des Spiels gestartet wird und neu gestartet wird, wenn die Runde vorbei ist. Die vom Timer gesetzte Frist legt die Zeit fest, innerhalb derer der Spieler, der am Zug ist, den Spielzug ausführen muss. Da Unterlassungsfehler nicht toleriert werden (z. B. wenn der Spieler, der an der Reihe ist, nicht spielt), haben wir angenommen, dass jeder Spielzug vor Ablauf des Timers stattfindet. Da wir auch keine netzbedingten Ausfälle tolerieren, wird die Nachricht über die Wette von den anderen Teilnehmern korrekt empfangen. Zusammenfassend lässt sich sagen, dass der Spieler, von dem ein Spiel erwartet wurde, abgestürzt ist, wenn der Timer an einem bestimmten Knotenpunkt abläuft. Natürlich wissen alle Knotenpunkte zu jeder Zeit, welcher Spieler am Zug ist.

Die im Falle eines Absturzes angewandte Strategie ermöglicht es den verbleibenden Knoten, das Spiel fortzusetzen. Im Moment gehen wir davon aus, dass alle Knoten über synchronisierte Zeitgeber verfügen (was in der Realität nicht der Fall ist). Wenn der Timer abläuft, streichen alle Knoten den erwarteten Spieler aus ihrer Teilnehmerliste. Diese Entfernung ist jedoch für den Verlauf der Runde transparent: Unmittelbar nach der Entdeckung des Absturzes wird die Runde an den nächsten Spieler vergeben. Das verteilte System leidet also nicht unter den negativen Auswirkungen des Absturzes, außer dass die Karten, die der ausgeschiedene Knoten vor dem Auftreten der Störung in der Hand hatte, verloren gehen. Es ist wichtig zu beachten, dass der Absturz eines Knotens erst dann erkannt wird, wenn ihm der Zug zugewiesen wird. Wenn ein Knoten abstürzt, obwohl er nicht im Besitz des Tokens ist, hat das Fehlen einer sofortigen Erkennung durch andere Knoten nicht die geringste Auswirkung auf den Betrieb des Systems. Erst wenn dieser Knoten an der Reihe ist, wird die entsprechende Zeitschaltuhr aktiviert, die dann abläuft: Durch das Versäumnis, zu spielen, können die anderen Knoten im System den Absturz erkennen. Natürlich wird das Spiel unterbrochen, wenn die Anzahl der Knoten aufgrund eines oder mehrerer Abstürze weniger als das zulässige Minimum (4) beträgt.

Wie bereits erwähnt, sind die Timer, die die Erkennung einer möglichen Störung des diensthabenden Spielers ermöglichen, in der Realität nicht synchronisiert. Denn selbst wenn das Netz zuverlässig ist, kann nicht davon ausgegangen werden, dass eine Nachricht über ein abgeschlossenes Spiel gleichzeitig bei den verschiedenen Empfängern eintrifft. Folglich beginnt der Timer für den nächsten diensthabenden Spieler an den verschiedenen Knotenpunkten zu leicht unterschiedlichen Zeiten. Wenn aber in einem solchen Szenario der Spieler, der den Token besitzt, die Wette abgibt, wenn das Zeitlimit abläuft, besteht das Risiko, dass einige Knotenpunkte die Wette korrekt annehmen, während bei anderen der Timer bereits abgelaufen ist, was zu einer Inkonsistenz des Systems führt: Jemand hat einen Absturz festgestellt, der nicht eingetreten ist. Um dieses Problem zu lösen, haben wir einen zusätzlichen Timer eingeführt, der nur für den diensthabenden Spieler aktiv ist und eine kürzere Frist hat (z. B. 5 Sekunden), nach der ein Einsatz nicht mehr zulässig ist. Auf diese Weise ermöglicht die Zeitdifferenz zwischen dem Timer, der sich auf die Möglichkeit des Spielens des diensthabenden Spielers bezieht, und dem Timer, der sich auf die Absturzerkennung bezieht, aufgrund des korrekten Funktionierens des Netzes, dass die Nachrichten vor einer möglichen fiktiven Absturzerkennung ankommen.

Schauen wir uns nun genauer an, wie der Absturz-Timeout innerhalb des Knotens in zwei verschiedenen Fällen funktioniert:

- Der Server teilt den Spielern mit, dass sie das Spiel beginnen können: Sie starten den Timer für die Absturzerkennung. Der Spieler, der an der Reihe ist, führt innerhalb der von seinem Spieltimer vorgegebenen Zeit ein Spiel aus (das kann eine Zweifelsaktion oder das Ausspielen einer Karte aus seiner Hand sein) und sendet eine Nachricht an alle anderen Teilnehmer, dass er dies getan hat. Nach Erhalt dieser Nachricht setzen die anderen Spieler ihrerseits das Timeout zurück; der Zug wird automatisch an jedem Knotenpunkt berechnet und von einem der Spieler übernommen (demjenigen, der auf denjenigen folgt, der das letzte Spiel gemacht hat).

![Alt text](./documentation/img/schemaTO_1.png)

- Der Server sendet den Befehl start_game an die Knotenpunkte, die den Timer starten. Weil er abgestürzt ist, spielt Spieler_0 nicht innerhalb des Zeitlimits. Dieses Ereignis führt dazu, dass die Zeitüberschreitung auf den anderen Knotenpunkten abläuft, die daraufhin die Störung erkennen und diesen Spieler aus der Teilnehmerliste entfernen. Danach ist automatisch der nächste Spieler an der Reihe.

![Alt text](./documentation/img/schemaTO_2.png)

## Aspekte der Umsetzung ##

Verwendete Sprachen

Server-seitig:

- python	2.7
- Flask: ein Microframework, das die Erstellung von Webanwendungen mit Python ermöglicht. Flask ermöglicht es Ihnen, einen Dienst bereitzustellen, der über eine bestimmte URL gemäß den angegebenen http-Methoden aufgerufen werden kann. Standardmäßig werden die Dienste nach einem sequentiellen Verfahren bereitgestellt, d. h. sie können nicht gleichzeitig aufgerufen werden. Leider stellt dies eine Einschränkung für unsere Implementierung dar. So wird beispielsweise in der Methode playCard, die von der grafischen Benutzeroberfläche aus aufgerufen wird, um eine Karte abzuspielen, die Nachricht playedCard gesendet (einschließlich ihrer selbst). In der Umsetzung bedeutet dies den Aufruf eines REST-Dienstes. Dies ist jedoch nicht möglich, wenn die Ausführung der Methode playedCard nicht vorher beendet wird. Um dieses Problem zu lösen, haben wir auf Multithreading zurückgegriffen: Jeder REST-Dienst wird in einem eigenen Thread ausgeführt. Flask bietet eine Option, die genau diese Idee aufgreift.

Client-seitig:

- javascript
- html
- css

Das System besteht aus drei Hauptelementen

- Der Registrar Server, der in der Datei server.py implementiert ist, bietet dem player_server die folgenden REST-Dienste.

| Metodo | HTTP Request | Descrizione servizio |
|--------|:------------:|---------------------:|
| `get_players()` | GET `/playerList` | Restituisce la lista dei giocatori iscritti al server |
| `get_games()` | GET `/gameList` | Restituisce la partita attiva sul server |
| `create_p(username, porta)` | POST `/createPlayer/<string:username>/`<br/>`<int:porta>` | Crea un nuovo giocatore all'interno del sistema  |
| `create_g(username, n_players)` | POST `/createGame/<string:username>/`<br/>`<int:n_players>` | Restituisce la lista dei giocatori iscritti al server |
| `join_g(username, game_id)` | PUT `/joinGame/<string:username>/`<br/>`<int:game_id>` | Permette ad un player la partecipazione ad una partita esistente se non &egrave; stato gi&agrave; 	raggiunto il numero di giocatori impostato al momento della creazione della partita |

- Der Spielerserver ist in der Datei player_server.py implementiert und implementiert die Logik eines einzelnen Spielers. Sie bietet die folgenden REST-Dienste.

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

Die grafische Benutzeroberfläche ist in der Datei gui.html implementiert. Die GUI benötigt die in player_server.py implementierten Dienste und verwendet Polling-Techniken, um die Statusänderungen einer Spielsitzung zu erhalten. Die Abfrage wird zum Beispiel verwendet, um den Stand der Runde oder einen möglichen zweifelhaften Stand der Kartenfolge des Dealers zu überwachen.

## Beurteilungen ##
Der derzeitige Stand der Technik schlägt die Alternative der Webdienste vor, die neben HTTP zusätzliche Technologien wie SOAP, WSDL und UDDI verwenden. Die neue REST-Technologie vereinfacht den Ansatz, mit dem Dienste realisiert werden, erheblich, wobei typische Vorteile wie die Unterstützung von Heterogenität und Interoperabilität erhalten bleiben. Außerdem eignet sich REST viel besser für die Implementierung von verteilten Systemen.

## Schlussfolgerungen ##
Wir schließen diesen Bericht mit der Beschreibung einiger möglicher Verbesserungen, die an dem System vorgenommen werden können, und erörtern mögliche zukünftige Entwicklungen.
Die erste Verbesserung betrifft die grafische Schnittstelle für die Abrufe. Das Polling könnte durch HTML5-Websockets ersetzt werden, die Vollduplex-Kommunikationskanäle über eine einzige TCP-Verbindung bereitstellen.
Eine der zukünftigen Entwicklungen könnte die Handhabung mehrerer gleichzeitiger Spiele durch den Server sein, da derzeit nur ein Spiel gehandhabt wird.
