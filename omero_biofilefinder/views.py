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
    csv_url = request.build_absolute_uri(csv_url)

    # Including the sessionUuid allows request from BFF to join the session
    # TODO: lookup which server we are connected to if there are more than one
    source = {
        "uri": csv_url,
        "type": "csv",
        "name": "omero.csv",
    }
    s = urllib.parse.quote(json.dumps(source))
    bff_static = reverse("bff_static", kwargs={"url": ""})
    url = f"{bff_static}?source={s}"
    # url = f"https://bff.allencell.org/app?source={s}"

    # We want to pick some columns to show in the BFF app
    # Need to know a few Keys from Key-Value pairs....
    # Let's just check first 5 images...
    datasets = conn.getObjects("Dataset", opts={"project": int(project_id)})
    image_ids = []
    for dataset in datasets:
        for image in dataset.listChildren():
            image_ids.append(image.id)
            if len(image_ids) > 5:
                break
        if len(image_ids) > 5:
            break
    # Get KVP keys for 5 images...
    anns, experimenters = marshal_annotations(conn, image_ids=image_ids,
                                              ann_type="map")
    keys = defaultdict(lambda: 0)
    for ann in anns:
        for key, val in ann["values"]:
            keys[key] += 1
    # Sort keys by number of occurrences and take the top 3
    sorted_keys = sorted(keys.keys(), key=lambda x: keys[x], reverse=True)
    # Show max 5 columns (4 keys)
    col_names = ["File Name", "Dataset"] + sorted_keys[:3]
    col_width = 1 / len(col_names)
    # column query e.g. "File Name:0.25,Dataset:0.25,Key1:0.25,Key2:0.25"
    col_query = ",".join([f"{name}:{col_width}:.2f" for name in col_names])
    url += "&c=" + col_query

    return HttpResponseRedirect(url)


@login_required()
def omero_to_csv(request, id, conn=None, **kwargs):

    datasets = conn.getObjects("Dataset", opts={"project": id})
    image_ids = []
    ds_names_by_iid = {}
    for dataset in datasets:
        for image in dataset.listChildren():
            image_ids.append(image.id)
            ds_names_by_iid[image.id] = dataset.getName()

    # We use page=-1 to avoid pagination (default is 500)
    anns, experimenters = marshal_annotations(conn, image_ids=image_ids,
                                              ann_type="map", page=-1)

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

    column_names = ["File Path", "File Name", "Dataset", "Thumbnail"]
    column_names.extend(list(keys))
    column_names.append("Uploaded")

    # write csv to return as http response
    with io.StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        for image_id in image_ids:
            values = kvp.get(image_id, {})
            thumb_url = reverse("webgateway_render_thumbnail",
                                kwargs={"iid": image_id})
            thumb_url = request.build_absolute_uri(thumb_url)
            image = conn.getObject("Image", image_id)
            image_url = request.build_absolute_uri(reverse("webindex"))
            # we end url with .png so that BFF enables open-with "Browser"
            image_url += f"?show=image-{image_id}&_=.png"
            row = [image_url,
                   image.getName() if image else "Not Found",
                   ds_names_by_iid.get(image_id, "Not Found"),
                   thumb_url]
            for key in keys:
                row.append(",".join(values.get(key, [])))
            row.append(image.creationEventDate().strftime(
                "%Y-%m-%d %H:%M:%S.%Z"))
            writer.writerow(row)

        response = HttpResponse(csvfile.getvalue(), content_type="text/csv")
        return response


def app(request, url, **kwargs):

    from django.contrib.staticfiles.storage import staticfiles_storage

    if len(url) == 0:
        url = "index.html"

    static_path = staticfiles_storage.path("omero_biofilefinder/dist/" + url)

    mode = "r"
    if url.endswith(".png"):
        mode = "rb"

    with open(static_path, mode=mode) as f:
        content = f.read()

        # We need to replace the basename in the js file
        if url.endswith(".js") and url.startswith("app."):
            # e.g. "/omero_biofilefinder/bff"
            basename = reverse("omero_biofilefinder_index") + "bff"
            content = content.replace('{basename:""}',
                                      f'{{basename:"{basename}"}}')

        response = HttpResponse(content)
        if (url.endswith(".js")):
            response["Content-Type"] = "application/javascript"
        elif (url.endswith(".css")):
            response["Content-Type"] = "text/css"
        elif (url.endswith(".png")):
            response["Content-Type"] = "image/png"
        elif (url.endswith(".html")):
            response["Content-Type"] = "text/html"
    return response
