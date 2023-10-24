"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import logging
from threading import Lock
from logging.handlers import RotatingFileHandler
import time
import unittest

logging.basicConfig(
        handlers=[RotatingFileHandler('./marketplace.log', maxBytes=500000, backupCount=20)],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%d-%m-%Y::%H:%M:%S')
logging.Formatter.converter = time.gmtime


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        logging.info('Enter Marketplace constructor with argumetns: queue_size_per_producer = %d',
                     queue_size_per_producer)

        # the maximum size of a queue associated with each producer
        self.queue_size_per_producer = queue_size_per_producer
        # list withh all products and their producers_id as tuple
        self.products = []
        # dictionary with how many products can a producer still publish in product list
        self.producer_available_queue_space = {}
        # dictionary with consumers carts, each cart is represented as a list
        self.consumer_carts = {}

        # Locks
        self.register_lock = Lock()         # lock to get and register a producer_id
        self.carts_lock = Lock()            # lock for consumer carts dictionary
        self.products_lock = Lock()         # lock for the list of products
        self.producer_space_lock = Lock()   # lock for the dictionary of free space per producer
        self.print_order_lock = Lock()      # lock to make printing order thread safe in consumer

        logging.info('Exit Marketplace constructor')

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # Return an unused, unique id for a producer
        # The ids are returned in incremental order, based on the number of
        # producers already registered (i. e. the len of dictionary which maintains
        # available space in product list for each producer).
        # Used lock to guarantee thread-safe when multiple producer threads request
        # an id in similar periods of time.

        logging.info('Enter function.')
        with self.register_lock:
            producer_id = len(self.producer_available_queue_space)
            self.producer_available_queue_space[producer_id] = self.queue_size_per_producer

        logging.info('Exit function. Registered producer with id: %d', producer_id)
        return producer_id



    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        producer_id = int(producer_id)
        ret = False
        logging.info('Enter function with arguments: producer_id = %d, product = %s',
                     producer_id,
                     product)
        # Check if the producers has available free space in product list,
        # and if so add the new tuple of (product, producer_id) and set
        # the return value to True, otherwise return false
        # Used lock to guarantee thread-safe when multiple producer threads request
        # to add new item in product list for no overwriting
        with self.producer_space_lock:
            if self.producer_available_queue_space[producer_id] > 0:
                self.producer_available_queue_space[producer_id] -= 1
                self.products.append((product, producer_id))
                ret = True
                logging.info('Producer %d published the following item: %s',
                             producer_id,
                             str(product))

        logging.info('Exit function.')
        return ret

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        # Return an unused, unique id for a producer
        # The ids are returned in incremental order, based on the number of
        # consumer carts already registered (i. e. the len of dictionary which maintains
        # all on use carts).
        # Used lock to guarantee thread-safe when multiple consumers threads request
        # an id in similar periods of time.
        #! Error check in logs if a cart creation has failed.
        logging.info('Enter function.')
        cart = -1
        with self.carts_lock:
            nr_carts = len(self.consumer_carts)
            cart = nr_carts
            self.consumer_carts[cart] = []

        if cart == -1:
            logging.error('Failed new cart creation!')

        logging.info('Exit function. Created a new cart with the id: %d', cart)
        return cart

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        logging.info('Enter function with arguments: cart_id = %d, product = %s', cart_id, product)
        cart_id = int(cart_id)

        # Search in the list of products first product item equal with the one desired,
        # add the found item to the cart and remove it from products list
        # If an item is found return True, otherwise False
        # Use 2 lock:
        # 1. one to protect the product list in case of item removal upon finding product
        # 2. one to protect the producers available from being modified by different consumers
        # at the same time
        with self.products_lock:
            for item in self.products:
                if item[0] == product:
                    self.consumer_carts[cart_id].append(item)
                    self.products.remove(item)
                    with self.producer_space_lock:
                        self.producer_available_queue_space[item[1]] += 1
                    logging.info('Exit function on True. Found item: %s', str(item[0]))
                    return True

        logging.info('Exit function on False. Item not found: %s', str(product))
        return False


    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        cart_id = int(cart_id)
        logging.info('Enter function with arguments: cart_id = %d, product = %s', cart_id, product)

        # Remove the first product found in the cart like the one specified as argument
        # and remove it from the cart, add it back to the product list and decrease
        # the available space in products list for the prodcut's producer
        # Used 2 lock:
        # 1. first to thread-safe append the item back to the procuts list
        # 2. second to thread-safe decrease the available space for the producer
        # The is no need to thread-protect the consumer's cart as he is the only one
        # who shouldbe able to modify it at some point as each consumer has one cart designated
        #! Check in logs if there a case when we try to remove an invalid product
        found = 0
        for item in self.consumer_carts[cart_id]:
            if item[0] == product:
                self.consumer_carts[cart_id].remove(item)
                with self.products_lock:
                    self.products.append(item)
                with self.producer_space_lock:
                    self.producer_available_queue_space[item[1]] -= 1
                logging.info('Exit function. Item removed successfully')
                found = 1
                break
        if found == 0:
            logging.warning('Exit function. Item not found to remove from cart %d: %s',
                            cart_id,
                            str(product))


    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logging.info('Enter function with arguments: cart_id = %d', cart_id)
        # Convert the cart list from a list of tuples [(product, product_id)] to list of
        # only [product] using list comprehenssions and return it
        products_list = [p[0] for p in self.consumer_carts[cart_id]]

        # Empty the cart for future uses of the same consumer
        self.consumer_carts[cart_id] = []

        logging.info('Exit function. List of product for cart %d are: %s', cart_id, products_list)
        return products_list


#! Unittesting module
class TestMarketplace(unittest.TestCase):
    """
        UnitTest Class for the six methods defined in class Marketplace
    """

    def setUp(self):
        self.marketplace = Marketplace(5)

    def test_register_producer(self):
        """
        Test if producers are registerered with incremental numbers and correct order
        """
        for i in range(20):
            self.assertEqual(self.marketplace.register_producer(), i)

    def test_publish(self):
        """
        Test if a producer cand add products and its available space is modified.
        Check if publish succeded only when there is free space for producer.
        """
        mock_product = Product("produs1", 10)
        producer_id = self.marketplace.register_producer()
        self.assertEqual(self.marketplace.producer_available_queue_space[producer_id],
                         self.marketplace.queue_size_per_producer)
        for i in range(7):
            if self.marketplace.producer_available_queue_space[producer_id] > 0:
                self.assertEqual(self.marketplace.producer_available_queue_space[producer_id],
                                 self.marketplace.queue_size_per_producer - i)
                self.assertTrue(self.marketplace.publish(producer_id, mock_product))
                self.assertEqual(self.marketplace.producer_available_queue_space[producer_id],
                                 self.marketplace.queue_size_per_producer - i - 1)
            else:
                self.assertFalse(self.marketplace.publish(producer_id, mock_product))
                self.assertEqual(self.marketplace.producer_available_queue_space[producer_id], 0)

    def test_new_cart(self):
        """
        Test if carts are registerered with incremental numbers and correct order
        """
        for i in range(20):
            self.assertEqual(self.marketplace.new_cart(), i)

    def test_add_to_cart(self):
        """
        Test add_to_cart functionality on mock up flow
        publish 5 products, add those 5 to cart with success
        and try to add 5 more and fail.
        """
        mock_product = Product("produs1", 10)
        producer_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        self.marketplace.products = []
        for _ in range(5):
            self.marketplace.publish(producer_id, mock_product)

        for _ in range(5):
            self.assertTrue(self.marketplace.add_to_cart(cart_id, mock_product))
            self.assertTrue((mock_product, producer_id) in self.marketplace.consumer_carts[cart_id])

        for _ in range(5):
            self.assertFalse(self.marketplace.add_to_cart(cart_id, mock_product))

    def test_remove_from_cart(self):
        """
        Test add_to_cart functionality on mock up flow
        publish 5 products, add those 5 to cart with success
        and try to add 1 more and fail, then remove 2 item and readd with succes
        follow by a last failed one.
        """
        mock_product = Product("produs1", 10)
        producer_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        self.marketplace.products = []
        for _ in range(5):
            self.marketplace.publish(producer_id, mock_product)

        for _ in range(5):
            self.assertTrue(self.marketplace.add_to_cart(cart_id, mock_product))
            self.assertTrue((mock_product, producer_id) in self.marketplace.consumer_carts[cart_id])

        # Check that there are no more items in products list
        self.assertFalse(self.marketplace.add_to_cart(cart_id, mock_product))

        # Remove 2 itmes
        self.marketplace.remove_from_cart(cart_id, mock_product)
        self.marketplace.remove_from_cart(cart_id, mock_product)
        self.assertTrue((mock_product, producer_id) in self.marketplace.products)

        # Readd the 2 items
        for _ in range(2):
            self.assertTrue(self.marketplace.add_to_cart(cart_id, mock_product))
            self.assertTrue((mock_product, producer_id) in self.marketplace.consumer_carts[cart_id])

        # Check that there are no more items in products list
        self.assertFalse(self.marketplace.add_to_cart(cart_id, mock_product))

    def test_place_order(self):
        """
        Check if 5 mock porudcts have been added successfully when placing final order.
        """
        mock_product = Product("produs1", 10)
        producer_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        self.marketplace.products = []
        check_list = []

        for _ in range(5):
            self.marketplace.publish(producer_id, mock_product)
            check_list.append(mock_product)

        for _ in range(5):
            self.assertTrue(self.marketplace.add_to_cart(cart_id, mock_product))
            self.assertTrue((mock_product, producer_id) in self.marketplace.consumer_carts[cart_id])

        self.assertEqual(check_list, self.marketplace.place_order(cart_id))
