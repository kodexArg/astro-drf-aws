"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-25-page-context-assistant]] · [[adr-14-auth]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

"""Permission gate for the page-context assistant ([[adr-25-page-context-assistant]]).

`CanUseAssistant` shares the check *shape* of `CanUseRouter`: the requesting
user must be a member of the Django group `admins` or `ai_operators`
([[API]] — POST /api/assistant/ask/). The decision reads Django group
membership only, never a token claim ([[adr-14-auth]] rule 2).
"""

from apps.router.permissions import AI_OPERATORS_GROUP
from apps.users.permissions import ADMINS_GROUP, HasAnyGroup


class CanUseAssistant(HasAnyGroup):
    group_names = (ADMINS_GROUP, AI_OPERATORS_GROUP)
