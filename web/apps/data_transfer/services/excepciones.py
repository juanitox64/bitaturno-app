class ErrorTransferencia(Exception):
    """Error controlado y apto para mostrarse al administrador."""


class PaqueteInvalido(ErrorTransferencia):
    """El paquete no cumple el formato o las restricciones de seguridad."""


class ConflictoImportacion(ErrorTransferencia):
    """La política seleccionada exige detenerse ante un registro existente."""

