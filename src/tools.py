from datetime import datetime, timedelta

class Throttle(object):
    def __init__(self, seconds=5, datetime_class=datetime):
        self.dict = {}
        self.ttl = timedelta(seconds=seconds)
        self.dtclass = datetime_class

    def _has_passed(self, value, now=None):
        now = now or self.dtclass.now()
        return value + self.ttl < now

    def _invalidate(self):
        now = self.dtclass.now()
        d = self.dict
        dc = d.copy()
        for (k, v) in dc.iteritems():
            if self._has_passed(v, now):
                del(d[k])

    def is_throttled(self, key):
        self._invalidate()
        ans = key in self.dict
        if not ans:
            self.dict[key] = self.dtclass.now()
        return ans

   
class DummyDatetime(object):
    def __init__(self):
        self.dt = datetime.fromtimestamp(0)

    def advance(self, seconds):
        self.dt += timedelta(seconds=seconds)

    def now(self):
        return self.dt

if __name__ == '__main__':
    # Test the Throttle class
    dt = DummyDatetime() # t=0
    th = Throttle(seconds=10, datetime_class=dt)
    assert th.is_throttled("a") == False, 't=0' # will expire in t=10
    dt.advance(5) # t=5
    assert th.is_throttled("a") == True, 't=5'
    dt.advance(10) # t=15
    assert th.is_throttled("a") == False, 't=15' # will expire in t=25
    dt.advance(5) # t=20
    assert th.is_throttled("a") == True, 't=20'
    dt.advance(10) # t=30
    assert th.is_throttled("a") == False, 't=30'
