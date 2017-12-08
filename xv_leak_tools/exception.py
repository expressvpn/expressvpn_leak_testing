# Base exception for all exceptions which we explicitly throw.
class XVEx(Exception):

    UNSPECIFIED = 0

    def __init__(self, message, code=UNSPECIFIED):
        super().__init__(message)
        self._code = code

    def __str__(self):
        code_msg = ''
        if self._code != 0:
            code_msg += "code: {} ".format(self.code())
        return "XVEx: {}{}".format(code_msg, Exception.__str__(self))

    def code(self):
        return self._code
