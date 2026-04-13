"""Exception hierarchy for DataLens AI."""


class DataLensError(Exception):
    """Base exception for DataLens AI."""


class IngestionError(DataLensError):
    """Error loading or processing data."""


class UnsupportedFormatError(IngestionError):
    """Unsupported file format."""


class QueryError(DataLensError):
    """Error executing a query."""


class SQLGenerationError(QueryError):
    """Error generating SQL from natural language."""


class SQLValidationError(QueryError):
    """Generated SQL failed validation."""


class SQLExecutionError(QueryError):
    """SQL execution failed."""


class ProviderError(DataLensError):
    """Error with an AI provider."""


class ProviderUnavailableError(ProviderError):
    """AI provider not available."""


class VisualizationError(DataLensError):
    """Error creating a visualization."""


class ChartSelectionError(VisualizationError):
    """Error selecting chart type."""


class ExportError(DataLensError):
    """Error exporting report."""


class ConfigError(DataLensError):
    """Configuration error."""
