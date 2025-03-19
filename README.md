
[![Actions Status](https://github.com/will-moore/omero-biofilefinder/workflows/OMERO/badge.svg)](https://github.com/will-moore/omero-biofilefinder/actions)


OMERO BioFile Finder
==================================

This plugin supports opening of OMERO data (e.g. a Project) in the BioFile Finder app https://bff.allencell.org/.

Key-Value pairs on Images in OMERO are converted into tabular data for BFF.


Installation
============

This section assumes that an OMERO.web is already installed.

Installing from Pypi
--------------------

Install the app using [pip](<https://pip.pypa.io/en/stable/>) .

Ensure that you are running ``pip`` from the Python environment
where ``omero-web`` is installed. Depending on your install, you may need to
call ``pip`` with, for example: ``/path/to_web_venv/venv/bin/pip install ...``

::

    $ pip install -U omero-biofilefinder


Development mode
----------------

Install `omero-biofilefinder` in development mode as follows:

    # within your python venv:
    $ cd omero-biofilefinder
    $ pip install -e .

After installation either from [Pypi](https://pypi.org/) or in development mode, you need to configure the application.
To add the application to the `omero.web.apps` settings, run the following command:

Note the usage of single quotes around double quotes:

    $ omero config append omero.web.apps '"omero_biofilefinder"'

Configure `Open with`. Currently we only support opening a `Project` in OMERO BioFile Finder.

    $ omero config append omero.web.open_with '["omero_bff", "omero_biofilefinder_openwith", {"supported_objects":["project"], "target": "_blank", "label": "BioFile Finder"}]'


Now restart your `omero-web` server.


Further Info
============

1. This app was derived from [cookiecutter-omero-webapp](https://github.com/ome/cookiecutter-omero-webapp).
2. For further info on deployment, see [Deployment](https://docs.openmicroscopy.org/latest/omero/developers/Web/Deployment.html)


License
=======

This project, similar to many Open Microscopy Environment (OME) projects, is
licensed under the terms of the AGPL v3.


Copyright
=========

2024 University of Dundee

