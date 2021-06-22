from unittest.mock import patch

import pytest

from conftest import Author
from django_factories import Factory, SubFactory


def test_factory_repr():
    assert repr(Factory(Author)) == "Factory(Author)"
    assert repr(Factory(Author, name="foo")) == "Factory(Author, name='foo')"


def test_subfactory_repr():
    assert repr(SubFactory()) == "SubFactory()"
    assert repr(SubFactory("author_factory")) == 'SubFactory("author_factory")'


def test_subfactory_repr_custom(chapter_factory, watterson_book_factory):
    assert (
        str(chapter_factory.__self__)
        == 'Factory(Chapter, book=SubFactory("book_factory"))'
    )
    assert (
        str(watterson_book_factory.__self__)
        == 'Factory(Book, author=SubFactory("watterson_author_factory"))'
    )


def test_book_factory(book_factory):
    book = book_factory()
    assert book.title == "Default Title"
    assert book.author.name == "Default Author"


def test_author_factory(author_factory):
    author = author_factory(name="Someone else")
    assert author.name == "Someone else"


def test_custom_author(book_factory):
    book = book_factory(author__name="Someone else")
    assert book.author.name == "Someone else"


def test_custom_author_as_object(book_factory):
    book = book_factory(author=Author(name="Someone else"))
    assert book.author.name == "Someone else"


def test_nested_relationship(chapter_factory):
    assert (
        chapter_factory(book__author__name="Someone else").book.author.name
        == "Someone else"
    )


@patch("conftest.Author._default_manager.create")
def test_create_instance(mocked_create, author_factory):
    author_factory.__self__.use_db = True
    author_factory()
    assert mocked_create.called


def test_non_model_fields(book_factory):
    with pytest.raises(TypeError) as e:
        book_factory(author__name="Someone else", author__age=57, foo="bar")
    assert "unexpected keyword argument 'foo'" in str(e.value)


def test_subfactory_kwargs_without_subfactory(book_factory, caplog):
    author = Author(name="David Foster Wallace")
    with pytest.raises(TypeError) as e:
        book_factory(author=author, author__name="Someone else")
    assert "unexpected keyword argument 'author__name'" in str(e.value)


def test_mixing_subfactory_with_kwarg(book_factory, caplog):
    kwargs = {"author": SubFactory(), "author__name": "Someone else"}
    book = book_factory(**kwargs)
    assert book.author.name == "Someone else"


def test_run_factories(book_factory):
    book = book_factory(author__name="Someone else")
    assert repr(book.author) == "<Author: Someone else>"


def test_run_factories_defaults_only(book_factory):
    kwargs = {"author": SubFactory()}
    result = book_factory.__self__.run_subfactories(kwargs)
    assert str(result) == "{'author': <Author: Default Author>}"


def test_named_fixture_as_default(watterson_book_factory):
    book = watterson_book_factory()
    assert book.author.name == "Bill Watterson"


def test_no_callable_as_subfactory_arg(caplog, broken_factory):
    with pytest.raises(TypeError):
        broken_factory()
    assert "Is the SubFactory function callable?" in caplog.records[0].msg


def test_custom_subfactory(watterson_book_factory):
    book = watterson_book_factory()
    assert book.author.name == "Bill Watterson"


def test_named_fixture_overridden(watterson_book_factory):
    book = watterson_book_factory(author__name="Not Bill Watterson")
    assert book.author.name == "Not Bill Watterson"


def test_no_error_due_to_auto_factory(model_b_factory):
    from conftest import ModelA

    model_b_factory(model_a=ModelA())


def test_customized_factory(enumerated_book_factory):
    enumerated_book_factory()
    assert enumerated_book_factory().title == "Book 2"
