class DomainError(Exception):
    pass


class UserAlreadyExistsError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class TokenError(DomainError):
    pass
