"""Configuration set up

The custom :class:`ConfigParser` provides two new functionalities to parse
lists:

* :meth:`ConfigParser.get_list`
* :meth:`ConfigParser.get_list_of_list`

As base class uses the standard :class:`configparser.ConfigParser` in python 3
and the `backported version <https://pypi.python.org/pypi/configparser>`_ for
python 2.7. See `the configparser documentation
<https://docs.python.org/3/library/configparser.html>`_ for more info.

Examples
--------
>>> import pyhetdex.tools.configuration as pconf
>>> # This can be imported only after `pyhetdex.tools.configuration` has been
>>> # imported
>>> from configparser import BasicInterpolation
>>> from configparser import ExtendedInterpolation
>>> # standard config parser interpolation
>>> stdparser = pconf.ConfigParser()
>>> # equivalent
>>> stdparser = pconf.ConfigParser(interpolation=BasicInterpolation())
>>> # extended config parser interpolation
>>> extparser = pconf.ConfigParser(interpolation=ExtendedInterpolation())
>>> # test mapping interface
>>> parser = pconf.ConfigParser()
>>> sections = {'section1': {'key1': 'value1',
...                          'key2': 'value2',
...                          'key3': 'value3'},
...             'section2': {'keyA': 'valueA',
...                          'keyB': 'valueB',
...                          'keyC': 'valueC'},
...             }
>>> parser.read_dict(sections)
>>> parser['section1']
<Section: section1>
>>> print(parser['section2']['keyA'])
valueA

::

    # Configuration file: default interpolation
    [general]
    dir1 = /path/to
    [section]
    dir1 = /path/to
    file1 = %(dir1)/file1

    # Configuration file: extended interpolation
    [general]
    dir1 = /path/to
    [section]
    file1 = %{general:dir1}/file1
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

import configparser as confp
import six


def override_conf(conf, args, prefix='setting', sep='__', nones=[None, []]):
    """Overrides entries in ``conf`` with values in ``args``.

    The function collects all the attributes of ``args`` of the form:
    ``prefix<sep>section<sep>option``. For each one, if its value is not in
    ``nones``, replace the ``option`` in the ``section`` of the configuration
    object with the corresponding value in ``args``; the value is cast to a
    string. The ``section`` and ``option`` must exist in ``conf``.

    Examples
    --------
    >>> from argparse import Namespace
    >>> c = ConfigParser()
    >>> c.read_dict({'sec1': {'opt1': 'val1'}})
    >>> print(c['sec1']['opt1'])
    val1
    >>> c = override_conf(c, Namespace(setting__sec1__opt1=None))
    >>> print(c['sec1']['opt1'])
    val1
    >>> c = override_conf(c, Namespace(setting__sec1__opt1='val2'))
    >>> print(c['sec1']['opt1'])
    val2

    Parameters
    ----------
    conf : :class:`configparser.ConfigParser` or child instance
        configuration object. It must support the `mapping protocol
        <https://docs.python.org/3/library/configparser.html#mapping-protocol-access>`_
    args : object
        object containing the attributes used for overriding the configuration
    prefix : string, optional
        prefix used to find the attributes in ``args`` that are considered for
        the override
    sep : string, optional
        the string that separate ``prefix``, the section name and the option
        name
    nones : list, optional
        if the value of the option is in this list, do not insert it in
        ``conf``

    Returns
    -------
    conf : :class:`~pyhetdex.tools.configuration.ConfigParser`
        updated configuration object
    """
    _prefix = prefix + sep
    for attr in dir(args):
        # skip if the prefix is not present
        if not attr.startswith(_prefix):
            continue
        # try to split the attribute name, if it fails skip the attribute
        try:
            _, section, option = attr.split(sep)
        except ValueError:
            continue

        value = getattr(args, attr)
        # If the value is in nones, skip
        if value in nones:
            continue
        if isinstance(value, list):
            # if it's a list join it as a list of strings
            value = ', '.join([str(v) for v in value])
        else:
            value = str(value)

        try:
            conf.get(section, option)
            conf.set(section, option, value)
        except (confp.NoSectionError, confp.NoOptionError):
            continue

    return conf


# =============================================================================
# Custom configuration parser. Provides extra get methods to parse and store
# complex options
# =============================================================================
class ConfigParser(confp.ConfigParser):
    """Customise configuration parser

    Parameters
    ----------
    args : list
        arguments passed to the parent class
    kwargs : dict
        keyword arguments passed to the parent class
    interpolation : :class:`Interpolation` instance
        only for python 2: select which interpolation to use
    """
    def __init__(self, *args, **kwargs):
        super(ConfigParser, self).__init__(*args, **kwargs)

        try:  # Python 2
            self.BOOLEAN_STATES = self._boolean_states
        except AttributeError:  # better pythons
            self.BOOLEAN_STATES = self.BOOLEAN_STATES

    def _to_boolean(self, value):
        '''Convert a string to a boolean compatible to ConfigParser standards

        Parameters
        ----------
        value : string
            input value

        Returns
        -------
        bool
            converted value

        Raises
        ------
        ValueError
            if the conversion fails
        '''
        try:
            return self.BOOLEAN_STATES[value.lower()]
        except KeyError:
            raise ValueError('Not a boolean: %s' % value)

    def get_list_of_list(self, section, option, use_default=False,
                         cast_to=str):
        """
        A convenience method which coerces option in the specified section
        to a list of lists. If the options is empty returns ``[[None, None]]``.

        Examples
        --------
        .. testsetup:: *

            from pyhetdex.tools.configuration import ConfigParser

        >>> # cat settings.cfg:
        >>> # [section]
        >>> # wranges_bkg = 3500-4500,4500-5500
        >>> conf = ConfigParser()
        >>> conf.read_dict({"section": {"wranges_bkg": "3500-4500,4500-5500"}})
        >>> conf.get_list_of_list("section", "wranges_bkg")
        [['3500', '4500'], ['4500', '5500']]
        >>> conf.get_list_of_list("section", "wranges_bkg", cast_to=float)
        [[3500.0, 4500.0], [4500.0, 5500.0]]
        >>> conf.get_list_of_list("section", "not_exist")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NoOptionError: No option 'not_exist' in section: 'section'
        >>> conf.get_list_of_list("section", "not_exist", use_default=True)
        [[None, None]]

        Parameters
        ----------
        section : string
            name of the section
        option : string
            name of the option
        use_default : bool
            whether default to ``[[None, None]]``
        cast_to : type, optional
            convert each element to the given type; default convert to string.
            The ``bool`` case is treated especially to comply with the
            ConfigParser standards.

        Returns
        -------
        value : list of lists
            parsed option

        Raises
        ------
        NoOptionError
            if the option doesn't exist and no default required
        """
        try:
            value = self.get(section, option)
        except confp.NoOptionError:
            if use_default:
                return [[None, None]]
            else:
                raise

        if not value.strip():
            value = [[None, None]]
        else:
            if cast_to == bool:
                cast_to = self._to_boolean
            value = [[cast_to(i.strip()) for i in v.split('-')]
                     for v in value.split(',')]
        return value

    def get_list(self, section, option, use_default=False, cast_to=str):
        """A convenience method which converts the option in the specified section
        from a comma separated list to a python list.

        If the options is empty returns the empty list ``[]``.

        Examples
        --------

        .. testsetup:: *

            from pyhetdex.tools.configuration import ConfigParser

        >>> # cat settings.cfg:
        >>> # [section]
        >>> # wranges_iq = 3500, 4500, 5500
        >>> conf = ConfigParser()
        >>> conf.read_dict({"section": {"wranges_iq": "3500, 4500, 5500"}})
        >>> conf.get_list("section", "wranges_iq")
        ['3500', '4500', '5500']
        >>> conf.get_list("section", "wranges_iq", cast_to=int)
        [3500, 4500, 5500]
        >>> conf.get_list("section", "not_exist")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NoOptionError: No option 'not_exist' in section: 'section'
        >>> conf.get_list("section", "not_exist", use_default=True)
        []

        Parameters
        ----------
        section : string
            name of the section
        option : string
            name of the option
        use_default : bool, optional
            whether default to ``[]``
        cast_to : type, optional
            convert each element to the given type; default convert to string.
            The ``bool`` case is treated especially to comply with the
            ConfigParser standards.

        Returns
        -------
        value : list of lists
            parsed option

        Raises
        ------
        NoOptionError
            if the option doesn't exist and no default required
        """
        try:
            value = self.get(section, option)
        except confp.NoOptionError:
            if use_default:
                return []
            else:
                raise

        if not value.strip():
            value = []
        else:
            if cast_to == bool:
                cast_to = self._to_boolean
            value = [cast_to(v.strip()) for v in value.split(',')]

        return value


# =============================================================================
# Interpolation classes are just a thin wrapper around the ones from the
# configparser package (backported one in python 2.7) with a warning to use
# the original ones instead of the ones added here in six.moves
# =============================================================================
class BasicInterpolation(confp.BasicInterpolation):
    def __init__(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            msg = ('Do not import the {name} class from ``six.moves``.'
                   ' Use ``import configparser`` or'
                   ' ``from configparser import {name}`` instead')
            warnings.warn(msg.format(name=self.__class__.__name__),
                          DeprecationWarning)
        super(BasicInterpolation, self).__init__(*args, **kwargs)


class ExtendedInterpolation(confp.ExtendedInterpolation):
    def __init__(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            msg = ('Do not import the {name} class from ``six.moves``.'
                   ' Use ``import configparser`` or'
                   ' ``from configparser import {name}`` instead')
            warnings.warn(msg.format(name=self.__class__.__name__),
                          DeprecationWarning)
        super(ExtendedInterpolation, self).__init__(*args, **kwargs)


# Register interpolators in six.moves
# === attributes

# add them to six.moves
six.add_move(six.MovedAttribute("BasicInterpolation",
                                "pyhetdex.tools.configuration",
                                "pyhetdex.tools.configuration"))
six.add_move(six.MovedAttribute("ExtendedInterpolation",
                                "pyhetdex.tools.configuration",
                                "pyhetdex.tools.configuration"))
