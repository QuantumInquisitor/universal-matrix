import unittest
from src.plasma_shader_pipeline import PlasmaShaderCompiler, ShaderUniformsPayload

class TestPlasmaShaderCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = PlasmaShaderCompiler()

    def test_uniform_compilation_and_color(self):
        payload = ShaderUniformsPayload(
            so13_rotation_angle_rad=0.7854,
            field_frequency_hz=432000000.0,
            toroidal_coherence=0.90,
            element_plane_tilt_deg=45.0
        )
        uniforms = self.compiler.compile_uniforms(payload)
        self.assertIn("u_plasma_color", uniforms)
        self.assertEqual(len(uniforms["u_plasma_color"]), 3)
        self.assertIn("glsl_fragment_snippet", uniforms)
        self.assertGreater(uniforms["u_coherence_density"], 0.0)

if __name__ == '__main__':
    unittest.main()
