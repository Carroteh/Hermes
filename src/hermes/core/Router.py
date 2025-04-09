from typing import Callable

import asyncio

#from hermes.core import KademliaNode
from hermes.core import KBucket
from hermes.core import Node
from hermes.core import Contact
from hermes.core import Support
#from hermes.core import DHT

class Router:

    def __init__(self, node: Node):
        self.node: Node = node
        #self.dht: DHT = None
        self.lock = asyncio.Lock()

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

    def rpc_find_value(self):
        #TODO
        pass

    async def get_closer_nodes(self, key: int, node_to_query: Contact,
                         rpc_call: Callable[[int, Contact], tuple[list[Contact], Contact, str]],
                         close_contacts: list[Contact],
                         farther_contacts: list[Contact]) -> tuple[bool, list[Contact], Contact, str | None]:
        """
        Exclude ourselves and peers we are contacting, to get a unique list of peers
        """
        contacts, contact_found_by, found_val = rpc_call(key, node_to_query)
        val = found_val
        found_by = contact_found_by

        peers_nodes: list[Contact] = [
            c for c in contacts if
            c.id != self.node.our_contact.id and
            c.id != node_to_query.id and
            c not in close_contacts and
            c not in farther_contacts
        ]

        nearest_node_distance = node_to_query.id ^ key

        # Update contact lists
        async with self.lock:
            for peer in peers_nodes:
                d = peer.id ^ key
                target_list = close_contacts if d < nearest_node_distance else farther_contacts
                if peer.id not in [c.id for c in target_list]:
                    target_list.append(peer)

        return val is not None, val, found_by

    async def lookup(self, key: int,
                     rpc_call: Callable[[int, Contact], tuple[list[Contact], Contact, str]],
                     give_all: bool = False) -> (bool, list[Contact], Contact, str):
        """
        Node lookup algorithm for finding the closest nodes to the given key and they target itself if possible.
        """
        ret: list[Contact] = []
        have_work = True

        all_nodes: list[Contact] = self.node.bucket_list.get_kbucket(key).contacts

        nodes_to_query: list[Contact] = all_nodes[:Support.A_VAL]

        # Split contacts into two groups
        closer_contacts: list[Contact] = [node for node in nodes_to_query if node.id ^ key < self.node.our_contact.id ^ key]
        farther_contacts: list[Contact] = [node for node in nodes_to_query if node.id ^ key >= self.node.our_contact.id ^ key]

        # Keep track of distinct nodes that have been contacted
        contacted_ids: set[int] = {n.id for n in nodes_to_query}
        contacted_Nodes: list[Contact] = nodes_to_query

        # Initial query attempt
        found, contacts, found_by, val = self.query(key, nodes_to_query, rpc_call, closer_contacts, farther_contacts)

        # If initial query resulted in a hit, we are done
        if found:
            return found, contacts, found_by, val

        # otherwise, continue and add the closer contacts to the return
        ret.extend(c for c in closer_contacts if c.id not in {r.id for r in ret})

        # Loop and continue to try and find the target until K nodes have been contacted or no one is left to query
        while len(ret) < Support.K_VAL and have_work:
            # Find far and close nodes that have not been contacted
            closer_uncontacted_nodes: list[Contact] = [c for c in closer_contacts if c not in contacted_Nodes]
            farther_uncontacted_nodes: list[Contact] = [c for c in farther_contacts if c not in contacted_Nodes]

            # Do we have nodes to contact?
            have_closer: bool = len(closer_uncontacted_nodes) > 0
            have_farther: bool = len(farther_uncontacted_nodes) > 0

            # Do we REALLY have nodes to contact?
            have_work = have_closer or have_farther

            # Try close nodes first
            if have_closer:
                new_nodes_to_query = closer_uncontacted_nodes[:Support.A_VAL]
                contacted_Nodes.extend(n for n in new_nodes_to_query if n.id not in contacted_ids)
                contacted_ids.update(n.id for n in new_nodes_to_query)

                # Query again
                found, contacts, found_by, val = self.query(key, new_nodes_to_query, rpc_call, closer_contacts,
                                                            farther_contacts)

                # Exit if we found the target
                if found:
                    return found, contacts, found_by, val

            # Do the same for the far uncontacted nodes
            elif have_farther:
                new_nodes_to_query = farther_uncontacted_nodes[:Support.A_VAL]
                contacted_Nodes.extend(n for n in new_nodes_to_query if n not in contacted_ids)
                contacted_ids.update(n.id for n in new_nodes_to_query)

                # Query again
                found, contacts, found_by, val = self.query(key, new_nodes_to_query, rpc_call, closer_contacts,
                                                            farther_contacts)

                if found:
                    return found, contacts, found_by, val

        if give_all:
            return False, ret, None, None
        else:
            return False, sorted(ret, key=lambda c: c.id ^ key)[:Support.K_VAL], None, None








