"""Regression tests for failures missed by the former shallow validator."""
import unittest
from validate_catalog import ROOT, read, check_document, no_duplicate_keys

class ValidationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.map=read(ROOT/'maps/BMG-GLITCH.JSON')
        self.schema=read(ROOT/'genre-map.schema.json')

    def test_real_map_valid(self):
        self.assertEqual(check_document(self.map,self.schema),[])

    def test_unknown_namespace_rejected(self):
        self.map['taxonomy']['invented_namespace']={}
        self.assertTrue(check_document(self.map,self.schema))

    def test_old_unsupported_status_rejected(self):
        self.map['taxonomy']['bmg']['status']='pending_official_tag_verification'
        self.assertTrue(check_document(self.map,self.schema))

    def test_missing_term_provenance_rejected(self):
        self.map['taxonomy']['bmg']['term_evidence'].pop('Glitch')
        self.assertTrue(any('provenance' in e for e in check_document(self.map,self.schema)))

    def test_empty_evidence_gap_is_valid(self):
        self.assertEqual(check_document(read(ROOT/'maps/BMG-NEUROFUNK.JSON'),self.schema),[])

    def test_zero_tempo_template_rejected(self):
        self.map['parameters']['tempo_bpm']={'min':0,'max':0,'preferred':[0]}
        self.assertTrue(check_document(self.map,self.schema))

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError): no_duplicate_keys([('term','a'),('term','b')])

    def test_wrong_type_rejected(self):
        self.map['taxonomy']['bmg']['genre_terms']='Glitch'
        self.assertTrue(check_document(self.map,self.schema))

if __name__=='__main__': unittest.main()
