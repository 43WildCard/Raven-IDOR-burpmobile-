from __future__ import annotations

from .identifiers import candidates_from_request


def analyze(request):
    return candidates_from_request(request)
