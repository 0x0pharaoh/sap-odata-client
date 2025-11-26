class SAPClientError(Exception):
    pass


class SAPAuthError(SAPClientError):
    pass


class SAPRequestError(SAPClientError):
    pass
