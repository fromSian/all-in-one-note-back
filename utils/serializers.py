from utils.encryption import RSAEncryption

from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured


class EncryptSerializerMixin:
    __ALL__ = "__all__"
    encryption: None

    def _get_encrypt_fields(self, representation):
        encrypted_fields = getattr(self.Meta, "encrypt_fields", None)
        excluded_fields = getattr(self.Meta, "excluded_fields", None)
        field_list = list()
        model_class = getattr(self.Meta, "model")

        if encrypted_fields is None:
            return None

        if (
            encrypted_fields
            and encrypted_fields != self.__ALL__
            and not isinstance(encrypted_fields, (list, tuple))
        ):
            raise TypeError(
                'The `encrypt_fields` option must be a list or tuple or "__all__".Got %s.'
                % type(encrypted_fields).__name__
            )

        if excluded_fields and not isinstance(excluded_fields, (list, tuple)):
            raise TypeError(
                "the `excluded_fields` option must be a list or tuple. Got %s."
                % type(excluded_fields).__name__
            )

        if encrypted_fields == self.__ALL__:
            field_list = [key for key, value in representation.items()]
        else:
            for field in encrypted_fields:
                if not (field in representation.keys()):
                    raise ImproperlyConfigured(
                        "Field name `%s` is not valid for model `%s`."
                        % (field, model_class.__name__)
                    )
            for key in representation.keys():
                if key in encrypted_fields:
                    field_list.append(key)

        if excluded_fields is not None:
            for field in excluded_fields:
                if not (field in representation.keys()):
                    raise ImproperlyConfigured(
                        "Field name `%s` is not valid for model `%s`."
                        % (field, model_class.__name__)
                    )
                else:
                    field_list.remove(field)
        return field_list

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        field_list = self._get_encrypt_fields(representation)
        if field_list is None:
            return representation

        model_class = getattr(self.Meta, "model")

        self.encryption = getattr(self.Meta, "encryption_class")()

        for key, value in representation.items():
            if key in field_list:
                if isinstance(representation[key], str):
                    representation[key] = self.encryption.encrypt(value)
                else:
                    raise ImproperlyConfigured(
                        "Field name `%s` is not able to be encrypted for model `%s`."
                        % (key, model_class.__name__)
                    )
        return representation

    def to_internal_value(self, data):

        field_list = self._get_encrypt_fields(data)
        if field_list is None:
            return super().to_internal_value(data)

        model_class = getattr(self.Meta, "model")

        self.encryption = getattr(self.Meta, "encryption_class")()

        _data = data.copy()
        for key, value in _data.items():
            if key in field_list:
                if isinstance(value, str):
                    _data.__setitem__(key, self.encryption.decrypt(value))
                else:
                    raise ImproperlyConfigured(
                        "Field name `%s` is not able to be decrypted for model `%s`."
                        % (key, model_class.__name__)
                    )
        return super().to_internal_value(_data)
