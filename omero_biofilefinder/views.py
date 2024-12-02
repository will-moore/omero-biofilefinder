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

import csv
import io
from django.shortcuts import render
from django.http import HttpResponse
from collections import defaultdict
from django.urls import reverse

from omeroweb.decorators import login_required

from omeroweb.webclient.tree import marshal_annotations


# login_required: if not logged-in, will redirect to webclient
# login page. Then back to here, passing in the 'conn' connection
# and other arguments **kwargs.
@login_required()
def index(request, conn=None, **kwargs):
    # We can load data from OMERO via Blitz Gateway connection.
    # See https://docs.openmicroscopy.org/latest/omero/developers/Python.html
    experimenter = conn.getUser()

    # A dictionary of data to pass to the html template
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    # print can be useful for debugging, but remove in production
    # print('context', context)

    # Render the html template and return the http response
    return render(request, "omero_biofilefinder/index.html", context)


@login_required()
def omero_to_csv(request, id, conn=None, **kwargs):

    datasets = conn.getObjects("Dataset", opts={"project": id})
    image_ids = []
    for dataset in datasets:
        for image in dataset.listChildren():
            image_ids.append(image.id)

    print("image_ids", image_ids)

    anns, experimenters = marshal_annotations(conn, image_ids=image_ids, ann_type="map")

    # Get all the Keys...
    keys = set()
    for ann in anns:
        for key_val in ann["values"]:
            print("key_val", key_val[0])
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
    print("column_names", column_names)


    # write csv to return as http response
    webclient_url = reverse("webindex")

    with io.StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        for image_id, values in kvp.items():
            thumb = reverse("webgateway_render_thumbnail", kwargs={"iid": image_id})
            row = [f"{webclient_url}?show=image-{image_id}", thumb]
            for key in keys:
                row.append(",".join(values.get(key, [])))
            writer.writerow(row)

        response = HttpResponse(csvfile.getvalue(), content_type="text")
        # response = HttpResponse(csvfile.getvalue(), content_type="text/csv")
        # response["Content-Disposition"] = 'attachment; filename="biofilefinder.csv"'
        return response

