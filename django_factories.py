import logging
from collections import defaultdict

from django.db.models.fields.related import ForeignKey, OneToOneField

__version__ = "0.2.3"
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
        self.transform_dunder_keys(kwargs)
        self.run_subfactories(kwargs)
        return self.create_instance(**kwargs)

    def create_instance(self, **kwargs):
        """Persist instance to database or just create in memory."""
        if self.use_db:
            return self.model._default_manager.create(**kwargs)
        return self.model(**kwargs)

    def transform_dunder_keys(self, kwargs):
        """Merge double-underscore keys into a single dictionary key."""
        related_obj_kwargs = defaultdict(dict)
        for dunder_key in [key for key in kwargs if "__" in key]:
            model, model_attr = dunder_key.split("__", maxsplit=1)
            if self.get_factory(model) and model_attr:
                model_value = kwargs.pop(dunder_key)
                related_obj_kwargs[model][model_attr] = model_value
        kwargs.update(related_obj_kwargs)

    def get_factory(self, key):
        """Return factory function for given model if available in defaults."""
        value = self.defaults.get(key)
        if isinstance(value, SubFactory):
            factory_function_name = value.factory_func or f"{key}_factory"
            return self.request.getfixturevalue(factory_function_name)

    def run_subfactories(self, kwargs):
        for key, value in kwargs.items():
            factory = self.get_factory(key)
            if factory:
                if isinstance(value, SubFactory):
                    value = {}
                elif not isinstance(value, dict):
                    continue

                try:
                    produce = factory(**value)
                except TypeError:
                    logger.error("Is the SubFactory function callable?")
                    raise
                else:
                    kwargs[key] = produce
