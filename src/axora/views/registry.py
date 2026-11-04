from typing import Any
from axora.views.interface import ViewBuilderInterface, ViewPayload


class ViewRegistry:
    """Central extensible registry storing view builders."""

    def __init__(self) -> None:
        self._builders: dict[str, ViewBuilderInterface] = {}

    def register(self, builder: ViewBuilderInterface) -> None:
        if builder.view_type in self._builders:
            raise ValueError(f"View builder for type '{builder.view_type}' is already registered.")
        self._builders[builder.view_type] = builder

    def get(self, view_type: str) -> ViewBuilderInterface:
        if view_type not in self._builders:
            raise ValueError(f"Unknown view type: '{view_type}'. Registered: {list(self._builders.keys())}")
        return self._builders[view_type]

    def has(self, view_type: str) -> bool:
        return view_type in self._builders

    def list_types(self) -> list[str]:
        return list(self._builders.keys())

    def build_view(self, view_type: str, data: Any, **kwargs: Any) -> ViewPayload:
        builder = self.get(view_type)
        return builder.build(data, **kwargs)
