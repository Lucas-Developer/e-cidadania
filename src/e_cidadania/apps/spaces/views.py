# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Cidadanía Coop.
# Written by: Oscar Carballal Prego <info@oscarcp.com>
#
# This file is part of e-cidadania.
#
# e-cidadania is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# e-cidadania is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with e-cidadania. If not, see <http://www.gnu.org/licenses/>.

import datetime

from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group

from django.contrib import messages

from django.template import RequestContext

from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.views.generic.create_update import create_object
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object

from e_cidadania.apps.spaces.models import Space, Entity, Document
from e_cidadania.apps.news.models import Post
from e_cidadania.apps.spaces.forms import SpaceForm


def go_to_space(request):

    """
    This view redirects to the space selected in the dropdown list in the
    index page. It only uses a POST petition.
    """
    
    if request.POST:
        return redirect('/spaces/' + request.POST['spaces'])

def view_space_index(request, space_name):

    """
    Show the index page for the requested space.
    """
    place = get_object_or_404(Space, name=space_name)

    extra_context = {
        'entities': Entity.objects.filter(space=place.id),
        'documents': Document.objects.filter(space=place.id),
        'publication': Post.objects.filter(post_space=place.id).order_by('-post_pubdate'),
            
        # BIG FUCKING SECURITY WARNING
        # DO NOT TOUCH THIS. PIRATES ARE WATCHING
        # When activating this line, accesing to a space gives
        # automatically the permissions of the author (this can be
        # from a simple moderator to the main admin of the system)
        
        #'user': User.objects.get(username=place.author)
    }

    return object_detail(request,
                         queryset = Space.objects.all(),
                         object_id = place.id,
                         template_name = 'spaces/index.html',
                         template_object_name = 'get_place',
                         extra_context = extra_context,
                        )

@permission_required('Space.edit_space')
def edit_space(request, space_name):

    """
    Only people registered to that space or site administrators will be able
    to edit spaces.
    """
    place = get_object_or_404(Space, name=space_name)

    return update_object(request,
                         model = Space,
                         object_id = place.id,
                         login_required = True,
                         template_name = 'spaces/edit.html',
                         template_object_name = 'get_place',
                         post_save_redirect = '/')

def delete_space(request, space_name):

    """
    Delete the selected space and return to the index page.
    """
    place = get_object_or_404(Space, name=space_name)
    return delete_object(request,
                         model = Space,
                         object_id = place.id,
                         login_required = True,
                         template_name = 'spaces/delete.html',
                         template_object_name = 'get_place',
                         post_delete_redirect = '/')

@permission_required('Space.add_space')
def create_space(request):

    """
    Create new spaces. In this view the author field is automatically filled
    so we can't use a generic view.
    """
    space = Space()
    form = SpaceForm(request.POST or None, request.FILES or None, instance=space)

    if request.POST:
        form_uncommited = form.save(commit=False)
        form_uncommited.author = request.user
        if form.is_valid():
            form_uncommited.save()
            space = form_uncommited.name
            return redirect('/spaces/' + space)
    
    return render_to_response('spaces/add.html',
                              {'form': form},
                              context_instance=RequestContext(request))
