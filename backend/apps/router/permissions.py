"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-17-chatbot-two-tier]] · [[adr-18-async-mandatory]] · [[adr-07-api-and-backend]] · [[adr-14-auth]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

"""Permission gate for the chatbot router's choosing tier ([[adr-17-chatbot-two-tier]]).

`ai_operators` is a router-only group: it MUST NEVER be added to any other
permission class. `CanUseRouter` shares the check *shape* of
`apps.users.permissions.HasAnyGroup` (also used by `IsInAdminsGroup`) but
widens the accepted group set to either `admins` or `ai_operators`.
"""

from apps.users.permissions import ADMINS_GROUP, HasAnyGroup

AI_OPERATORS_GROUP = "ai_operators"


class CanUseRouter(HasAnyGroup):
    group_names = (ADMINS_GROUP, AI_OPERATORS_GROUP)
