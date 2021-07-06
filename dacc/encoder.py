import datetime
import decimal
from flask.json import JSONEncoder


class PrettyFloat(float):
    def __repr__(self):
        return "%.15g" % self


class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder to deal with non-serialized JSON types"""

    def default(self, o):
        print("o : {}".format(o))
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, decimal.Decimal):
            return PrettyFloat(o)
        return super().default(o)
