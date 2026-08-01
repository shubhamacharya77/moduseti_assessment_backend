from typing import Any
from models.evidence import EvidenceItem, EvidencePackage


class EvidenceCollector:
    """Centralized aggregator that normalizes, deduplicates, and packages multi-tool evidence items."""

    def collect_and_package(
        self,
        tool_outputs: list[list[EvidenceItem] | EvidenceItem],
        user_question: str = "Executive Strategy Inquiry"
    ) -> EvidencePackage:
        """Flattens tool outputs, removes duplicates, validates schemas, and builds EvidencePackage.

        Args:
            tool_outputs: List of EvidenceItem objects or lists of EvidenceItem objects from tools.
            user_question: Executive question context.

        Returns:
            Validated immutable EvidencePackage object.
        """
        flattened_items: list[EvidenceItem] = []

        # 1. Flatten multi-tool output structures
        for output in tool_outputs:
            if isinstance(output, list):
                for item in output:
                    if isinstance(item, EvidenceItem):
                        flattened_items.append(item)
            elif isinstance(output, EvidenceItem):
                flattened_items.append(output)

        # 2. Deduplicate evidence items by composite key (source, title)
        seen_keys: set[tuple[str, str]] = set()
        deduplicated_items: list[EvidenceItem] = []

        for item in flattened_items:
            key = (item.source.strip().lower(), item.title.strip().lower())
            if key not in seen_keys:
                seen_keys.add(key)
                deduplicated_items.append(item)

        # 3. Build & return immutable EvidencePackage
        return EvidencePackage(
            question=user_question,
            items=deduplicated_items
        )
