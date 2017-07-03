# -*-encoding:utf-8-*-
import unicodecsv
from django.http import HttpResponse
from models import TravelData
import os
import shutil
import xadmin
import xadmin.views as xviews
from django.contrib import messages

from django.core.exceptions import PermissionDenied
from django.db import transaction, router
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib.admin.utils import get_deleted_objects, model_ngettext
from xadmin.plugins.actions import BaseActionView


from xadmin.util import unquote
from xadmin.views.base import filter_hook, csrf_protect_m, ModelAdminView
from django.template.response import TemplateResponse

from django.db import models
from .models import FileExtendInfo

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields


        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = unicodecsv.writer(response, encoding='utf-8')

        field_names = TravelData._meta.get_fields()
        if header:
            row = [field.verbose_name for field in field_names if field.concrete]
            writer.writerow(row)
        for obj in queryset:
            data = TravelData.objects.filter(RouteName_id=obj.id)
            for sub_obj in data:
                row = [getattr(sub_obj, field.name)() if callable(getattr(sub_obj, field.name)) else getattr(sub_obj, field.name) for field in
                   field_names if field.concrete]
                writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv



class DeleteAdminView(xviews.DeleteAdminView):
    delete_confirmation_template = None

    def init_request(self, object_id, *args, **kwargs):
        "The 'delete' admin view for this model."
        self.obj = self.get_object(unquote(object_id))

        if not self.has_delete_permission(self.obj):
            raise PermissionDenied

        if self.obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(self.opts.verbose_name), 'key': escape(object_id)})

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (self.deleted_objects, model_count, self.perms_needed, self.protected) = get_deleted_objects(
            [self.obj], self.opts, self.request.user, self.admin_site, using)

    @csrf_protect_m
    @filter_hook
    def get(self, request, object_id):
        context = self.get_context()
        return TemplateResponse(request, self.delete_confirmation_template or
                                self.get_template_list("views/model_delete_confirm.html"), context, current_app=self.admin_site.name)

    @csrf_protect_m
    @transaction.atomic
    @filter_hook
    def post(self, request, object_id):
        if self.perms_needed:
            raise PermissionDenied

        self.delete_model()

        response = self.post_response()
        if isinstance(response, basestring):
            return HttpResponseRedirect(response)
        else:
            return response

    @filter_hook
    def delete_model(self):
        """
        Given a model instance delete it from the database.
        """
        self.obj.delete()

    @filter_hook
    def get_context(self):
        if self.perms_needed or self.protected:
            title = _("Cannot delete %(name)s") % {"name":
                                                   force_unicode(self.opts.verbose_name)}
        else:
            title = _("Are you sure?")

        new_context = {
            "title": title,
            "object": self.obj,
            "deleted_objects": self.deleted_objects,
            "perms_lacking": self.perms_needed,
            "protected": self.protected,
        }

        context = super(DeleteAdminView, self).get_context()
        context.update(new_context)
        return context

    @filter_hook
    def get_breadcrumb(self):
        bcs = super(DeleteAdminView, self).get_breadcrumb()
        bcs.append({
            'title': force_unicode(self.obj),
            'url': self.get_object_url(self.obj)
        })
        item = {'title': _('Delete')}
        if self.has_delete_permission():
            item['url'] = self.model_admin_url('delete', self.obj.pk)
        bcs.append(item)

        return bcs

    @filter_hook
    def post_response(self):
        self.message_user(_('The %(name)s "%(obj)s" was deleted successfully.') %
                          {'name': force_unicode(self.opts.verbose_name), 'obj': force_unicode(self.obj)}, 'success')

        if not self.has_view_permission():
            return self.get_admin_url('index')
        return self.model_admin_url('changelist')

ACTION_CHECKBOX_NAME = '_selected_action'
class DeleteSelectedAction(BaseActionView):

    action_name = "delete_selected"
    description = _(u'Delete selected %(verbose_name_plural)s')

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = True

    model_perm = 'delete'
    icon = 'fa fa-times'

    @filter_hook
    def delete_models(self, queryset):
        n = queryset.count()
        if n:
            if self.delete_models_batch:
                if(self.model_name=='view'):
                    for data in queryset:
                        for field in data._meta.fields:
                            if(field.name=='subjecttype'):
                                s = getattr(data, 'subjecttype')
                                if (s != '-1'):
                                    id = getattr(data, 'id')
                                    FileExtendInfo.objects.filter(fileId=str(id)).delete()
                            s = getattr(data,field.name)
                            if(os.path.isfile('./media/'+str(s))==True):
                                if(str(s).find("/quanjing/")==-1):
                                    os.remove('./media/' + str(s))
                                else:
                                    s = str(s).split("/")
                                    str1 = s[0:3]
                                    str1 = '/'.join(str1)
                                    if(os.path.isdir('./media/'+str1)):
                                        shutil.rmtree('./media/'+str1)
                                    if(os.path.exists('./media/'+str1+'.zip')):
                                        os.remove('./media/'+str1+'.zip')
                queryset.delete()
            else:
                for obj in queryset:
                    if (self.model_name == 'view'):
                        for field in obj._meta.fields:
                            if (field.name == 'subjecttype'):
                                s = getattr(obj, 'subjecttype')
                                if (s != '-1'):
                                    id = getattr(obj, 'id')
                                    FileExtendInfo.objects.filter(fileId=str(id)).delete()
                            s = getattr(obj, field.name)
                            if (os.path.isfile('./media/' + str(s)) == True):
                                if (str(s).find("/quanjing/") == -1):
                                    os.remove('./media/' + str(s))
                                else:
                                    s = str(s).split("/")
                                    str1 = s[0:3]
                                    str1 = '/'.join(str1)
                                    if (os.path.isdir('./media/' + str1)):
                                        shutil.rmtree('./media/' + str1)
                                    if (os.path.exists('./media/' + str1 + '.zip')):
                                        os.remove('./media/' + str1 + '.zip')
                    obj.delete()
            self.message_user(_("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(self.opts, n)
            }, 'success')

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)
        if (self.model_name=='filetype' or self.model_name=='discipline' or self.model_name=='language' or self.model_name=='spacescope' or self.model_name=='format'):
            for obj in queryset:
                data = obj.filebaseinfo_set.all()
                if data:
                    messages.info(self.request, (_(u"存在关联数据无法删除 %(name)s") % {"name": obj}))
                    return redirect('.')

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if perms_needed:
                raise PermissionDenied
            self.delete_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_unicode(self.opts.verbose_name)
        else:
            objects_name = force_unicode(self.opts.verbose_name_plural)





        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": objects_name}
        else:
            title = _("Are you sure?")

        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, self.delete_selected_confirmation_template or
                                self.get_template_list('views/model_delete_selected_confirm.html'), context, current_app=self.admin_site.name)


