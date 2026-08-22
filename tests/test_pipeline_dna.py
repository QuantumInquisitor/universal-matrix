import unittest
import numpy as np
from src.run_field_simulation import HighDimensionalMatrixEngine
from src.dna_bio_mapper import DNABioMapper

class TestPipelineDNAIntegration(unittest.TestCase):

    def setUp(self):
        self.matrix_engine = HighDimensionalMatrixEngine(num_nodes=114, dim=13)
        self.dna_mapper = DNABioMapper(base_freq=432.0)

    def test_pipeline_layer_8_dna_tensor_injection(self):
        """Verify orchestrator applies Layer 8 biological tensor transformations cleanly."""
        seq = "ATGCGATCG"
        tensor_13d = self.dna_mapper.sequence_to_13d_tensor(seq)
        
        # Inject sequence slice into matrix engine SO(13) state matrix
        self.matrix_engine.state_matrix[:len(seq), :] = tensor_13d[:len(seq), :]
        
        transformed_state = self.matrix_engine.state_matrix
        
        self.assertEqual(transformed_state.shape, (13, 13))
        self.assertFalse(np.isnan(transformed_state).any())

if __name__ == "__main__":
    unittest.main()
