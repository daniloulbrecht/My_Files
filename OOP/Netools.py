from ipaddress import ip_network
import random

class Netools():
    def __init__(self, network):
        self.network = ip_network(network)
    def generate_ip_list(self):
        """
        Generates a complete list of IPs inside a subnet without
		network and broadcast addresses.
        """
        ip_list = []
        for ip in self.network.hosts():
            ip_list.append(str(ip))
        return ip_list
    def generate_random_ips(self, ips=3):
        """
        Generates a random list of IPs inside a subnet without
		network and broadcast addresses.
        Default = 3 IPs.
        You can change to any value passing as argument to
        parameter 'ips'.
        For example:
        generate_random_ips(20)
        """
        ip_list = []
        for ip in self.network.hosts():
            ip_list.append(str(ip))
        random.shuffle(ip_list)
        ip_list = random.sample(ip_list, ips)
        return ip_list
    def fhrp_ips(self, first_three=True, last_three=False):
        """
        This method generates fhrp commum used IPs (first three or
        last three IPs) plus mask.
        The sequence returned is mask, ip, ip, ip for example.
        Returns only first three IPs but you can change this behavior
        by passing other argument values in parameters.
        first_three=True, last_three=False is the default values.
        """
        netip = self.network.network_address
        mask = self.network.netmask
        first_ip, second_ip, third_ip = netip + 1, netip + 2, netip + 3
        last_ip, penultimate_ip, antepenultimate_ip = (self.network.broadcast_address
            - 1, self.network.broadcast_address - 2, self.network.broadcast_address - 3)
        if first_three == True and last_three == True:
            return (str(mask), str(first_ip), str(second_ip),
                str(third_ip), str(antepenultimate_ip), str(penultimate_ip), str(last_ip))
        elif last_three == True:
            return str(mask), str(antepenultimate_ip), str(penultimate_ip), str(last_ip)
        else:
            return str(mask), str(first_ip), str(second_ip), str(third_ip)
    def isasubnet(self, networklist, result=False, matchednetwork=None):
        """
        This method checks whether a network is a subnet of any of the
        networks from a networklist, if positive returns True and the
        corresponding network (returns Boolean value, and network
        corresponding in str). If not, returns False and None.
        """
        for targetnetwork in networklist:
            targetobg = ip_network(targetnetwork)
            result = self.network.subnet_of(targetobg)
            if result == True:
                matchednetwork = str(targetobg)
                break
        return result, matchednetwork
    def isasupernet(self, networklist, result=False, matchednetworklist=[]):
        """
        This method checks whether a network is a supernet of some
        of networks from a network list, if positive returns True
        and the list of matching networks (returns Boolean value,
        and corresponding network (s) in list). If not, returns
        False and None
        """
        for targetnetwork in networklist:
            targetobg = ip_network(targetnetwork)
            result = self.network.supernet_of(targetobg)
            if result == True:
                matchednetworklist.append(str(targetobg))
        if matchednetworklist:
            return result, matchednetworklist
        else:
            return result, None
