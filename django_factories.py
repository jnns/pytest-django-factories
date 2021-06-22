import logging
from typing import Callable

from django.db.models.fields.related import ForeignKey, OneToOneField

__version__ = "0.2.4"
logger = logging.getLogger(__name__)


class SubFactory:
    """Marker class for invoking a factory function."""

    def __init__(self, factory_func=None):
        self.factory_func = factory_func

    def __repr__(self):
        func = self.factory_func and f'"{self.factory_func}"' or ""
        return f"SubFactory({func})"


class Factory:
    """Callable that returns a factory method for a given Django method.

    Invoke via:

        Factory(Model)(request)
    """

    def __init__(self, _model=None, **defaults):
        if _model:
            self.model = _model
        assert self.model
        self.defaults = defaults

    def __repr__(self):
        defaults = ", ".join(
            [f"{key}={value!r}" for key, value in self.defaults.items()]
        )
        if defaults:
            defaults = ", " + defaults
        return f"Factory({self.model.__name__}{defaults})"

    def __call__(self, request):
        self.request = request
        self.use_db = "django_db_setup" in request.fixturenames
        self.init_auto_factories()
        return self.create

    def init_auto_factories(self):
        """Set default value for ForeignKey fields to a SubFactory."""
        fields_to_use_subfactory = (
            ForeignKey,
            OneToOneField,
        )
        related_obj_fields = {
            f.name
            for f in self.model._meta.fields
            if isinstance(f, fields_to_use_subfactory)
        }

        # Don't set up a factory if a default has been specified manually.
        related_obj_fields -= set(self.defaults)

        for field in related_obj_fields:
            fixture_name = f"{field}_factory"
            try:
                self.request.getfixturevalue(fixture_name)
            except LookupError:
                pass
            else:
                self.defaults[field] = SubFactory(fixture_name)

    def create(self, **kwargs):
        """Factory function to be returned when factory object is called."""
        kwargs = {**self.defaults, **kwargs}
        kwargs = self.run_subfactories(kwargs)
        return self.create_instance(**kwargs)

    def run_subfactories(self, kwargs: dict) -> dict:
        """Transform dunder keywords into object instances."""
        subfactories = [k for k, v in kwargs.items() if isinstance(v, SubFactory)]
        for related_field in subfactories:
            kwargs.update(self.run_subfactory(related_field, kwargs))
        return kwargs

    def run_subfactory(self, related_field: str, kwargs: dict) -> dict:
        factory = self.get_factory(related_field)
        factory_kwargs = self.get_subfactory_kwargs(related_field, kwargs)

        for k in factory_kwargs:
            kwargs.pop(k)

        try:
            factory_kwargs = {
                k.split("__", maxsplit=1)[1]: v for k, v in factory_kwargs.items()
            }
            kwargs[related_field] = factory(**factory_kwargs)
        except TypeError:
            logger.error("Is the SubFactory function callable?")
            raise

        return kwargs

    def get_subfactory_kwargs(self, related_field, kwargs):
        """Return keyword arguments for given related field."""
        return {k: v for k, v in kwargs.items() if k.startswith(f"{related_field}__")}

    def get_factory(self, key) -> Callable:
        """Return factory function for given model if available in defaults."""
        factory = self.defaults.get(key)
        factory_function_name = factory.factory_func or f"{key}_factory"
        return self.request.getfixturevalue(factory_function_name)

    def create_instance(self, **kwargs):
        """Persist instance to database or just create in memory."""
        if self.use_db:
            return self.model._default_manager.create(**kwargs)
        return self.model(**kwargs)
