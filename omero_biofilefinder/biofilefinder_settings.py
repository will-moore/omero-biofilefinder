#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2025 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Settings for the OMERO.biofilefinder app."""

import sys
from omeroweb.settings import process_custom_settings, report_settings

# load settings
BIOFILEFINDER_SETTINGS_MAPPING = {

    "omero.web.bff.force_https":
        ["FORCE_HTTPS",
         False,
         bool,
         ("Enforce https for absolute URLs. Only needed if Django does not "
          "know it is running under https.")],
}

process_custom_settings(sys.modules[__name__], 'BIOFILEFINDER_SETTINGS_MAPPING')
report_settings(sys.modules[__name__])