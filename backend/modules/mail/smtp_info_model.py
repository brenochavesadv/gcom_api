class SmtpInfo:
        def __init__(
            self,
            host,
            port,
            user,
            pw,
            from_email
        ):
            self.host = host
            self.port = port
            self.user = user
            self.pw = pw
            self.from_email = from_email
