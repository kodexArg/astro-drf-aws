"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-10-cache]] · [[adr-06-initial-stack]]
Docs: [[BACKEND]] · [[CACHE]]
LIVE-DOC:END"""

class EnsureCacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not response.has_header("Cache-Control"):
            response["Cache-Control"] = "no-store"
        return response
