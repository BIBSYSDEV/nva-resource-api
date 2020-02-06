import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return {'__Decimal__': str(obj)}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def as_Decimal(dct):
    if '__Decimal__' in dct:
        return decimal.Decimal(dct['__Decimal__'])
    return dct