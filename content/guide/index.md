# Getting started

## Installation

Install the package using `pip`.

<Code lang="bash">
pip install tcom
</Code>

## Usage

The first thing you must do in your app is to create a "catalog" of components. This is the object that manage the components and its global settings. Then, you add to the catalog the folder(s) with your components.

<Code lang="python">
from tcom import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")
</Code>

You use the catalog to render a parent component from your views:

<Code lang="python">
def myview():
  ...
  return catalog.render(
    "ComponentName",
    title="Lorem ipsum",
    message="Hello",
  )
</Code>

## Components

The components are `.jinja` files. The name of the file before the first dot is the component name and it **must** begin with an uppercase letter. This is the only way to distinguish themn from regular HTML tags.

For example, if the filename es `PersonForm.jinja`, the name of the component is `PersonForm` and can be used like `{{ '<PersonForm>...</PersonForm>'|e }}`.

A component can begin with a Jinja comment where it declare what attributes it takes. This metadata is in [TOML](https://toml.io/) format.

<Code lang="html+jinja">
<h1>{ { title }}</h1>
</Code>
