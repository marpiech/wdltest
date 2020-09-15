# wdltest

python3 setup.py sdist bdist_wheel; twine upload --repository testpypi dist/wdltest-0.0.4*; pip3 install --upgrade --index-url https://test.pypi.org/simple/ --no-deps wdltest==0.0.4
