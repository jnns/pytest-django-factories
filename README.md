# pytest-django-factories

![Python package](https://github.com/jnns/pytest-django-factories/workflows/Python%20package/badge.svg)

Factories for your Django models that can be used as Pytest fixtures. 
Re-use them implicitly for instantiating related objects without much boilerplate code.

```python
>>> book = book_factory(title="Calvin & Hobbes", author__name="Bill Watterson")
>>> book
<Book: Calvin & Hobbes>
>>> book.author.name
<Author: Bill Watterson>
```

# Introduction

Write a fixture for your Django model by using the `Factory` class:

```python
# conftest.py
import pytest
from django_factories import Factory
from .models import Author

@pytest.fixture
def author_factory(request):
    factory = Factory(Author)
    return factory(request)
```

```python
# tests.py
def test_function(author_factory):
    author = author_factory(name="Bill Watterson")
    assert author.name
```

> :notebook: **Note**  
> The `request` passed to the fixture function is a pytest fixture itself and provides information about the test function requesting the fixture. 
> See [pytest documentation](https://docs.pytest.org/en/latest/reference.html#std:fixture-request). 

## Default values

A plain `Factory` will, of course, instantiate the object with the defaults given at the model definition.
If you want to set defaults for the factory specifically, you can assign pass them to the Factory:

```python
@pytest.fixture
def author_factory(request):
    defaults = {
        "first_name": "William",
        "last_name": "Watterson",
        "birthdate": "1958-07-05",
    }
    return Factory(Author, **defaults)(request)
```

## Related objects

If you want to test a model which depends on another object being present, 
the Factory class will try to look up a matching factory fixture for that `ForeignKey` field
and create the related object automatically for you.
Attributes for the related object can be specified in the same double-underscore syntax that you're familiar with from Django's queryset lookups:

```python
@pytest.fixture
def author_factory(request):
    return Factory(Author)(request)

@pytest.fixture
def book_factory(request):
    return Factory(Book)(request)

def test(book_factory):
    book = book_factory(
        author__first_name="Astrid", 
        author__last_name="Lindgren"
    )
```

This only works if there is a factory fixture available to create the related object. 
`Factory` will look for a fixture named `<field>_factory`. 
If you have a fixture that you named differently (or you have multiple fixtures for that particular model), you can specify a custom fixture name:

```python
@pytest.fixture
def book_factory(request):
    return Factory(
        Book, 
        author=SubFactory("my_author_fixture")
    )(request)
```

Passing object instances as keyword arguments instead works as well, of course:

```python
book = book_factory(
    author=Author(
        first_name="Astrid", 
        last_name="Lindgren"
    )
)
```

## Database usage

You can use `Factory` to instantiate objects in memory and also to create them in the database directly via `Model.objects.create()`. 
If your test function is [marked to use the database](https://pytest-django.readthedocs.io/en/latest/helpers.html#pytest-mark-django-db-request-database-access), the objects will be saved to the database.
Unmarked tests will only create objects in memory.

## Customizing a factory

The `Factory` can be subclassed and you can override its `create(**kwargs)` method to customize how objects are instantiated. Here's an example of an auto-enumerating factory for a Book model:

```python
@pytest.fixture
def book_factory(request):
    books = []

    class BookFactory(Factory):
        model = Book

        def create(self, **kwargs):
            book_number = len(books) + 1
            obj = super().create(**kwargs, title=f"Book {book_number}")
            books.append(obj)
            return obj

    return BookFactory()(request)
```

# Installation 

```bash
pip install pytest-django-factories
```

# Contributing

All contributions are welcome. To check out the development version and run the tests, follow these steps:

```bash
git clone https://github.com/jnns/pytest-django-factories.git
cd pytest-django-factories
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

# Similar projects

When I wrote this library, I needed a quick and easy way to create related objects using Pytest fixtures. 
I didn't know about [pytest-factoryboy](https://github.com/pytest-dev/pytest-factoryboy),
which allows registering the powerful factories from [factory_boy](https://factoryboy.readthedocs.io/) 
for Pytest's fixture dependency injection.  

Basically, *pytest-django-factories* is a less-feature-packed combination of both *factory_boy* and 
*pytest-factoryboy* that will hopefully help you get going quickly. 
