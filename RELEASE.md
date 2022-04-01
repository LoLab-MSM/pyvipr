# How to release

## Install release tool

```bash
pip install twine
pip install wheel
```

## Prepare release

- To release a new version of pyvipr on PyPI:

* Update version_info and frontend_version in _version.py (set release version, remove 'dev')
* Update frontend version in js/package.json and pyvipr/staticlab/package.json
* git add the _version.py file and git commit
* Build the distribution (both )

```bash
python setup.py sdist
python setup.py bdist_wheel --universal
```

* Tag it

```bash
git tag -a X.X.X -m "Version x.x.x release"
```

Update _version.py (add 'dev' and increment minor)
git add and git commit
git push
git push --tags

- To release a new version of pyvipr on NPM:

```
# clean out the `dist` and `node_modules` directories
Update package.json
git clean -fdx
npm install
npm publish
```