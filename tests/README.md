# Tests as learning artifacts

`test_scaffold.py` only checks that the package is healthy and that the core contracts hold
their shape. Everything else is written by the author, before the code it tests.

For every core TODO:

1. write a small hand-computed example;
2. add a failing test;
3. run it and record the failure;
4. implement the minimum code that passes;
5. add boundary and failure-mode tests;
6. explain why the test would catch a tempting wrong implementation.

The last step is the one that matters. A leakage test that passes against a broken temporal
split proves nothing — so the split test is written against a deliberately broken
implementation first, and only then against the real one.

Do not ask an agent to generate the full test suite before making your own attempt. See
[LEARNING.md](../LEARNING.md).
