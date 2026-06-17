"""IP/CIDR parsing and deterministic network normalization."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedNetworks:
    ipv4: list[ipaddress.IPv4Network]
    ipv6: list[ipaddress.IPv6Network]
    invalid: list[str]


def parse_network(value: str) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("empty network")
    return ipaddress.ip_network(cleaned, strict=False)


def split_networks(values: list[str]) -> ParsedNetworks:
    ipv4: list[ipaddress.IPv4Network] = []
    ipv6: list[ipaddress.IPv6Network] = []
    invalid: list[str] = []
    for value in values:
        try:
            network = parse_network(value)
        except ValueError:
            invalid.append(value)
            continue
        if isinstance(network, ipaddress.IPv4Network):
            ipv4.append(network)
        else:
            ipv6.append(network)
    return ParsedNetworks(
        ipv4=sort_networks(collapse_networks(ipv4)),
        ipv6=sort_networks(collapse_networks(ipv6)),
        invalid=sorted(set(invalid)),
    )


def collapse_networks(networks: list[ipaddress._BaseNetwork]) -> list[ipaddress._BaseNetwork]:
    return list(ipaddress.collapse_addresses(networks))


def sort_networks(networks: list[ipaddress._BaseNetwork]) -> list:
    return sorted(networks, key=lambda network: (network.version, int(network.network_address), network.prefixlen))


def stringify_networks(networks: list[ipaddress._BaseNetwork]) -> list[str]:
    return [str(network) for network in sort_networks(networks)]

