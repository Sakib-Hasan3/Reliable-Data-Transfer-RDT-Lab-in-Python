# backend/rdt/packet.py

import zlib
from dataclasses import dataclass


@dataclass
class Packet:
    seq_num: int
    data: str
    checksum: int


def compute_checksum(seq_num: int, data: str) -> int:
    """
    Compute a CRC32 checksum over seq_num and data.
    """
    s = f"{seq_num}|{data}"
    return zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF


def make_packet(seq_num: int, data: str) -> Packet:
    """
    Create a packet with correct checksum.
    """
    checksum = compute_checksum(seq_num, data)
    return Packet(seq_num=seq_num, data=data, checksum=checksum)


def is_corrupted(packet: Packet) -> bool:
    """
    Check if a packet's checksum matches its contents.
    """
    expected = compute_checksum(packet.seq_num, packet.data)
    return expected != packet.checksum
