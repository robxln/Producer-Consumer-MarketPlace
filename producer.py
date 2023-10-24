"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time
from itertools import cycle

class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.name = kwargs["name"]

    def run(self):
        """
        A producer publish items through an infinit cylic loop on the
        list of products he can produce until the available space on
        market product list for him has been filled, after that wait
        a certain period of time (republish_wait_time) and try again
        to republish the item on which he has failed to publish.
        A producer moves to the next item in tcylyc order of the product
        list only after he has succeed publishing the current item.
        """
        cycle_porducts_list = cycle(self.products)
        producer_id = self.marketplace.register_producer()
        while True:
            iterator = next(cycle_porducts_list)
            product = iterator[0]
            qty = iterator[1]
            produce_time = iterator[2]

            # Wait for the product to be made
            time.sleep(produce_time)

            while qty > 0:
                while self.marketplace.publish(producer_id, product) is False:
                    time.sleep(self.republish_wait_time)
                qty -= 1
