import logging
from typing import TYPE_CHECKING, Any, Type
from axora.extensions.bdd.interface import DatabaseConnectorInterface

if TYPE_CHECKING:
    from axora.semantic.service import SemanticModelService
else:
    SemanticModelService = Any

logger = logging.getLogger("axora.extensions.bdd.registry")


class ConnectorRegistry:
    """Registry managing database connector drivers indexed by URL scheme."""

    def __init__(self) -> None:
        self._drivers: dict[str, Type[DatabaseConnectorInterface]] = {}

    def register(self, scheme: str, connector_cls: Type[DatabaseConnectorInterface]) -> None:
        """Registers a connector class for a specific URL scheme (e.g. 'postgresql', 'sqlite+aiosqlite')."""
        normalized_scheme = scheme.lower().strip()
        self._drivers[normalized_scheme] = connector_cls
        logger.debug(f"[CONNECTOR REGISTRY] Registered driver for scheme '{normalized_scheme}': {connector_cls.__name__}")

    def get(self, scheme: str) -> Type[DatabaseConnectorInterface]:
        """Retrieves the registered connector class for a given scheme."""
        normalized_scheme = scheme.lower().strip()
        if normalized_scheme not in self._drivers:
            available = list(self._drivers.keys())
            raise ValueError(
                f"No database connector registered for URL scheme '{scheme}'. Available schemes: {available}"
            )
        return self._drivers[normalized_scheme]

    def has_scheme(self, scheme: str) -> bool:
        """Checks if a scheme has a registered connector."""
        return scheme.lower().strip() in self._drivers

    def list_schemes(self) -> list[str]:
        """Returns all currently registered URL schemes."""
        return sorted(list(self._drivers.keys()))

    def create(
        self,
        url: str,
        semantic_service: SemanticModelService | None = None,
        **kwargs: Any,
    ) -> DatabaseConnectorInterface:
        """Instantiates the appropriate connector driver based on the URL scheme."""
        scheme = self._extract_scheme(url)
        connector_cls = self.get(scheme)
        return connector_cls(url=url, semantic_service=semantic_service, **kwargs)

    def _extract_scheme(self, url: str) -> str:
        """Extracts the protocol scheme from a standard database connection URL."""
        if "://" in url:
            return url.split("://", 1)[0].lower().strip()
        raise ValueError(
            f"Invalid database URL: '{url}'. Expected standard URI format with '://' delimiter."
        )
