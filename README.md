Lincă Nicolae-Robert
331CC

# Tema 1 - Marketplace

Organizare
-
### **Marketplace**
Are rolul de mediator între thread-urile de tip *Consumer* si *Producer*, clasa oferind o interfață comună între aceste tipuri de thread-uri cu următoarele facilități:

1. Înregistrarea unui producător
2. Punerea în vânzare a unui produs de către un producător înregistrat
3. Solicitarea și obținerea unui coș de cumpărături de către un consumator
4. Adăugarea unui produs în coș dacă acesta se află spre vânzare
5. Eliminarea unui produs din coș și repunerea sa spre vânzare pe piață (market)
6. Finalizarea unei comenzi asociate unui coș de cumpărături

### **Producer**
Un producător are rolul de a se înregistra pe piață, după care acesta poate să înceapă să publice continuu produse pe piață, fiind limitat la un număr maxim de produse ce pot exista în același timp spre vânzare. Va exista mereu un timp necesar realizării unui produs, precum
și un timp de așteptare dacă nu poate să pună pe piată produsul creat.

### **Consumer**
Un consumator mai întâi va procura un coș de cumpărături de la *Marketplace*, după care va putea să adauge un produs existent pe piață sau va aștepta până când acesta devine disponibil, sau de asemnea poate să elimine un produs din coș și să il repună spre vânzare, toate acestea întâmplandu-se pe parcusul unei sesiune de cumpărături. O dată finalizată lista de operații (adaugare/eliminare) din cadrul unei sesiuni de cumpărături,
va plasa comanda, informând *Marketplace* să elibereze coșul pentru ulterioare folosiri
de către acesta și afișând produsele care au rămas la final în coș. Un consumator poate să realizeze mai multe sesiuni de cumpărături, însă iși va păstra același coș de cumpărături.


Implementare
-

Pentru detalii mai ample/specifice de implementare consultați comentariile de cod de la fiecare funcțtie / clasă.

Pentru gestionarea consumatorilor, producătorilor, produselor aflate spre vânzare și a coșurilor de cumpărături, precum și a operațiilor cu acestea, clasa le gestionează sub forma următoarelor structuri:

    # the maximum size of a queue associated with each producer
    self.queue_size_per_producer = queue_size_per_producer

    # list withh all products and their producers_id as tuple
    self.products = []

    # dictionary with how many products can a producer still publish in product list
    self.producer_available_queue_space = {}

    # dictionary with consumers carts, each cart is represented as a list
    self.consumer_carts = {}

* Elemetele listei de produse sunt reținute sub forma de tuple(*product*, *producer_id*) pentru a facilita modificarea ușoară a numărului de produse pe care un producător le mai poate pune pe piață (valoare salvată în dicționarul *producer_available_queue_space*) sau a readăugării unui produs înapoi pe piață dintr-un coș, deoarece coșul fiecărui cumprător (care este gestionat cu ajutorul dicționarului *consumer_carts*) păstrează același al elementelor ca lista de produse
* Id-urile producătorilor sunt identificate prin numere întregi, oferite incremental pe baza numărului de producători deja existenți pe piață în momentul solicitării
* Fiecare cumpărător are asignat un coș unic identificat prin *cart_id*, care este generat pe același principiu ca id-urile producătorilor. Deși un cumpărător poate face mai multe sesiuni de cumpărături, descrise prin adaugare/eliminare de produse în coș, el iși va păstra mereu același *cart_id*
* Pentru selectarea unui produs în momentul în care un consumator dorește să îl adauge în coș, îl va lua pe primul pe care îl găsețe în lista de produse de tipul celui căutat, iar dacă nu va găsi va aștepta un timp până să reîncerce
* În momentul plasării comenzii, coșul de cumpărături al consumatorului este golit
și îi este returnată o lista doar cu elemtele *product* din tuple pentru a le afișa
* Coșurile de cumpărături pentru fiecare consumator sunt inițializate ca liste goale

### **Sincronizarea thread-urilor**
Pentru sincronizarea thread-urilor au fost folosite următoarele *Lock-uri* pentru a elimina problemele de concurență:

    self.register_lock = Lock()         # lock to get and register a producer_id
    self.carts_lock = Lock()            # lock for consumer carts dictionary
    self.products_lock = Lock()         # lock for the list of products
    self.producer_space_lock = Lock()   # lock for the dictionary of free space per producer
    self.print_order_lock = Lock()      # lock to make printing order thread safe in consumer

Aceste *Lock-uri* asigură faptul că nu se pot întâmpla următoarele probleme de concurență (race-condition):

1. Nu pot exista doi producători care să se înregistreze în același timp
2. Nu pot exista doi producători care să publice un produs în același timp, riscând a strica lista de produse
3. Nu pot exista doi cumpărători care să solicite în același timp un coș, riscănd a se oferi două coșuri cu același id, nerespectănd unicitatea și distincția între ele
4. Nu pot exista doi cumpărători care să caute un produs și să âl aduage ân coș în același timp pentru a evita cazul în care ambii ar incerca să modifice lista de produse, putând provoca scenarii de forma: să pună în coș ambii același produs, să strice ordinea produselor în lista putând provoca suprascrieri sau ignorarea unor produse ân momentul ân care alți cumpărători ar căuta un produs să îl aduage în coș, să modifice invalid spațiul disponibil unui producător pentru publicare de produse etc.
5. Nu pot exista doi cumpărători care să scoată din coș un produs și să îl repună în lista de produse putând provoca probleme de concurență ca la 4.
6. Nu pot exista doi cumpărători care să scrie la output lista de produse cumpărate după ce au finalizat comanda, evitând eventuale probleme de suprascrieri

Resurse utilizate
-

* https://docs.python.org/3/tutorial/datastructures.html
* https://docs.python.org/3/howto/logging.html
* https://docs.python.org/3/library/unittest.html#organizing-test-code
* https://ocw.cs.pub.ro/courses/asc/laboratoare/02
* https://ocw.cs.pub.ro/courses/asc/laboratoare/03
* https://ocw.cs.pub.ro/courses/icalc/laboratoare/laborator-05how-to-set-timestamps-on-gmt-utc-on-python-logging
* https://stackoverflow.com/questions/6321160/
* https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler
* https://stackoverflow.com/questions/51477200/how-to-use-logger-to-print-a-list-in-just-one-line-in-python
* https://medium.com/@masnun/infinitely-cycling-through-a-list-in-python-ef37e9df100