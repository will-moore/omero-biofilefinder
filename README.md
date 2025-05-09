
[![Actions Status](https://github.com/will-moore/omero-biofilefinder/workflows/OMERO/badge.svg)](https://github.com/will-moore/omero-biofilefinder/actions)


OMERO BioFile Finder
==================================

This plugin supports opening of OMERO data (e.g. a Project) in the BioFile Finder app https://bff.allencell.org/.

Key-Value pairs on Images in OMERO are converted into tabular data for BFF.

NB: This app is currently at the proof-of-concept stage. Feedback welcome!

**WARNING** We include your OMERO session ID within URLs that BFF uses to access data from OMERO, such
as the Thumbnail URL. You should not share the session ID with anyone while the session is still active.



Data in webclient - images and Key-Value pairs are from idr0021.
<img width="1256" alt="Image" src="https://github.com/user-attachments/assets/8124429d-ef3e-497b-baa2-9d537ac98357" />

Open Project with BioFile Finder...
<img width="420" alt="Image" src="https://github.com/user-attachments/assets/4e933502-b322-42b4-a19c-8de603e5427c" />

This will open BioFile Finder in another tab. Here the images are grouped by `Gene Symbol`.
<img width="1510" alt="Image" src="https://github.com/user-attachments/assets/3993278e-b978-4e89-b886-6df587a1297b" />


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

Export script
-------------

We use an OMERO.server script to build a `parquet` file that is read by BioFile Finder.

TODO: add script upload instructions and/or add functionality in the app to upload it "automatically".

The script can be run directly (without using the OMERO scripting service). This will use `cli_login` to login
to your chosen OMERO server. The exported data will get written to your current directory (where you're running the script)
and the parquet file will only get attached to the target (e.g. Project or Dataset) if you can annotate it.

    $ cd omero_biofilefinder/scripts
    $ python omero/annotation_scripts/Export_to_Biofile_Finder.py Project:501 --base-url https://your-server.org/


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

