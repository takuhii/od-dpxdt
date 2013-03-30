#!/usr/bin/env python
# Copyright 2013 Brett Slatkin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Frontend for the API server."""

import logging

# Local libraries
import flask
from flask import Flask, abort, redirect, render_template, request, url_for
from flask.ext.wtf import Form

# Local modules
from . import app
from . import db
import forms
import models


@app.route('/')
def homepage():
    context = {
    }
    return render_template('home.html', **context)



@app.route('/new', methods=['GET', 'POST'])
def new_build():
    """Page for crediting or editing a build."""
    form = forms.BuildForm()
    if form.validate_on_submit():
        build = models.Build()
        form.populate_obj(build)
        db.session.add(build)
        db.session.commit()

        logging.info('Created build via UI: build_id=%r, name=%r',
                     build.id, build.name)
        return redirect(url_for('view_build', id=build.id))

    return render_template(
        'new_build.html',
        build_form=form)


@app.route('/build')
def view_build():
    build_id = request.args.get('id', type=int)
    if not build_id:
        return abort(400)

    build = models.Build.query.get(build_id)
    if not build:
        return abort(404)

    candidate_list = (
        models.Release.query
        .filter_by(build_id=build_id)
        .order_by(models.Release.number.desc())
        .all())

    # Collate by release name, order releases by latest creation
    release_dict = {}
    created_dict = {}
    for candidate in candidate_list:
        release_list = release_dict.setdefault(candidate.name, [])
        release_list.append(candidate)

        max_created = created_dict.get(candidate.name, candidate.created)
        created_dict[candidate.name] = max(candidate.created, max_created)

    # Sort each release by candidate number descending
    for release_list in release_dict.itervalues():
        release_list.sort(key=lambda x: x.number, reverse=True)

    # Sort all releases by created time descending
    release_age_list = [
        (value, key) for key, value in created_dict.iteritems()]
    release_age_list.sort(reverse=True)
    release_name_list = [key for _, key in release_age_list]

    return render_template(
        'view_build.html',
        build=build,
        release_name_list=release_name_list,
        release_dict=release_dict)


@app.route('/candidate')
def view_candidate():
    context = {
    }
    return render_template('view_candidate.html', **context)


@app.route('/run')
def view_run():
    context = {
    }
    return render_template('view_run.html', **context)
