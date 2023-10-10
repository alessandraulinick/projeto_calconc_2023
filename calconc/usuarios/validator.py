from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_cep(value):
    value = re.sub('[^0-9]', '', value)
    if len(value) != 8:
        raise ValidationError(
            _("o CEP '%(value)s' não é um válido."),
            params={"value": value},
        )


def validate_fone(value):
    value = re.sub('[^0-9]', '', value)
    if not bool(re.match('^([14689][0-9]|2[12478]|3([1-5]|[7-8])|5([13-5])|7[193-7])9[0-9]{8}$', value)):
        raise ValidationError(
            _("O fone '%(value)s' não é válido"),
            params={"value": value},
        )


def validate_cpf_cnpj(value):
    value = re.sub('[^0-9]', '', value)
    if len(value) != 11 and len(value) != 14:
        raise ValidationError(
            _("O CPF ou CNPJ '%(value)s' não é um válido."),
            params={"value": value},
        )


def validate_ie(value):
    value = re.sub('[^0-9]', '', value)
    if len(value) != 9:
        raise ValidationError(
            _("A IE '%(value)s' não é válida"),
            params={"value": value},
        )
