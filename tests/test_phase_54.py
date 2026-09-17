import unittest
from src.fpga_bitstream_compiler import FPGABitstreamCompiler

class TestPhase54FPGACompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = FPGABitstreamCompiler(target_vendor="XILINX")

    def test_transpilation_success(self):
        wgsl = "@compute @workgroup_size(64) fn main() { spatial_flux *= 1.14; }"
        res = self.compiler.transpile_wgsl_to_hdl(wgsl)
        self.assertEqual(res["status"], "SYNTHESIS_SUCCESSFUL")
        self.assertEqual(res["target_vendor"], "XILINX")
        self.assertIn("module wgsl_flux_core_", res["verilog_hdl"])
        self.assertIn("bitstream_hash", res)

    def test_transpilation_failed_empty_input(self):
        res = self.compiler.transpile_wgsl_to_hdl("")
        self.assertEqual(res["status"], "COMPILATION_FAILED")

if __name__ == "__main__":
    unittest.main()

