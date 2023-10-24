# Producer-Consumer Marketplace

Organization
-
### **Marketplace**
Acts as a mediator between *Consumer* and *Producer* threads, offering a common interface for these types of threads with the following functionalities:

1. Registering a producer
2. Placing a product for sale by a registered producer
3. Requesting and obtaining a shopping cart by a consumer
4. Adding a product to the cart if it is available for sale
5. Removing a product from the cart and putting it back on the market
6. Finalizing an order associated with a shopping cart

### **Producer**
A producer's role is to register in the market. After registration, they can continuously publish products in the market but are limited to a maximum number of products that can be available for sale at the same time. There is always a required time for product creation, as well as a waiting time if the producer cannot put the created product on the market.

### **Consumer**
A consumer first procures a shopping cart from the *Marketplace*. Then, they can add an existing product from the market or wait for it to become available. They can also remove a product from the cart and put it back on sale. All these actions take place during a shopping session. Once the list of shopping session operations (add/remove) is completed, they place an order, instructing the *Marketplace* to release the cart for future use and displaying the products left in the cart. A consumer can perform multiple shopping sessions, but they will keep the same shopping cart.

Implementation
-
For more detailed and specific implementation information, refer to the code comments for each function/class.

To manage consumers, producers, products available for sale, and operations with them, the class manages the following structures:

    # the maximum size of a queue associated with each producer
    self.queue_size_per_producer = queue_size_per_producer

    # list with all products and their producers_id as a tuple
    self.products = []

    # dictionary with how many products a producer can still publish in the product list
    self.producer_available_queue_space = {}

    # dictionary with consumer carts, each cart is represented as a list
    self.consumer_carts = {}

The products' list elements are stored as tuples (*product*, *producer_id*) to facilitate easy modification of the number of products a producer can put on the market (value saved in the dictionary *producer_available_queue_space*) or to re-add a product back to the market from a cart. The consumer's cart (managed through the *consumer_carts* dictionary) retains the same elements as the product list.

Producer IDs are identified by integers, assigned incrementally based on the number of existing producers in the market at the time of registration. Each consumer is assigned a unique cart identified by a *cart_id*, generated on the same principle as producer IDs. While a consumer can have multiple shopping sessions (described by adding/removing products in the cart), they will always keep the same *cart_id*.

When a consumer wants to select a product, they will take the first one they find in the product list that matches their search criteria. If they don't find it, they will wait for a while before trying again.

Upon placing an order, the consumer's shopping cart is emptied, and a list containing only the *product* elements from the tuples is returned for display. The shopping carts for each consumer are initially initialized as empty lists.

### **Thread Synchronization**
The following *Locks* have been used for thread synchronization to eliminate concurrency issues:

    self.register_lock = Lock()         # lock to get and register a producer_id
    self.carts_lock = Lock()            # lock for consumer carts dictionary
    self.products_lock = Lock()         # lock for the list of products
    self.producer_space_lock = Lock()   # lock for the dictionary of free space per producer
    self.print_order_lock = Lock()      # lock to make printing order thread safe in consumer

These *Locks* ensure that the following concurrency issues (race conditions) do not occur:

1. Two producers cannot register at the same time.
2. Two producers cannot publish a product at the same time, avoiding the risk of disrupting the product list.
3. Two consumers cannot request a cart at the same time, ensuring that two carts with the same ID are not offered, maintaining their uniqueness and distinction.
4. Two consumers cannot search for a product and add it to their cart at the same time to avoid modifying the product list simultaneously, preventing scenarios where both would try to add the same product to their cart, potentially disrupting the product order, causing overwrites, or ignoring some products when other consumers search for them. They may try to add a product, which could result in invalid producer space for product publishing, etc.
5. Two consumers cannot remove a product from their cart and put it back on the product list, avoiding concurrency issues as in 4.
6. Two consumers cannot write the list of purchased products to the output after completing an order, preventing potential overwrites.

Resources Used
-
* [Python Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
* [Python Logging](https://docs.python.org/3/howto/logging.html)
* [Python Unittest](https://docs.python.org/3/library/unittest.html#organizing-test-code)
* [OCW - Advanced Systems Programming Course](https://ocw.cs.pub.ro/courses/asc/laboratoare/02)
* [OCW - Advanced Systems Programming Course](https://ocw.cs.pub.ro/courses/asc/laboratoare/03)
* [OCW - Introduction to Algorithms Course](https://ocw.cs.pub.ro/courses/icalc/laboratoare/laborator-05how-to-set-timestamps-on-gmt-utc-on-python-logging)
* [Stack Overflow](https://stackoverflow.com/questions/6321160/)
* [Stack Overflow](https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler)
* [Stack Overflow](https://stackoverflow.com/questions/51477200/how-to-use-logger-to-print-a-list-in-just-one-line-in-python)
* [Medium - Cycling Through a List in Python](https://medium.com/@masnun/infinitely-cycling-through-a-list-in-python-ef37e9df100)
