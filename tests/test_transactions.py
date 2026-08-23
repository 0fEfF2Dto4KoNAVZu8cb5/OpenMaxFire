import unittest

from openmaxfire.client import MaxFireClient
from openmaxfire.transactions import execute_transaction, parse_transaction_plan


class FakeTransport:
    def __init__(self, incoming: bytes = b""):
        self.incoming = bytearray(incoming)
        self.writes: list[bytes] = []

    def write(self, data: bytes) -> None:
        self.writes.append(data)

    def read(self, size: int = 1) -> bytes:
        if not self.incoming:
            return b""
        result = bytes(self.incoming[:size])
        del self.incoming[:size]
        return result

    def close(self) -> None:
        pass


class TransactionTests(unittest.TestCase):
    def test_plan_normalizes_register_values(self):
        plan = parse_transaction_plan(
            {
                "schema": "openmaxfire.transaction.v1",
                "description": "fixture",
                "operations": [
                    {"op": "read", "unit": "C", "address": "0x02"},
                    {"op": "delay", "seconds": 0},
                    {
                        "op": "write",
                        "unit": "A",
                        "address": "0x6B",
                        "value": "0x40",
                        "verify": True,
                    },
                ],
            }
        )
        self.assertTrue(plan.has_writes)
        self.assertEqual(plan.to_dict()["operations"][2]["value"], "0x40")

    def test_loader_entry_is_rejected_from_register_transactions(self):
        with self.assertRaisesRegex(ValueError, "firmware loader"):
            parse_transaction_plan(
                {
                    "schema": "openmaxfire.transaction.v1",
                    "operations": [
                        {"op": "write", "unit": "C", "address": 0x0F, "value": 0xC4}
                    ],
                }
            )

    def test_unknown_field_is_rejected_instead_of_silently_ignored(self):
        with self.assertRaisesRegex(ValueError, "verfiy"):
            parse_transaction_plan(
                {
                    "schema": "openmaxfire.transaction.v1",
                    "operations": [
                        {
                            "op": "write",
                            "unit": "A",
                            "address": 0x10,
                            "value": 0x20,
                            "verfiy": True,
                        }
                    ],
                }
            )

    def test_write_plan_requires_api_authorization(self):
        plan = parse_transaction_plan(
            {
                "schema": "openmaxfire.transaction.v1",
                "operations": [
                    {"op": "write", "unit": "A", "address": 0x10, "value": 0x20}
                ],
            }
        )
        with self.assertRaises(PermissionError):
            execute_transaction(MaxFireClient(FakeTransport()), plan)

    def test_verified_plan_executes_in_order(self):
        plan = parse_transaction_plan(
            {
                "schema": "openmaxfire.transaction.v1",
                "operations": [
                    {"op": "read", "unit": "C", "address": 0x02},
                    {
                        "op": "write",
                        "unit": "A",
                        "address": 0x6B,
                        "value": 0x40,
                        "verify": True,
                    },
                ],
            }
        )
        transport = FakeTransport(b"CR0212\nAW6B40\nAR6b40\n")
        result = execute_transaction(
            MaxFireClient(transport), plan, allow_writes=True
        )
        self.assertTrue(result["success"])
        self.assertEqual(transport.writes, [b"CR02", b"AW6B40", b"AR6B"])
        self.assertEqual(result["results"][0]["request_hex"], "43 52 30 32")
        self.assertTrue(result["results"][1]["verified"])
        self.assertEqual(
            result["results"][1]["readback_request_hex"], "41 52 36 42"
        )

    def test_failed_verification_stops_following_operations(self):
        plan = parse_transaction_plan(
            {
                "schema": "openmaxfire.transaction.v1",
                "operations": [
                    {
                        "op": "write",
                        "unit": "A",
                        "address": 0x6B,
                        "value": 0x40,
                        "verify": True,
                    },
                    {"op": "read", "unit": "C", "address": 0x02},
                ],
            }
        )
        transport = FakeTransport(b"AR6b41\nCR0212\n")
        result = execute_transaction(
            MaxFireClient(transport), plan, allow_writes=True
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["operations_completed"], 1)
        self.assertEqual(transport.writes, [b"AW6B40", b"AR6B"])


if __name__ == "__main__":
    unittest.main()
