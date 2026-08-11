"""Shared email-sending function used by the daily digest script.

Sends via "onboarding@resend.dev", Resend's sandbox sender address, which
works without verifying a custom domain. In sandbox mode, emails can only
be delivered to the email address associated with the Resend account
itself, until a custom domain is verified.
"""

import logging

import resend

from app.config import settings

resend.api_key = settings.resend_api_key

logger = logging.getLogger(__name__)


def send_digest_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send a single digest email. Returns True on success, False on any
    failure (logged, not raised) so one failed send doesn't crash a batch
    send to many subscribers.
    """
    try:
        resend.Emails.send(
            {
                "from": "onboarding@resend.dev",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
        )
        return True
    except Exception as exc:
        logger.error("send_digest_email: failed to send to '%s': %s", to_email, exc)
        return False
