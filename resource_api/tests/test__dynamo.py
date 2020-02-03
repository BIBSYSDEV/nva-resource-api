from unittest import TestCase

from boto3.resources.base import ServiceResource

from common import dynamo


class TestDynamo(TestCase):
    def test_validate_region(self):
        ddb = dynamo.DynamoDB()

        region = 'Lancaster'
        self.assertRaisesRegex(ValueError, 'Region "%s" is invalid' % region, ddb.connect, region)

    def test_connect(self):
        ddb = dynamo.DynamoDB()

        _dynamo = ddb.connect('eu-west-1')
        self.assertTrue(isinstance(_dynamo, ServiceResource), 'Type was not DDB')
