from unittest.mock import patch

from conftest import Author
from django_factories import Factory, SubFactory


def test_factory_repr():
    assert repr(Factory(Author)) == "Factory(Author)"
    assert repr(Factory(Author, name="foo")) == "Factory(Author, name='foo')"


def test_subfactory_repr():
    assert repr(SubFactory()) == "SubFactory()"
    assert repr(SubFactory("author_factory")) == 'SubFactory("author_factory")'


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


def test_transform_dunder_keys(book_factory):
    kwargs = {"author__name": "Someone else", "author__age": 57, "foo": "bar"}
    book_factory.__self__.transform_dunder_keys(kwargs)
    assert kwargs == {"author": {"name": "Someone else", "age": 57}, "foo": "bar"}


def test_run_factories(book_factory):
    kwargs = {"author": {"name": "Someone else"}}
    book_factory.__self__.run_subfactories(kwargs)
    assert str(kwargs) == "{'author': <Author: Someone else>}"


def test_run_factories_defaults_only(book_factory):
    kwargs = {"author": SubFactory()}
    book_factory.__self__.run_subfactories(kwargs)
    assert str(kwargs) == "{'author': <Author: Default Author>}"


def test_no_error_due_to_auto_factory(model_b_factory):
    from conftest import ModelA

    model_b_factory(model_a=ModelA())


def test_customized_factory(enumerated_book_factory):
    enumerated_book_factory()
    assert enumerated_book_factory().title == "Book 2"
