
Docs generated with the [Spinx Book Theme](https://sphinx-book-theme.readthedocs.io/en/latest/tutorials/get-started.html).

In the poetry2nix development environment,

```
nix develop ..#poetry2nix
```

[run the build](https://www.sphinx-doc.org/en/master/usage/quickstart.html#running-the-build)

```
make html
```

Manually update the https://github.com/pyedifice/pyedifice.github.io website:

```
rm -r ../../pyedifice.github.io/*
```
```
cp -r build/html/* ../../pyedifice.github.io/
```
