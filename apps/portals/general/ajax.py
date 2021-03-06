# For simple dajax(ice) functionalities
from dajaxice.decorators import dajaxice_register

# For rendering templates
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from configs import settings
from apps.users.models import Dept, Subdept, ERPProfile
from apps.walls.models import Wall, Post, Comment
from apps.docs.utils import Drive, Github

from apps.walls.utils import get_tag_object
from annoying.functions import get_object_or_None
# Decorators
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from misc.utils import *
from apps.users.models import *
from apps.walls.models import *
from post_office import mail

import os
from django.core.management import call_command

from apps.portals.general.utils import share_drive, attach_drive_to_entity

def admins_only(in_func):
    def out_func(request, *args, **kwargs):
        if not request.user.is_staff:
            return json.dumps({'message':'Not Authorized'})
        in_func(request, *args, **kwargs )
    return out_func

    
@dajaxice_register
def hello(request):
    """
        Used for testing Dajaxice
    """
    #html_content = render_to_string("dash/task_tables/coord_you.html", query_dictionary, RequestContext(request))
    return json.dumps({'message': 'hello'})

########## FOR ADMIN PORTAL #######################
@dajaxice_register
def get_users_of_subdept(request, subdept_id):
    user = request.user
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    append_string = ""
    for i in ERPProfile.objects.filter(coord_relations__in=Subdept.objects.filter(id=subdept_id)):
        append_string+=render_to_string('portals/general/user.html', {'user':i.user,'link_type':'subdept','link_id':subdept_id}, context_instance=global_context(request, token_info=False))
    return json.dumps({'append_string':append_string});

@dajaxice_register
def get_users_of_page(request, page_id):
    user = request.user
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    append_string = ""
    for i in ERPProfile.objects.filter(page_relations__in=Page.objects.filter(id=page_id)):
        append_string+=render_to_string('portals/general/user.html', {'user':i.user,'link_type':'page','link_id':page_id}, context_instance=global_context(request, token_info=False))
    return json.dumps({'append_string':append_string});

@dajaxice_register
def add_users_to_page(request,page_id,user_ids):
    user = request.user
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    page = Page.objects.get(id = page_id)
    append_string = ''
    for user_id in user_ids:
        user = User.objects.get(id = user_id.split('_')[1])
        e = user.erp_profile
        if not (page in e.page_relations.all()):
            append_string += render_to_string('portals/general/user.html', {'user':e.user,'link_type':'page','link_id':page_id}, context_instance=global_context(request, token_info=False))
        e.page_relations.add(page)
        share_drive( drive, user, page.directory_id )

    return json.dumps({'message':'done','append_string':append_string})

@dajaxice_register
def add_users_to_subdept(request,subdept_id,user_ids):
    drive = Drive()
    user = request.user
    erp_profile = user.erp_profile
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    subdept = Subdept.objects.get(id = subdept_id)
    dept = subdept.dept

    append_string = ''
    if (not user.is_superuser) and erp_profile.core_relations.filter(id=dept.id).count() == 0 and \
        erp_profile.supercoord_relations.filter(id=dept.id).count() == 0:
        return json.dumps({'message': 'This subdept is not under your department !'})

    for user_id in user_ids:
        user = User.objects.get(id = user_id.split('_')[1])
        e = user.erp_profile
        if not (subdept in e.coord_relations.all()):
            append_string += render_to_string('portals/general/user.html', {'user':e.user,'link_type':'subdept','link_id':subdept_id}, context_instance=global_context(request, token_info=False))
        e.coord_relations.add(subdept)
        share_drive( drive, user, subdept.directory_id )

    return json.dumps({'message':'done','append_string':append_string})

@dajaxice_register
def delete_user_from_subdept(request,subdept_id,user_id):
    user = request.user
    erp_profile = user.erp_profile
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    subdept = Subdept.objects.get(id = subdept_id)
    dept = subdept.dept
    if (not user.is_superuser) and erp_profile.core_relations.filter(id=dept.id).count() == 0 and \
        erp_profile.supercoord_relations.filter(id=dept.id).count() == 0:
        return json.dumps({'message': 'This subdept is not under your department !'})

    User.objects.get(id = user_id).erp_profile.coord_relations.remove(subdept)
    return json.dumps({'message':'done'})
    
@dajaxice_register
def delete_user_from_page(request,page_id,user_id):
    user = request.user
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    User.objects.get(id = user_id).erp_profile.page_relations.remove(Page.objects.get(id = page_id))
    return json.dumps({'message':'done'})
    
@dajaxice_register
def create_subdept(request, dept_id, name):
    user = request.user
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    if (not user.is_superuser) and user.erp_profile.core_relations.filter(id=dept_id).count() == 0 and user.erp_profile.supercoord_relations.filter(id=dept_id).count() == 0:
        return json.dumps({'message': 'This subdept is not under your department !'})
     
    s = Subdept.objects.create(dept=Dept.objects.get(id=dept_id), name=name)

    drive = Drive()
    attach_drive_to_entity( drive, s )

    return json.dumps({'message' : 'done', 'id' : s.id, 'name' : name})

@dajaxice_register
def create_page(request, name):
    # ?
    user = request.user
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    p = Page.objects.create(name=name);

    drive = Drive()
    attach_drive_to_entity( drive, p )

    return json.dumps({'message': 'done', 'id' : p.id, 'name' : name})

@dajaxice_register
def remove_subdept(request, subdept_id):
    # ?
    user = request.user
    erp_profile = user.erp_profile
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    subdept = Subdept.objects.get(id = subdept_id)
    dept = subdept.dept
    if (not user.is_superuser) and erp_profile.core_relations.filter(id=dept.id).count() == 0 and \
        erp_profile.supercoord_relations.filter(id=dept.id).count() == 0:
        return json.dumps({'message': 'This subdept is not under your department !'})
    
    subdept.is_active = False;
    subdept.save()
    return json.dumps({'message': 'done'})

@dajaxice_register
def remove_page(request, page_id):
    # ?
    user = request.user
    erp_profile = user.erp_profile
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})

    page = Page.objects.get(id = page_id).delete();
    page.is_active = False;
    page.save()
    
    return json.dumps({'message':'done'})

@dajaxice_register
def create_user(request, email, first_name, last_name, supercoord):
    user = request.user
    erp_profile = user.erp_profile
    if not user.is_staff:
        return json.dumps({'message':'Not Authorized'})
    #import pdb;pdb.set_trace();
    if not email or not first_name or not last_name:
        return json.dumps({'message' : '<b>Error :</b> All fields are required'});
    elif User.objects.filter(email=email).count() + User.objects.filter(username=email[:30]).count():
        return json.dumps({'message':'<b>Error :</b> Account with ' + email + ' already exists'});
    try:
        validate_email( email )
    except ValidationError:
        return json.dumps({'message':'<b>Error :</b> Please enter a valid email address'});

    passwd = User.objects.make_random_password()
    u = User.objects.create_user(username=email[:30], email=email, first_name=first_name, last_name=last_name, password=passwd);
    e = ERPProfile.objects.create(user=u)
    
    depts = Dept.objects.filter(id__in=supercoord)
    for dept in depts:
        if dept in erp_profile.core_relations.all():
            e.supercoord_relations.add(dept)
            
    #import pdb;pdb.set_trace();
    #--------------------------------------

    if settings.SEND_EMAIL:
        mail.send( [u.email], 
            settings.DEFAULT_FROM_EMAIL, 
            template='welcome.email',
            context={ 
                'user' : u,
                'password' : passwd,
                'SITE_URL' : settings.SITE_URL,
                'FEST_NAME' : settings.FEST_NAME,
            },
            headers = {},
        )
    # refresh json lists.

    call_command('jsonify_data')
    call_command('collectstatic', interactive=False)
    if settings.PERMISSION_COMMAND:
        os.system('/home/saarango/git/fest-api/runscript')
    return json.dumps( { 
        'message' : 'Successfully created <b>' + email + '</b>. <br />An email will be sent with the password to the given email address in 15mins.<br/>Please ask them to check spam !<br /> IF they do not get an email, ask them to use the forgot password to create a password',
        'success' : 'yes',
        'id' : u.id,
        'first_name' : u.first_name,
        'last_name' : u.last_name,
        'email' : u.email,
        'passkey': passwd
    } )
