# backend/rdt/stop_and_wait.py

from typing import Dict, Any, List
from .packet import make_packet, is_corrupted
from .unreliable_channel import UnreliableChannel


def chunk_data(data: str, packet_size: int) -> List[str]:
    return [data[i : i + packet_size] for i in range(0, len(data), packet_size)]


def simulate_stop_and_wait(
    message: str,
    packet_size: int = 4,
    loss_rate: float = 0.1,
    corruption_rate: float = 0.1,
    ack_loss_rate: float = 0.05,
    max_retries_per_packet: int = 20,
) -> Dict[str, Any]:
    """
    Simulate a Stop-and-Wait reliable data transfer over an unreliable channel.

    Returns a dict with:
        - events: list of event dicts (timeline)
        - final_data: reconstructed data at receiver
        - stats: counters
        - config_used: config params
    """
    channel = UnreliableChannel(
        loss_rate=loss_rate,
        corruption_rate=corruption_rate,
        ack_loss_rate=ack_loss_rate,
    )

    chunks = chunk_data(message, packet_size)
    events: List[Dict[str, Any]] = []

    stats = {
        "total_packets": len(chunks),
        "packets_sent": 0,
        "retransmissions": 0,
        "packets_lost": 0,
        "packets_corrupted": 0,
        "acks_lost": 0,
        "successful_packets": 0,
        "aborted": False,
    }

    delivered_data: List[str] = []
    expected_seq_at_receiver = 0
    step = 0

    for seq_num, chunk in enumerate(chunks):
        retry_count = 0
        packet_delivered_and_acked = False

        while not packet_delivered_and_acked:
            step += 1
            retry_count += 1
            stats["packets_sent"] += 1

            if retry_count > 1:
                stats["retransmissions"] += 1

            if retry_count > max_retries_per_packet:
                events.append(
                    {
                        "step": step,
                        "type": "error",
                        "who": "sender",
                        "seq": seq_num,
                        "description": f"Max retries reached for packet {seq_num}. Aborting.",
                    }
                )
                stats["aborted"] = True
                # Abort entire simulation
                final_data = "".join(delivered_data)
                return {
                    "events": events,
                    "final_data": final_data,
                    "stats": stats,
                    "config_used": {
                        "packet_size": packet_size,
                        "loss_rate": loss_rate,
                        "corruption_rate": corruption_rate,
                        "ack_loss_rate": ack_loss_rate,
                        "max_retries_per_packet": max_retries_per_packet,
                    },
                }

            packet = make_packet(seq_num, chunk)
            events.append(
                {
                    "step": step,
                    "type": "send_packet",
                    "who": "sender",
                    "seq": seq_num,
                    "data": chunk,
                    "description": f"Sender sends packet #{seq_num} (attempt {retry_count}).",
                }
            )

            # Transmit packet through unreliable channel
            delivered_packet, status = channel.transmit_packet(packet)

            if status == "lost":
                stats["packets_lost"] += 1
                step += 1
                events.append(
                    {
                        "step": step,
                        "type": "packet_lost",
                        "who": "channel",
                        "seq": seq_num,
                        "description": f"Packet #{seq_num} was lost in the channel.",
                    }
                )
                # Sender will "timeout" and retry (simulated by continuing loop)
                continue

            if status == "corrupted":
                stats["packets_corrupted"] += 1
                step += 1
                events.append(
                    {
                        "step": step,
                        "type": "packet_corrupted",
                        "who": "channel",
                        "seq": seq_num,
                        "description": f"Packet #{seq_num} was corrupted in the channel.",
                    }
                )
                # Receiver sees corrupted packet and drops it
                step += 1
                events.append(
                    {
                        "step": step,
                        "type": "drop_corrupted",
                        "who": "receiver",
                        "seq": seq_num,
                        "description": f"Receiver drops corrupted packet #{seq_num}. No ACK sent.",
                    }
                )
                # Sender will retry
                continue

            # status == "ok"
            step += 1
            events.append(
                {
                    "step": step,
                    "type": "packet_received",
                    "who": "receiver",
                    "seq": delivered_packet.seq_num,
                    "data": delivered_packet.data,
                    "description": f"Receiver got packet #{delivered_packet.seq_num}.",
                }
            )

            # Verify checksum at receiver
            if is_corrupted(delivered_packet):
                stats["packets_corrupted"] += 1
                step += 1
                events.append(
                    {
                        "step": step,
                        "type": "drop_corrupted",
                        "who": "receiver",
                        "seq": delivered_packet.seq_num,
                        "description": f"Receiver detected corruption in packet #{delivered_packet.seq_num} and dropped it.",
                    }
                )
                # No ACK, sender will retry
                continue

            # Check sequence number
            if delivered_packet.seq_num != expected_seq_at_receiver:
                step += 1
                events.append(
                    {
                        "step": step,
                        "type": "unexpected_seq",
                        "who": "receiver",
                        "seq": delivered_packet.seq_num,
                        "expected_seq": expected_seq_at_receiver,
                        "description": f"Receiver expected seq #{expected_seq_at_receiver}, got #{delivered_packet.seq_num}. Dropping.",
                    }
                )
                # Simple stop-and-wait: drop, no ACK
                continue

            # All good: deliver data
            delivered_data.append(delivered_packet.data)
            stats["successful_packets"] += 1
            expected_seq_at_receiver += 1

            step += 1
            events.append(
                {
                    "step": step,
                    "type": "deliver_data",
                    "who": "receiver",
                    "seq": delivered_packet.seq_num,
                    "data": delivered_packet.data,
                    "description": f"Receiver delivers data for packet #{delivered_packet.seq_num} to application.",
                }
            )

            # Send ACK back
            ack_seq = delivered_packet.seq_num
            step += 1
            events.append(
                {
                    "step": step,
                    "type": "send_ack",
                    "who": "receiver",
                    "seq": ack_seq,
                    "description": f"Receiver sends ACK for packet #{ack_seq}.",
                }
            )

            ack_delivered, ack_status = channel.transmit_ack(ack_seq)
            if ack_status == "lost":
                stats["acks_lost"] += 1
                step += 1
                events.append(
                    {
                        "step": step,
                        "type": "ack_lost",
                        "who": "channel",
                        "seq": ack_seq,
                        "description": f"ACK for packet #{ack_seq} was lost.",
                    }
                )
                # Sender will timeout and retry
                continue

            # ACK arrived at sender
            step += 1
            events.append(
                {
                    "step": step,
                    "type": "ack_received",
                    "who": "sender",
                    "seq": ack_delivered,
                    "description": f"Sender received ACK for packet #{ack_delivered}.",
                }
            )
            packet_delivered_and_acked = True

    final_data = "".join(delivered_data)

    return {
        "events": events,
        "final_data": final_data,
        "stats": stats,
        "config_used": {
            "packet_size": packet_size,
            "loss_rate": loss_rate,
            "corruption_rate": corruption_rate,
            "ack_loss_rate": ack_loss_rate,
            "max_retries_per_packet": max_retries_per_packet,
        },
    }
