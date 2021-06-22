from itertools import count

import django
import pytest
from django.conf import settings
from django.db import models

from django_factories import Factory, SubFactory

settings.configure(DEBUG=False)
django.setup()


class Author(models.Model):
    name = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()

    class Meta:
        app_label = "dummy_app"

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    class Meta:
        app_label = "dummy_app"


class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Chapter 1")

    class Meta:
        app_label = "dummy_app"


class ModelA(models.Model):
    class Meta:
        app_label = "dummy_app"


class ModelB(models.Model):
    model_a = models.ForeignKey(ModelA, on_delete=models.CASCADE)

    class Meta:
        app_label = "dummy_app"


@pytest.fixture
def author_factory(request):
    factory = Factory(Author, name="Default Author")
    return factory(request)


@pytest.fixture
def book_factory(request):
    return Factory(Book, title="Default Title")(request)


@pytest.fixture
def watterson_author_factory(request):
    return Factory(Author, name="Bill Watterson")(request)


@pytest.fixture
def bill_watterson(author_factory):
    return author_factory(name="Bill Watterson")


@pytest.fixture
def watterson_book_factory(request, watterson_author_factory):
    """This factory builds objects with "Bill Watterson" as default author."""
    return Factory(Book, author=SubFactory("watterson_author_factory"))(request)


@pytest.fixture
def broken_factory(request):
    return Factory(Book, author=SubFactory("bill_watterson"))(request)


@pytest.fixture
def chapter_factory(request):
    return Factory(Chapter)(request)


@pytest.fixture
def model_b_factory(request):
    """Please note that a factory function for ModelA is missing intentionally."""
    return Factory(ModelB)(request)


@pytest.fixture
def enumerated_book_factory(request):
    counter = count(1)

    class BookFactory(Factory):
        model = Book

        def create(self, **kwargs):
            return super().create(**kwargs, title=f"Book {next(counter)}")

    return BookFactory()(request)
