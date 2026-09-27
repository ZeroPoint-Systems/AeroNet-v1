import pytest

from simulation.communication.packet import Packet


def test_packet_records_size_in_bytes():
    packet = Packet(sender_id="a1", receiver_id="a2", timestamp_created=0.0, payload=[1, 2, 3])
    assert packet.size_bytes > 0


def test_self_addressed_packet_is_rejected():
    with pytest.raises(ValueError):
        Packet(sender_id="a1", receiver_id="a1", timestamp_created=0.0, payload=None)


def test_mark_delivered_before_creation_time_is_rejected():
    packet = Packet(sender_id="a1", receiver_id="a2", timestamp_created=5.0, payload=None)
    with pytest.raises(ValueError):
        packet.mark_delivered(4.0)


def test_mark_delivered_twice_is_rejected():
    packet = Packet(sender_id="a1", receiver_id="a2", timestamp_created=0.0, payload=None)
    packet.mark_delivered(1.0)
    with pytest.raises(ValueError):
        packet.mark_delivered(2.0)


def test_mark_delivered_sets_timestamp():
    packet = Packet(sender_id="a1", receiver_id="a2", timestamp_created=0.0, payload=None)
    packet.mark_delivered(3.0)
    assert packet.timestamp_delivered == 3.0
