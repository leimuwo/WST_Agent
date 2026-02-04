from __future__ import annotations

from typing import Any, Dict


class PlatformClient:
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
