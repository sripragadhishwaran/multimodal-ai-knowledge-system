"""
Section-aware retrieval policy.

Controls how document section types influence retrieval quality
without removing sections from the knowledge base.

The policy is intentionally independent from:
- vector search
- distance calculation
- MMR
- LLM generation

This keeps section-specific retrieval behavior configurable
and testable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionPolicy:
    """
    Defines retrieval behavior for a document section.

    priority:
        Multiplicative ranking factor applied to the retrieval score.

        1.0 = no adjustment
        <1.0 = lower priority
        >1.0 = higher priority

    query_keywords:
        Keywords that indicate the user may explicitly be asking
        about this section type.
    """

    priority: float
    query_keywords: tuple[str, ...] = ()


class SectionPolicyEngine:
    """
    Determines section-aware retrieval adjustments.

    The engine does not remove chunks. It only provides a policy
    signal that the Retriever can use later during ranking.
    """

    DEFAULT_POLICY = SectionPolicy(
        priority=1.0,
    )

    POLICIES: dict[str, SectionPolicy] = {
        "content": SectionPolicy(
            priority=1.0,
        ),
        "references": SectionPolicy(
            priority=0.85,
            query_keywords=(
                "reference",
                "references",
                "source",
                "sources",
                "citation",
                "citations",
                "bibliography",
                "bibliographic",
                "works cited",
            ),
        ),
    }

    def get_policy(self, section_type: str | None) -> SectionPolicy:
        """
        Return the policy associated with a section type.

        Unknown or missing section types use the neutral default
        policy so existing retrieval behavior remains safe.
        """

        if not section_type:
            return self.DEFAULT_POLICY

        normalized = section_type.strip().lower()

        return self.POLICIES.get(
            normalized,
            self.DEFAULT_POLICY,
        )

    def is_section_requested(
        self,
        query: str,
        section_type: str | None,
    ) -> bool:
        """
        Determine whether the user's query explicitly targets
        a particular section type.

        Returns False when the section type is unknown or has
        no query keywords.
        """

        if not query or not section_type:
            return False

        policy = self.get_policy(section_type)

        if not policy.query_keywords:
            return False

        normalized_query = " ".join(query.lower().split())

        return any(keyword in normalized_query for keyword in policy.query_keywords)

    def get_priority(
        self,
        query: str,
        section_type: str | None,
    ) -> float:
        """
        Return the effective section priority for a query.

        Explicitly requested sections receive neutral priority
        so they are not penalized.

        Otherwise, the configured section priority is returned.
        """

        policy = self.get_policy(section_type)

        if self.is_section_requested(
            query=query,
            section_type=section_type,
        ):
            return 1.0

        return policy.priority
