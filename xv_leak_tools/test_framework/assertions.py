# All test failures should be represented by this exception
class LeakTestFail(Exception):
    pass

class Assertions:

    # pylint: disable=invalid-name,no-self-use,too-many-arguments

    def failTest(self, custom_msg=None):
        raise LeakTestFail(custom_msg or 'Failing test manually')

    def assertTrue(self, a, custom_msg=None):
        if not a:
            raise LeakTestFail(custom_msg or "{} is not True".format(a))

    def assertFalse(self, a, custom_msg=None):
        if a:
            raise LeakTestFail(custom_msg or "{} is not False".format(a))

    def assertIsNone(self, a, custom_msg=None):
        if a is not None:
            raise LeakTestFail(custom_msg or "{} is not None".format(a))

    def assertIsNotNone(self, a, custom_msg=None):
        if a is None:
            raise LeakTestFail(custom_msg or "unexpectedly got None")

    def assertIs(self, a, b, custom_msg=None):
        if a is not b:
            raise LeakTestFail(custom_msg or "{} is not {}".format(a, b))

    def assertIsNot(self, a, b, custom_msg=None):
        if a is b:
            raise LeakTestFail(custom_msg or "{} is unexpectedly {}".format(a, b))

    def assertEqual(self, a, b, custom_msg=None):
        if a != b:
            raise LeakTestFail(custom_msg or "{} not equal to {}".format(a, b))

    def assertNotEqual(self, a, b, custom_msg=None):
        if a == b:
            raise LeakTestFail(custom_msg or "{} equal to {}".format(a, b))

    def assertGreater(self, a, b, custom_msg=None):
        if not a > b:
            raise LeakTestFail(custom_msg or "%s not greater than %s" % (a, b))

    def assertGreaterEqual(self, a, b, custom_msg=None):
        if not a >= b:
            raise LeakTestFail(custom_msg or "%s not greater than or equal to %s" % (a, b))

    def assertLess(self, a, b, custom_msg=None):
        if not a < b:
            raise LeakTestFail(custom_msg or "%s not less than %s" % (a, b))

    def assertLessEqual(self, a, b, custom_msg=None):
        if not a <= b:
            raise LeakTestFail(custom_msg or "%s not less than or equal to %s" % (a, b))

    def assertIsIn(self, a, b, custom_msg=None):
        if a not in b:
            raise LeakTestFail(custom_msg or "{} was not in {}".format(a, b))

    def assertIsNotIn(self, a, b, custom_msg=None):
        if a in b:
            raise LeakTestFail(custom_msg or "{} was unexpectedly in {}".format(a, b))

    def assertEmpty(self, a, custom_msg=None):
        if len(a) != 0:
            raise LeakTestFail(custom_msg or "object was not empty: {}".format(a))

    def assertNotEmpty(self, a, custom_msg=None):
        if len(a) == 0:
            raise LeakTestFail(custom_msg or 'object was unexpectedly empty')

    def assertNoException(self, func, args=None, kwargs=None, allowed_exceptions=None,
                          custom_msg=None):

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if allowed_exceptions is None:
            allowed_exceptions = []

        try:
            return func(*args, **kwargs)
        except Exception as ex:
            for allowed_exception in allowed_exceptions:
                if isinstance(ex, allowed_exception):
                    return
            raise LeakTestFail(custom_msg or "Expected no exception, but got: {}".format(ex))
