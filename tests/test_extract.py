import unittest
import json
import time

from txt2hpo.extract import Extractor, group_sequence
from tests.test_cases import *


class ExtractPhenotypesTestCase(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print('%s: %.3f' % (self.id(), t))

    def test_group_sequence(self):
        truth = [[0, 1], [3]]
        self.assertEqual(group_sequence([0, 1, 3]), truth)

    def test_hpo(self):

        hpo = Extractor(return_context=True, correct_spelling=False).hpo

        # Test extracting single phenotype
        truth = json.dumps([{"hpid": ["HP:0001290"], "index": [0, 9], "matched": "Hypotonia", "context": "Hypotonia"}])
        self.assertEqual(hpo("Hypotonia"), truth)

        # Test adding non phenotypic term
        truth = json.dumps([{"hpid": ["HP:0001290"], "index": [5, 14], "matched": "hypotonia", "context": "Word hypotonia"}])
        self.assertEqual(hpo("Word hypotonia"), truth)

        # Test handling punctuation
        truth = json.dumps([{"hpid": ["HP:0001290"], "index": [6, 15], "matched": "hypotonia", "context": "Word, hypotonia"}])
        self.assertEqual(hpo("Word, hypotonia"), truth)

        # Test extracting a multiword phenotype
        truth = json.dumps([{"hpid": ["HP:0001263"],
                             "index": [0, 19], "matched": "Developmental delay",
                             "context": "Developmental delay"}])
        self.assertEqual(hpo("Developmental delay"), truth)

        # Test extracting a multiword phenotype with reversed word order
        truth = json.dumps([{"hpid": ["HP:0001263"], "index": [0, 19],
                             "matched": "Delay developmental",
                             "context": "Delay developmental"}])

        #hpo = Extractor(return_context=True, correct_spelling=False).hpo()

        self.assertEqual(hpo("Delay developmental"), truth)

        # Test extracting a phenotype with inflectional endings
        truth = json.dumps([{"hpid": ["HP:0001290"], "index": [0, 9], "matched": "Hypotonic", "context": "Hypotonic"}])
        self.assertEqual(hpo("Hypotonic"), truth)

        # Test extracting a multiword phenotype with inflectional endings and reversed order
        truth = json.dumps([{"hpid": ["HP:0001263"], "index": [0, 19], "matched": "Delayed development",
                             "context": "Delayed development"}])
        self.assertEqual(hpo("Delayed development"), truth)

        # Test extracting multiword phenotype following an unrelated phenotypic term
        truth = json.dumps([{"hpid": ["HP:0000365"], "index": [6, 18],
                             "matched": "hearing loss", "context":"Delay hearing loss"}])
        self.assertEqual(hpo("Delay hearing loss"), truth)

        # Test extracting multiword phenotype preceding an unrelated phenotypic term
        truth = json.dumps([{"hpid": ["HP:0000365"], "index": [0, 12],
                             "matched": "Hearing loss", "context":"Hearing loss following"}])
        self.assertEqual(hpo("Hearing loss following"), truth)

        # Test extracting two multiword phenotype preceding interrupted by an unrelated phenotypic term
        truth = json.dumps([
                            {"hpid": ["HP:0001263"], "index": [23, 42], "matched": "developmental delay",
                             "context": "Hearing loss following developmental delay"},
                            {"hpid": ["HP:0000365"], "index": [0, 12], "matched": "Hearing loss",
                             "context":"Hearing loss following developmental delay"}
                            ])
        self.assertEqual(hpo("Hearing loss following developmental delay"), truth)

        # Test spellchecker
        hpo = Extractor(return_context=True, correct_spelling=True).hpo
        truth = json.dumps([{"hpid": ["HP:0001290"], "index": [0, 9], "matched": "hypotonic",
                             "context":"hypotonic"}])

        self.assertEqual(hpo("hyptonic"), truth)

        truth = json.dumps([])
        hpo = Extractor(return_context=True, correct_spelling=False).hpo
        self.assertEqual(hpo("hyptonic"), truth)

        truth = json.dumps([{"hpid": ["HP:0000938"], "index": [35, 45], "matched": "osteopenia",
                             "context":"Female with multiple fractures and osteopenia NA NA"},
                        {"hpid": ["HP:0002757"],"index": [12, 30], "matched": "multiple fractures",
                         "context": "Female with multiple fractures and osteopenia NA NA"}])

        self.assertEqual(truth, hpo("Female with multiple fractures and osteopenia NA NA"))

        truth = json.dumps([{"hpid": ["HP:0001156"], "index": [30, 43], "matched": "brachydactyly",
                             "context": "Female with fourth metacarpal brachydactyly"}])

        self.assertEqual(truth, hpo("Female with fourth metacarpal brachydactyly"))

        hpo = Extractor(return_context=False, correct_spelling=False).hpo
        truth = json.dumps([{"hpid": ["HP:0000988"], "index": [23, 27], "matched": "rash"},
                            {"hpid": ["HP:0000988"], "index": [18, 27], "matched": "skin rash"},
                            {"hpid": ["HP:0008070"], "index": [33, 44], "matched": "sparse hair"},
                            {"hpid": ["HP:0000964"], "index": [10, 16], "matched": "eczema"}])

        self.assertEqual(truth, hpo("Male with eczema, skin rash, and sparse hair"))

        # Test extracting multiple phenotypes with max_neighbors
        hpo = Extractor(return_context=True, correct_spelling=True, max_neighbors=3).hpo
        truth = json.dumps([{"hpid": ["HP:0001263"], "index": [0, 23], "matched": "developmental and delay",
                             "context": "developmental and delay"}])
        self.assertEqual(hpo("developmental and delay"), truth)

        hpo = Extractor(return_context=True, correct_spelling=True, max_neighbors=1).hpo
        truth = json.dumps([])
        self.assertEqual(hpo("developmental and delay"), truth)

        hpo = Extractor(correct_spelling=False, return_context=False).hpo

        # Test extracting single phenotype followed by multiword phenotype
        truth = json.dumps([
                 {"hpid": ["HP:0000750"], "index": [0, 12], "matched": "Speech delay"},
                 {"hpid": ["HP:0100710"], "index": [17, 26], "matched": "impulsive"}
        ])
        self.assertEqual(hpo("Speech delay and impulsive"), truth)

        # Test extracting multiword phenotype followed by single phenotype
        truth = json.dumps([
                 {"hpid": ["HP:0100710"], "index": [0, 9], "matched": "Impulsive"},
                 {"hpid": ["HP:0000750"], "index": [14, 26], "matched": "speech delay"}
                 ])
        self.assertEqual(hpo("Impulsive and speech delay"), truth)

        # Test extracting an abbreviated phenotype
        truth = json.dumps([{"hpid": ["HP:0001370"], "index": [0, 2], "matched": "RA"}])
        self.assertEqual(hpo("RA"), truth)

        # Test extracting multiple phenotypes
        truth = json.dumps([{"hpid": ["HP:0001290"], "index": [0, 9], "matched": "Hypotonia"},
                            {"hpid": ["HP:0001263"], "index": [11, 30], "matched": "developmental delay"
                             }])
        self.assertEqual(hpo("Hypotonia, developmental delay"), truth)

        # Test term indexing given max length of extracted text
        hpo = Extractor(correct_spelling=False, return_context=False, max_length=20).hpo
        truth = json.dumps([
            {"hpid": ["HP:0001263"], "index": [0, 19], "matched": "Developmental delay"},
            {"hpid": ["HP:0001290"], "index": [21, 30], "matched": "hypotonia"}
        ])
        self.assertEqual(hpo("Developmental delay, hypotonia"), truth)

    def test_hpo_big_text_spellcheck_on(self):
        # test parsing a page
        hpo = Extractor(max_neighbors=2).hpo
        self.assertEqual(len(json.loads(hpo(test_case11_text))), 9)

    def test_hpo_big_text_spellcheck_off(self):
        # test parsing a page
        hpo = Extractor(max_neighbors=2, correct_spelling=False).hpo
        self.assertEqual(len(json.loads(hpo(test_case11_text))), 9)

    def test_hpo_big_text_spellcheck_off_max3(self):
        # test parsing a page
        hpo = Extractor(max_neighbors=3, correct_spelling=False).hpo
        self.assertEqual(len(json.loads(hpo(test_case11_text))), 10)

    def test_hpo_big_text_max_neighbors(self):
        # test parsing a page
        hpo = Extractor(max_neighbors=2, correct_spelling=True).hpo
        hpo_max_2 = json.loads(hpo(test_case11_text))
        hpo = Extractor(max_neighbors=3, correct_spelling=True).hpo
        hpo_max_3 = json.loads(hpo(test_case11_text))

        self.assertNotEqual(hpo_max_2, hpo_max_3)

    def test_iteration_over_chunks(self):
        # test performing multiple extractions in a row
        sentences = ['Developmental delay', 'Hypotonia']
        hpo = Extractor(correct_spelling=False).hpo
        for sentence in sentences:
            result = json.loads(hpo(sentence))
            self.assertNotEqual(len(result), 0)
        sentences = ['Hypotonia', 'Developmental delay']

        for sentence in sentences:
            result = json.loads(hpo(sentence))
            self.assertNotEqual(len(result), 0)

        hpo = Extractor(correct_spelling=True).hpo
        sentences = ['Developmental delay', 'Hypotonia']
        for sentence in sentences:
            result = json.loads(hpo(sentence))
            self.assertNotEqual(len(result), 0)
        sentences = ['Hypotonia', 'Developmental delay']

        for sentence in sentences:
            result = json.loads(hpo(sentence))
            self.assertNotEqual(len(result), 0)

        sentences = ['Developmental delay', 'Hypotonia']
        for sentence in sentences:
            result = json.loads(hpo(sentence))
            self.assertNotEqual(len(result), 0)
        sentences = ['Hypotonia', 'Developmental delay']

        for sentence in sentences:
            result = json.loads(hpo(sentence))
            self.assertNotEqual(len(result), 0)

    def test_conflict_resolver(self):

        conflict_resolver = Extractor().conflict_resolver

        extracted = [{"hpid": ["HP:0000729", "HP:0001631"],
                    "index": [50, 53],
                    "matched": "ASD",
                    "context": "the sample, 14,16 children were diagnosed with ASD, of whom 5689 had neurological and"}]

        truth = [{"hpid": ["HP:0000729"],
                    "index": [50, 53],
                    "matched": "ASD",
                    "context": "the sample, 14,16 children were diagnosed with ASD, of whom 5689 had neurological and"}]

        self.assertEqual(truth, conflict_resolver(extracted))

        extracted = [{"hpid": ["HP:0000729", "HP:0001631"],
                  "index": [44, 47],
                  "matched": "ASD",
                  "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                  whose defect spontaneously closed"}]

        truth = [{"hpid": ["HP:0001631"],
                  "index": [44, 47],
                  "matched": "ASD",
                  "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                  whose defect spontaneously closed"}]

        self.assertEqual(truth, conflict_resolver(extracted))

        # Test conflict resolution if terms have identical context similarity scores

        extracted = [{"hpid": ["HP:0001631", "HP:0001631"],
                      "index": [44, 47],
                      "matched": "ASD",
                      "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                          whose defect spontaneously closed"}]

        # Expected result remove only one term
        truth = [{"hpid": ["HP:0001631"],
                  "index": [44, 47],
                  "matched": "ASD",
                  "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                          whose defect spontaneously closed"}]

        self.assertEqual(truth, conflict_resolver(extracted))

        # Test conflict resolution if terms have identical context similarity scores

        extracted = [{"hpid": ["HP:0001631", "HP:0001631"],
                      "index": [44, 47],
                      "matched": "ASD",
                      "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                                  whose defect spontaneously closed"}]

        # Expected result remove only one term
        truth = [{"hpid": ["HP:0001631"],
                  "index": [44, 47],
                  "matched": "ASD",
                  "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                                  whose defect spontaneously closed"}]

        self.assertEqual(truth, conflict_resolver(extracted))

        # Test conflict resolution if 2 of 3 terms have identical context similarity scores

        extracted = [{"hpid": ["HP:0000729", "HP:0001631", "HP:0001631"],
                      "index": [44, 47],
                      "matched": "ASD",
                      "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                                          whose defect spontaneously closed"}]

        # Expected result remove only one term
        truth = [{"hpid": ["HP:0001631"],
                  "index": [44, 47],
                  "matched": "ASD",
                  "context": "secundum, all underwent surgical repair for ASD except for 1 individual \
                                          whose defect spontaneously closed"}]

        self.assertEqual(truth, conflict_resolver(extracted))

    def test_custom_synonyms(self):
        # test adding custom synonyms
        custom_syn = {"HP:0001263": ['DD', 'GDD']}

        hpo = Extractor(custom_synonyms=custom_syn).hpo
        truth = json.dumps([{"hpid": ["HP:0001263"], "index": [0, 3], "matched": "GDD"},
                            {"hpid": ["HP:0001263"], "index": [4, 6], "matched": "DD"}])
        self.assertEqual(hpo("GDD DD"), truth)

    def test_extract_ambiguous(self):
        # test resolver works
        hpo = Extractor(resolve_conflicts=True).hpo
        truth = json.dumps([{"hpid": ["HP:0001631"], "index": [44, 47], "matched": "asd"}])
        test1 = hpo("secundum, all underwent surgical repair for ASD except for 1 individual whose defect spontaneously closed")
        self.assertEqual(truth, test1)

    def test_conflict_instantiate(self):
        # Test that reinstantiation does not affect results
        ex = Extractor(resolve_conflicts=True)
        self.assertEqual(ex.resolve_conflicts, True)
        res = json.loads(ex.hpo("ASD"))
        self.assertEqual(len(res[0]['hpid']), 1)

        ex = Extractor(resolve_conflicts=False)
        self.assertEqual(ex.resolve_conflicts, False)
        res = json.loads(ex.hpo("ASD"))
        self.assertEqual(len(res[0]['hpid']), 2)

        ex = Extractor(resolve_conflicts=True)
        self.assertEqual(ex.resolve_conflicts, True)
        res = json.loads(ex.hpo("ASD"))
        self.assertEqual(len(res[0]['hpid']), 1)