"""
Determine a host's IP address given its MAC address and an IP address
range to scan for it.

I created this to discover a WLAN printer (which dynamically gets an IP
address assigned via DHCP) on the local network.

Calls Nmap_ to ping hosts and return their MAC addresses (requires root
privileges).

Requires Python_ 2.7+ or 3.3+.


:Copyright: 2014-2016 `Jochen Kupperschmidt
:Date: 27-Mar-2016 (original release: 25-Jan-2014)
:License: MIT
"""

import subprocess
import xml.etree.ElementTree as Et


def __scan_for_hosts(ip_range):
    """Scan the given IP address range using Nmap and return the result
    in XML format.
    """
    nmap_args = ['nmap', '-n', '-sP', '-oX', '-', ip_range]
    return subprocess.check_output(nmap_args)


def find_ip_address_for_mac_address(mac_address, ip_range):
    """Parse Nmap's XML output, find the host element with the given
    MAC address, and return that host's IP address (or `None` if no
    match was found).
    """
    found_ips = []
    xml = __scan_for_hosts(ip_range)
    host_elems = Et.fromstring(xml).iter('host')

    for x in range(len(mac_address)):
        host_elem = __find_host_with_mac_address(host_elems, mac_address[x])
        if host_elem is not None:
            found_ips.append(__find_ip_address(host_elem))
    return found_ips


def __find_host_with_mac_address(host_elems, mac_address):
    """Return the first host element that contains the MAC address."""
    for host_elem in host_elems:
        if __host_has_mac_address(host_elem, mac_address):
            return host_elem


def __host_has_mac_address(host_elem, wanted_mac_address):
    """Return true if the host has the given MAC address."""
    found_mac_address = __find_mac_address(host_elem)
    return (
        found_mac_address is not None and
        found_mac_address.lower() == wanted_mac_address.lower()
    )


def __find_mac_address(host_elem):
    """Return the host's MAC address."""
    return __find_address_of_type(host_elem, 'mac')


def __find_ip_address(host_elem):
    """Return the host's IP address."""
    return __find_address_of_type(host_elem, 'ipv4')


def __find_address_of_type(host_elem, type_):
    """Return the host's address of the given type, or `None` if there
    is no address element of that type.
    """
    address_elem = host_elem.find('./address[@addrtype="{}"]'.format(type_))
    if address_elem is not None:
        return address_elem.get('addr')


# if __name__ == '__main__':
#     mac_address = '00:33:66:99:cc:ff'
#     ip_range = '192.168.1.1-255'
#
#     xml = scan_for_hosts(ip_range)
#     ip_address = find_ip_address_for_mac_address(xml, mac_address)
#
#     if ip_address:
#         print('Found IP address {} for MAC address {} in IP address range {}.'
#               .format(ip_address, mac_address, ip_range))
#     else:
#         print('No IP address found for MAC address {} in IP address range {}.'
#               .format(mac_address, ip_range))
