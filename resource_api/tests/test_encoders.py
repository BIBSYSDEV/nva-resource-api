import os
import json
from resource_api.common.encoders import DecimalEncoder
from resource_api.common.encoders import as_Decimal
from decimal import Decimal
import sys

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
import unittest

class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_decimal_encoder(self):
        sample_dict = {
            "sample1": Decimal("100"),
            "sample2": [ Decimal("2.0"), Decimal("2.1") ],
            "sample3": Decimal("3.1415"),
            "other": "hello!"
        }

        sample_dict_encoded_as_json_string = json.dumps(sample_dict, cls=DecimalEncoder)

        sample_dict_recreated = json.loads(sample_dict_encoded_as_json_string, object_hook=as_Decimal)

        self.assertEqual(sample_dict,sample_dict_recreated)
