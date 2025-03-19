#!/usr/bin/env python
#
# Copyright (c) 2024 University of Dundee.
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
#

import requests
import csv
import io
import urllib
import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from collections import defaultdict
from django.urls import reverse

from omeroweb.decorators import login_required

from omeroweb.webclient.tree import marshal_annotations


@login_required()
def index(request, conn=None, **kwargs):
    # Placeholder index page
    return render(request, "omero_biofilefinder/index.html", {})


def wrap_url(request, url, conn):
    """
    We need to enable the url to work when accessed from the BFF app.

    The URL must be aboslute and include the sessionUuid and server
    """
    url = request.build_absolute_uri(url)
    return f"{url}?bsession={conn._sessionUuid}&server=1"


@login_required()
def open_with_redirect_to_app(request, conn=None, **kwargs):
    """
    Open-with > BFF goes here...

    We generate a URL for loading csv for the project and then
    redirect to the BFF app with the source parameter set to the
    csv URL.
    """

    project_id = request.GET.get("project")
    csv_url = reverse("omero_biofilefinder_csv", kwargs={"id": project_id})
    csv_url = wrap_url(request, csv_url, conn)
    
    # Including the sessionUuid allows external request from BFF app to join the session
    # TODO: lookup which server we are connected to if there are more than one
    source = {
        "uri": csv_url,
        "type": "csv",
        "name": "omero.csv",
    }
    s = urllib.parse.quote(json.dumps(source))
    url = f"https://bff.allencell.org/app?source={s}"

    return HttpResponseRedirect(url)    


@login_required()
def omero_to_csv(request, id, conn=None, **kwargs):

    datasets = conn.getObjects("Dataset", opts={"project": id})
    image_ids = []
    for dataset in datasets:
        for image in dataset.listChildren():
            image_ids.append(image.id)

    # We use page=-1 to avoid pagination (default is 500)
    anns, experimenters = marshal_annotations(conn, image_ids=image_ids, ann_type="map", page=-1)

    # Get all the Keys...
    keys = set()
    for ann in anns:
        for key_val in ann["values"]:
            keys.add(key_val[0])

    # Add values to dict {image_id: {key: [list, of, values]}}
    kvp = {}
    for ann in anns:
        image_id = ann["link"]["parent"]["id"]
        if image_id not in kvp:
            kvp[image_id] = defaultdict(list)
        for key_val in ann["values"]:
            key = key_val[0]
            value = key_val[1]
            kvp[image_id][key].append(value)

    column_names = ["File Path", "Thumbnail"] + list(keys)

    # write csv to return as http response
    webclient_url = request.build_absolute_uri(reverse("webindex"))

    with io.StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        for image_id, values in kvp.items():
            thumb_url = reverse("webgateway_render_thumbnail", kwargs={"iid": image_id})
            thumb_url = wrap_url(request, thumb_url, conn)
            image = conn.getObject("Image", image_id)
            # "File Path" is just the name of the image since BFF can't make use
            # of a full URL to the image in webclient
            row = [image.getName() if image else "Not Found",
                   thumb_url]
            for key in keys:
                row.append(",".join(values.get(key, [])))
            writer.writerow(row)

        response = HttpResponse(csvfile.getvalue(), content_type="text/csv")
        return response
