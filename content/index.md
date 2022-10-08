---
title: Meh
component: HomePage
---

A component can begin with a Jinja comment where it declare what arguments it takes.

```html+jinja
{#def title, message='Hi' #}

<h1>{{ title }}</h1>
<div>{{ message }}. This is my component</div>
```
