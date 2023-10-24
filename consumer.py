"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]

    def run(self):
        """
            Assign a cart to the consumer to use for all orders from carts.
            Then try to acquire all the products form each cart at a time,
            and if there are no available product waits and retry until one
            become available on market. If an operation is to remove items,
            loop untill all items of that type (quantity) are removed.
            When all items have been aquired place the order and print
            all the products after the output format. The print is thread-safe
            protected through an mutual lock beetwen all consumer, defined in
            market class.
        """
        cart_id = self.marketplace.new_cart()
        for cart in self.carts:
            for operation in cart:
                qty = operation["quantity"]
                product = operation["product"]
                if operation["type"] == "add":
                    while qty > 0:
                        ret = self.marketplace.add_to_cart(cart_id, product)
                        if ret is True:
                            qty -= 1
                        else:
                            time.sleep(self.retry_wait_time)
                elif operation["type"] == "remove":
                    while qty > 0:
                        self.marketplace.remove_from_cart(cart_id, product)
                        qty -= 1

            products = self.marketplace.place_order(cart_id)

            # Thread safe print of the cart order protected with shared lock from marketplace
            with self.marketplace.print_order_lock:
                for product in products:
                    print("" + self.name + " bought " + str(product))
