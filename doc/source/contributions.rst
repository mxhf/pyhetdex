Contribute to pyhetdex
**********************

How To
======

The suggested workflow for implementing bug fixes and/or new features is the
following:

* Identify or, if necessary, add to our `redmine issue tracker
  <https://luna.mpe.mpg.de/redmine/projects/pyhetdex>`_ one or more issues to
  tackle. Multiple issues can be addressed together if they belong together.
  Assign the issues to yourself.
* Create a new branch from the trunk with a name either referring to the topic
  or the issue to solve. E.g. if you need to add a new executable, tracked by
  issue #1111
  ``do_something``::

    svn cp ^/trunk ^/branches/do_something_1111\
    -m 'create branch to solve issue #1111'

* Switch to the branch::

    svn switch ^/branches/do_something_1111

* Implement the required changes and don't forget to track your progress on
  redmine. If the feature/bug fix requires a large amount of time, we suggest,
  when possible, to avoid one big commit at the end in favour of smaller
  commits. In this way, in case of breakages, is easier to traverse the branch
  history and find the offending code. For each commit you should add an entry
  in the ``Changelog`` file.

  If you work on multiple issues on the same branch, close one issue before
  proceeding to the next. When closing one issue is good habit to add in the
  description on the redmine the revision that resolves it.
* Every function or class added or modified should be adequately documented as
  described in :ref:`code_style`.

  Documentation is essential both for users and for your fellow developers to
  understand the scope and signature of functions and classes. If a new module
  is added, it should be also added to the documentation in the appropriate
  place. See the existing documentation for examples.

  Each executable should be documented and its description should contain
  enough information and examples to allow users to easily run it.
* Every functionality should be thoroughly tested for python 2.7 and 3.4 or 3.5
  in order to ensure that the code behaves as expected and that future
  modifications will not break existing functionalities. When fixing bugs, add
  tests to ensure that the bug will not repeat. For more information see
  :ref:`testing`.
* Once the issue(s) are solved and the branch is ready, merge any pending change
  **from** the trunk::

    svn merge ^/trunk

  While doing the merge, you might be asked to manually resolve one or more
  conflicts.  Once all the conflicts have been solved, commit the changes with a
  meaningful commit message, e.g.: ``merge ^/trunk into
  ^/branches/do_something_1111``.  Then rerun the test suite to make sure your
  changes do not break functionalities implemented while you were working on
  your branch.
* Then contact the maintainer of ``pyhetdex`` and ask to merge your branch **back
  to the trunk**.

Information about branching and merging can be found in the `svn book
<http://svnbook.red-bean.com/en/1.8/svn.branchmerge.html>`_. For any questions or
if you need support do not hesitate to contact the maintainer or the other
developers.

.. _code_style:

Coding style
============

All the code should be compliant with the official python style guidelines
described in :pep:`8`. To help you keep the code in spec, we suggest to install
plugins that check the code for you, like `Synstastic
<https://github.com/scrooloose/syntastic>`_ for vim or `flycheck
<http://www.flycheck.org/en/latest/>`_ for Emacs.

The code should also be thoroughly documented using the `numpy style
<https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_. See
the existing documentation for examples.

.. _testing:

Testing
=======

``pyhetdex`` uses the testing framework provided by the `pytest package
<http://pytest.org/latest/contents.html#>`_. The tests should cover every
aspect of a function or method. If exceptions are explicitly raised, this should
also tested to ensure that the implementation behaves as expected.

The preferred way to run the tests is using `tox
<https://testrun.org/tox/latest/index.html>`_, an automatised test help
package. If you have installed tox, with e.g. ``pip install tox``, you can run
it by typing::

    tox

It will take care of creating virtual environments for every supported version
of python (2.7, 3.4, 3.5 and 3.6), if it exists on the system, install
``pyhetdex``, its dependences and the packages necessary to run the tests and
runs ``py.test``.

You can run the tests for a specific python version using::

    py.test

or::

    python setup.py test

The latter command fetches all the needed dependences, among others ``pytest``
itself, will be fetched and installed in a ``.eggs`` directory. Then it will
run ``py.test``. This command might fail when running in a virtual environment.
If you get ``ImportError: No module named 'numpy'`` while installing ``scipy``,
install numpy by hand ``pip install [--user] numpy`` and rerun it again. Use
the option ``--addopts`` to pass additional options to ``py.test``.

You can run specific tests providing the file name(s) and, optionally the name
of a test. E.g.::

    py.test tests/test_logging_helper.py  # runs only the tests in the logging helper file
    py.test tests/test_logging_helper.py::test_log_setup  # runs only one test 

Relevant command line options::

    -v                    verbose output: print the names and parameters of the
                          tests
    -s                    capture standard output: can cause weird interactions
                          with the logging module

Some test are place holders for missing tests, non reviewed or buggy code. They
are marked as ``todo`` and they fail. It is possible to skip them invoking::

    py.test -m "not todo"

or::

    tox -- -m "not todo"

A code coverage report is also created thanks to the `pytest-cov
<https://pypi.python.org/pypi/pytest-cov>`_ plugin and can be visualized opening
into a browser ``cover/index.html``. If you want a recap of the coverage
directly in the terminal you can provide one of the following options when
running ``py.test``::

    --cov-report term
    --cov-report term-missing
    
Besides running the tests, the ``tox`` command also builds, by default, the
documentation and collates the coverage tests from the various python
interpreters and can copy then to some directory. To do the latter create, if
necessary, the configuration file ``~/.config/little_deploy.cfg`` and add to it
a section called ``pyhetdex`` with either one or both of the following options:

.. code-block:: ini

    [pyhetdex]
    # if given the deploys the documentation to the given dir
    doc = /path/to/dir
    # if given the deploys the coverage report to the given dir
    cover = /path/to/other/dir

    # it's also possible to insert the project name and the type of the document
    # to deploy using the {project} and {type_} placeholders. E.g
    # cover = /path/to/dir/{project}_{type_}
    # will be expanded to /path/to/dir/pyhetdex_cover

For more information about the configuration file check `little_deploy
<https://github.com/montefra/little_deploy>`_. 

For other command line arguments type::

    py.test -h

For a list of available fixtures type::

    py.test --fixtures tests/

``tox`` and ``pyenv``
---------------------

Many systems have a limited number of python versions installed. `pyenv
<https://github.com/pyenv/pyenv>`_ provides ways to have multiple python
versions that can be used by ``tox`` via the `tox-pyenv
<https://pypi.python.org/pypi/tox-pyenv>`_ plugin.

Here we outline the steps necessary to make ``tox`` use ``pyenv``:

* Install ``pyenv`` following `these instructions
  <https://github.com/pyenv/pyenv#installation>`_. We suggest to use ``brew``
  under Mac OS X or the automatic installer. When is done, follow the
  instructions to enables ``pyenv``.
* Install the python versions that you need. E.g. if you have python 2.7 and
  3.6 on you system, you can install only missing versions, e.g.::

      pyenv install 3.4.6
      pyenv install 3.5.3

  Of course you can also install 2.7 and 3.6 using pyenv.
* Install ``tox-pyenv`` in the same place where ``tox`` is installed, i.e.
  either on the system, a virtual environment or a ``pyenv`` instance::

      pip install tox-pyenv

  This way ``tox`` is can use ``pyenv which`` to locate a required python
  version

* The last step consists in letting ``pyenv`` know which python versions to
  use. If you have already set `pyenv global
  <https://github.com/pyenv/pyenv/blob/master/COMMANDS.md#pyenv-global>_` to
  all the version required for testing you should be done. Otherwise go to the
  ``pyhetdex`` directory and run `pyenv local
  <https://github.com/pyenv/pyenv/blob/master/COMMANDS.md#pyenv-local>_`::

    pyenv local system 3.4.6 3.5.3

  This command creates a file called ``.python-version`` that contains the
  following three lines::

    system
    3.4.6
    3.5.3

  It will make ``pyenv which`` look for python versions in the system
  directories as well as within the ``pyenv`` directory. 

  If you did installed also other versions of python (e.g. 3.6.0 and 2.7.13)
  under ``pyenv`` and want to use them instead of the system ones, you can
  use::

    pyenv local 3.6.0 3.4.6 3.5.3 2.7.13

* Run ``tox``: now you will be able to use all the python version that tox
  requires.

Documentation
=============

To build the documentation you need the additional dependences described in
:ref:`optdep`. They can be installed by hand or during ``pyhetdex`` installation
by executing one of the following commands on a local copy::

  pip install /path/to/pyhetdex[doc]
  pip install /path/to/pyhetdex[livedoc]

The first install ``sphinx``, the ``alabaster`` theme and the ``numpydoc``
extension; the second also installs ``sphinx-autobuild``.

To build the documentation in html format go to the ``doc`` directory and run::

  make html

The output is saved in ``doc/build/html``. For the full list of available
targets type ``make help``.

If you are updating the documentation and want avoid the
``edit-compile-browser refresh`` cycle, and you have installed
``sphinx-autobuild``, type::

  make livehtml

This command compiles the documentation and serves it on
http://127.0.0.1:{port}, where ``{port}`` is an available port, and open the
page on your default browser. The html documentation is automatically rebuilt
after every change of the source and the browser reloaded.

Please make sure that every module in ``pyhetdex`` is present in the
:ref:`code_documentation`.
