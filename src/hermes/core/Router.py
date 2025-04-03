from typing import Callable

from hermes.core import KademliaNode
from hermes.core import KBucket
from hermes.core import Node
from hermes.core import Contact

class Router:

    def __init__(self, node: KademliaNode):
        self.node: Node = node

    def get_closest_nonempty_kbucket(self, key: int) -> KBucket:
        """
        Returns the closest nonempty bucket to the given key through XOR distance.
        """
        # Gets all nonempty buckets
        ordered_buckets = sorted([bucket for bucket in self.node.bucket_list
                                  if len(bucket) > 0], key=lambda k: k.Key ^ key)

        if len(ordered_buckets) == 0:
            raise Exception("There is no nonempty bucket. First register a peer.")

        return ordered_buckets[0]

    def get_closest_nodes(self, key: int, bucket: KBucket) -> list[Contact]:
        """
        Sorts the bucket's contacts by XOR distance to the given key.
        """
        return sorted(bucket.contacts, key=lambda c: c.id ^ key)

    def rpc_find_nodes(self, key: int, contact: Contact) -> (list[Contact], Contact, str):
        """
        RPC to find nodes by key
        """
        (new_contacts, timeout_err) = contact.find_node(self.node.our_contact, key)
        #TODO null continuation?
        return new_contacts, None, None

    def get_closer_nodes(self, key: int, node_to_query: Contact,
                         rpc_call: Callable[[int, Contact], (list[Contact], Contact, str)],
                         close_contacts: list[Contact],
                         farther_contacts: list[Contact]):
        """

        """
        contacts, contact_found_by, found_val = rpc_call(key, node_to_query)
        val = found_val
        found_by = contact_found_by

        # peers_nodes: list[Contact] =



