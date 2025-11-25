# backend/rdt/unreliable_channel.py

import random
from .packet import Packet


class UnreliableChannel:
    """
    Simulates an unreliable channel for data packets and ACKs.
    """

    def __init__(
        self,
        loss_rate: float = 0.1,
        corruption_rate: float = 0.1,
        ack_loss_rate: float = 0.05,
    ):
        self.loss_rate = loss_rate
        self.corruption_rate = corruption_rate
        self.ack_loss_rate = ack_loss_rate

    def transmit_packet(self, packet: Packet):
        """
        Simulate transmitting a data packet from sender to receiver.

        Returns: (delivered_packet_or_None, status_str)
        status_str in {"ok", "lost", "corrupted"}
        """
        # Packet lost
        if random.random() < self.loss_rate:
            return None, "lost"

        # Copy packet to avoid mutating original
        delivered = Packet(packet.seq_num, packet.data, packet.checksum)

        # Corrupt packet
        if random.random() < self.corruption_rate:
            # Simple corruption: flip one character in data if possible
            if delivered.data:
                idx = random.randrange(len(delivered.data))
                corrupted_char = chr((ord(delivered.data[idx]) + 1) % 128)
                delivered.data = (
                    delivered.data[:idx] + corrupted_char + delivered.data[idx + 1 :]
                )
            return delivered, "corrupted"

        return delivered, "ok"

    def transmit_ack(self, ack_seq: int):
        """
        Simulate transmitting an ACK from receiver to sender.

        Returns: (ack_seq_or_None, status_str)
        status_str in {"ok", "lost"}
        """
        if random.random() < self.ack_loss_rate:
            return None, "lost"
        return ack_seq, "ok"
