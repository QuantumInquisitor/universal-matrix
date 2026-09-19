import unittest
from src.core.pino_engine import PhysicsInformedOperator
from src.hal.safety_driver import SafetyInterlockDriver

class TestPinoGuardrailRemedy(unittest.TestCase):
    def setUp(self):
        self.pino = PhysicsInformedOperator(energy_threshold=100.0)
        self.safety = SafetyInterlockDriver()

    def test_pino_blocks_impossible_ml_move_before_HITL(self):
        impossible_move = [[1500.0, 1500.0], [1500.0, 1500.0]]
        
        # 1. PINO Core detects physical conservation violation
        pino_check = self.pino.enforce_conservation_laws(impossible_move)
        
        print(f"\n[PINO Check] Result: {pino_check['status']} (Energy: {pino_check['total_energy']})")
        
        self.assertFalse(pino_check["is_physically_valid"])
        self.assertEqual(pino_check["status"], "PHYSICS_VIOLATION_DETECTED")

        # 2. Safety Interlock evaluates scalar velocity against thresholds (>1000.0)
        validation = self.safety.validate_spatial_vector(impossible_move[0][0])
        
        print(f"[Safety Check] Result Payload: {validation}")

        # Verify safety interlock triggered (either non-NOMINAL status or lock flag)
        is_locked = validation.get("hardware_locked", False) or validation.get("is_e_stop_active", False) or validation.get("status") != "NOMINAL"
        self.assertTrue(is_locked)

    def test_nominal_ml_move_passes_both_guardrails(self):
        valid_move = [[3.0, 4.0], [3.0, 4.0]]
        
        pino_check = self.pino.enforce_conservation_laws(valid_move)
        validation = self.safety.validate_spatial_vector(valid_move[0][0])
        
        self.assertTrue(pino_check["is_physically_valid"])
        self.assertEqual(validation.get("status"), "NOMINAL")

if __name__ == "__main__":
    unittest.main()
