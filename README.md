
[![Actions Status](https://github.com/will-moore/omero-biofilefinder/workflows/OMERO/badge.svg)](https://github.com/will-moore/omero-biofilefinder/actions)


OMERO BioFile Finder
==================================

This plugin supports opening of OMERO data (e.g. a Project) in the BioFile Finder app https://bff.allencell.org/.

Key-Value pairs on Images in OMERO are converted into tabular data for BFF.

NB: This app is currently at the proof-of-concept stage. Feedback welcome!

**WARNING** We include your OMERO session ID within URLs that BFF uses to access data from OMERO, such
as the Thumbnail URL. You should not share the session ID with anyone while the session is still active.


Installation
============

This section assumes that an OMERO.web is already installed.

Development mode
----------------

Install `omero-biofilefinder` in development mode as follows:

    # within your python venv:
    $ cd omero-biofilefinder
    $ pip install -e .

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

