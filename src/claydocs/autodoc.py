import inspect
import typing as t
from dataclasses import dataclass, field
from importlib import import_module

from docstring_parser import Docstring, parse


@dataclass
class Autodoc:
    type: str = ""
    name: str = ""
    signature: str = ""
    bases: list[str] = field(default_factory=list)
    doc: Docstring | None = None
    methods: list["Autodoc"] = field(default_factory=list)


def autodoc(name: str) -> Autodoc:
    module_name, obj_name = name.rsplit(".", 1)
    module = import_module(module_name)
    assert module
    obj = getattr(module, obj_name, None)
    assert obj
    return autodoc_obj(obj)


def autodoc_obj(obj: t.Any) -> Autodoc:
    if inspect.isclass(obj):
        return autodoc_class(obj)
    elif inspect.isfunction(obj):
        return autodoc_function(obj)
    else:
        return Autodoc()


def autodoc_class(obj: t.Any, type: str = "class") -> Autodoc:
    init = getattr(obj, "__init__", None)
    docstring = obj.__doc__ or init.__doc__ or ""
    obj_name = obj.__name__
    members = [v for k, v in inspect.getmembers(obj) if k[0] != "_"]

    return Autodoc(
        type=type,
        name=obj_name,
        bases=[
            base.__name__
            for base in obj.__bases__
            if base.__name__ != "object"
        ],
        doc= parse(docstring),
        signature=get_signature(obj_name, init),
        methods=[
            autodoc_function(meth, type="method")
            for meth in members
            if inspect.isfunction(meth)
        ]
    )


def autodoc_function(obj: t.Any, type: str = "function") -> Autodoc:
    docstring = obj.__doc__ or ""
    obj_name = obj.__name__

    return Autodoc(
        type=type,
        name=obj_name,
        signature=get_signature(obj_name, obj),
        doc=parse(docstring),
    )


def get_signature(obj_name: str, obj: t.Any, split_at: int = 70) -> str:
    sig = inspect.signature(obj)
    str_sig = str(sig).replace("(self, ", "(").replace("(self)", "()")
    fullsig = f"{obj_name}{str_sig}"
    if len(fullsig) < split_at:
        return fullsig

    fullsig = (
        fullsig
        .replace("*, ", "\n    *, ")
        .replace(", **", ",\n    **")
        .replace("(", "(\n    ", 1)
    )
    for name in sig.parameters:
        fullsig = fullsig.replace(f", {name}", f",\n    {name}")

    return fullsig.replace(") ->", "\n) ->")
