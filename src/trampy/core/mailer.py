from __future__ import annotations

import os
import ssl
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Iterable, Optional, Sequence, Tuple


@dataclass(frozen=True)
class SMTPSettings:
    host: str
    port: int
    user: Optional[str] = None
    password: Optional[str] = None
    use_starttls: bool = True
    use_ssl: bool = False
    timeout_sec: int = 20
    from_addr: Optional[str] = None

    @staticmethod
    def from_config(cfg, prefix: str = "SMTP_") -> "SMTPSettings":
        host = cfg.get(prefix + "HOST")
        port = int(cfg.get(prefix + "PORT", 587))
        use_starttls = bool(cfg.get(prefix + "USE_STARTTLS", True))
        use_ssl = bool(cfg.get(prefix + "USE_SSL", False))
        user = cfg.get(prefix + "USER", None)
        password = cfg.get(prefix + "PASS", None)
        timeout_sec = int(cfg.get(prefix + "TIMEOUT_SEC", 20))
        from_addr = cfg.get(prefix + "FROM", user)

        if not host:
            raise ValueError("SMTP host no configurat (SMTP_HOST).")

        # Evitem combinació incoherent
        if use_ssl and use_starttls:
            raise ValueError("Config SMTP incoherent: no pots tenir USE_SSL i USE_STARTTLS a la vegada.")

        return SMTPSettings(
            host=host,
            port=port,
            user=user,
            password=password,
            use_starttls=use_starttls,
            use_ssl=use_ssl,
            timeout_sec=timeout_sec,
            from_addr=from_addr,
        )


class EmailClient:
    def __init__(self, settings: SMTPSettings):
        self.settings = settings

    def send(
        self,
        subject: str,
        to: Sequence[str],
        body_text: str,
        body_html: Optional[str] = None,
        cc: Optional[Sequence[str]] = None,
        bcc: Optional[Sequence[str]] = None,
        attachments: Optional[Sequence[Tuple[str, bytes, str]]] = None,
    ) -> None:
        if not to:
            raise ValueError("No hi ha destinataris (to).")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings.from_addr or (self.settings.user or "")
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)

        recipients = list(to) + list(cc or []) + list(bcc or [])

        # Cos
        msg.set_content(body_text)
        if body_html:
            msg.add_alternative(body_html, subtype="html")

        # Adjunts: (filename, content_bytes, mime_type)
        for att in attachments or []:
            filename, content, mime_type = att
            maintype, subtype = mime_type.split("/", 1)
            msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

        # Connexió SMTP
        context = ssl.create_default_context()

        if self.settings.use_ssl:
            with smtplib.SMTP_SSL(self.settings.host, self.settings.port, timeout=self.settings.timeout_sec, context=context) as s:
                self._login_if_needed(s)
                s.send_message(msg, to_addrs=recipients)
        else:
            with smtplib.SMTP(self.settings.host, self.settings.port, timeout=self.settings.timeout_sec) as s:
                s.ehlo()
                if self.settings.use_starttls:
                    s.starttls(context=context)
                    s.ehlo()
                self._login_if_needed(s)
                s.send_message(msg, to_addrs=recipients)

    def _login_if_needed(self, s: smtplib.SMTP) -> None:
        if self.settings.user and self.settings.password:
            s.login(self.settings.user, self.settings.password)