import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.conf import settings

# -------------------------------------------------------------------
# Clase que las migraciones antiguas esperan: CorporateEmailValidator
# -------------------------------------------------------------------
class CorporateEmailValidator:
    """
    Valida que el email pertenezca a un dominio corporativo.
    Compatible con migraciones (tiene deconstruct y __eq__).
    """
    def __init__(self, domains=None):
        # Permite fijar dominios en la migración o usar settings
        self.domains = [d.lower() for d in (domains or [])]

    def __call__(self, value):
        email = (value or "").lower()
        domains = self.domains or [d.lower() for d in getattr(settings, "CORPORATE_EMAIL_DOMAINS", [])]
        if not any(email.endswith(f"@{d}") for d in domains):
            raise ValidationError(
                _("Debes usar tu correo corporativo (%(domains)s)."),
                params={"domains": ", ".join(domains) or "—"}
            )

    # Necesario para que Django pueda serializar el validador en migraciones
    def deconstruct(self):
        path = f"{self.__module__}.{self.__class__.__name__}"
        kwargs = {}
        if self.domains:
            kwargs["domains"] = self.domains
        return (path, (), kwargs)

    # Para que Django compare instancias en migraciones sin considerarlas distintas
    def __eq__(self, other):
        return isinstance(other, CorporateEmailValidator) and self.domains == other.domains


# -------------------------------------------------------------------
# Wrapper conveniente (lo puede usar tu código actual si quieres)
# -------------------------------------------------------------------
def validate_corporate_email(email: str):
    return CorporateEmailValidator()(email)


# -------------------------------------------------------------------
# Validador de complejidad de contraseñas (PRD)
# -------------------------------------------------------------------
class PasswordComplexityValidator:
    """
    - Al menos 8 caracteres
    - 1 mayúscula, 1 minúscula, 1 dígito, 1 caracter especial
    """
    def validate(self, password, user=None):
        if len(password or "") < 8:
            raise ValidationError(_("La contraseña debe tener al menos 8 caracteres."))
        if not re.search(r'[A-Z]', password or ""):
            raise ValidationError(_("La contraseña debe incluir al menos una mayúscula."))
        if not re.search(r'[a-z]', password or ""):
            raise ValidationError(_("La contraseña debe incluir al menos una minúscula."))
        if not re.search(r'\d', password or ""):
            raise ValidationError(_("La contraseña debe incluir al menos un número."))
        if not re.search(r'[^\w\s]', password or ""):
            raise ValidationError(_("La contraseña debe incluir al menos un caracter especial."))

    def get_help_text(self):
        return _("Mínimo 8 caracteres, con mayúscula, minúscula, número y caracter especial.")
