# coding=UTF-8
from itertools import chain

from django.db.models.options import PROXY_PARENTS
from django.utils.encoding import force_unicode
from xadmin.views.list import COL_LIST_VAR, ORDER_VAR
from xadmin.plugins.relate import RELATE_PREFIX
from django.core.urlresolvers import reverse
from xadmin.models import Bookmark
from django.contrib.contenttypes.models import ContentType

from django.db.models import Q

import operator
from xadmin import widgets
from xadmin.plugins.utils import get_context_dict

from xadmin.util import get_fields_from_path, lookup_needs_distinct
from django.core.exceptions import SuspiciousOperation, ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models.sql.query import LOOKUP_SEP, QUERY_TERMS
from django.template import loader
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from xadmin.filters import manager as filter_manager, FILTER_PREFIX, SEARCH_VAR, DateFieldListFilter, RelatedFieldSearchFilter
from xadmin.views import BaseAdminPlugin
from xadmin.util import is_related_field
from xadmin.filters import BaseFilter

class CreateSub(BaseAdminPlugin):
    createsub = False

    def init_request(self,*args,**kwargs):
        return bool(self.createsub)

    def save_models(self,__):
        if '_rel_subParent__id__exact' in self.request.POST:
            subParent = self.request.POST['_rel_subParent__id__exact']
            self.admin_view.new_obj.subParent_id = subParent
            self.admin_view.new_obj.save()
        else:
            self.admin_view.new_obj.save()


class RelateMenuPlugin(BaseAdminPlugin):
    use_related = True
    relatemenu = False
    related_list = []

    def init_request(self,*args,**kwargs):
        return bool(self.relatemenu)

    def _get_all_related_objects(self, local_only=False, include_hidden=False,
                                 include_proxy_eq=False):
        """
        Returns a list of related fields (also many to many)
        :param local_only:
        :param include_hidden:
        :return: list
        """
        include_parents = True if local_only is False else PROXY_PARENTS
        fields = self.opts._get_fields(
            forward=False, reverse=True,
            include_parents=include_parents,
            include_hidden=include_hidden
        )
        if include_proxy_eq:
            children = chain.from_iterable(c._relation_tree
                                           for c in self.opts.concrete_model._meta.proxied_children
                                           if c is not self.opts)
            relations = (f.remote_field for f in children
                         if include_hidden or not f.remote_field.field.remote_field.is_hidden())
            fields = chain(fields, relations)
        return list(fields)


    def get_related_list(self):
        if hasattr(self, '_related_acts'):
            return self._related_acts

        _related_acts = []
        for rel in self._get_all_related_objects():
            if self.related_list and (rel.get_accessor_name() not in self.related_list):
                continue
            if rel.related_model not in self.admin_site._registry.keys():
                continue
            has_view_perm = self.has_model_perm(rel.related_model, 'view')
            has_add_perm = self.has_model_perm(rel.related_model, 'add')
            if not (has_view_perm or has_add_perm):
                continue

            _related_acts.append((rel, has_view_perm, has_add_perm))

        self._related_acts = _related_acts
        return self._related_acts

    def related_link(self, instance):
        links = []
        for rel, view_perm, add_perm in self.get_related_list():

            opts = rel.related_model._meta

            label = opts.app_label
            model_name = opts.model_name

            field = rel.field
            rel_name = rel.get_related_field().name

            verbose_name = force_unicode(opts.verbose_name)
            lookup_name = '%s__%s__exact' % (field.name, rel_name)
            if(instance.hasChild==False and verbose_name=='文献专题'):
                continue
            if(instance.hasChild==True and verbose_name=='专题文献属性'):
                continue
            link = ''.join(('<li class="with_menu_btn">',

                            '<a href="%s?%s=%s" title="%s"><i class="icon fa fa-th-list"></i> %s</a>' %
                          (
                            reverse('%s:%s_%s_changelist' % (
                                    self.admin_site.app_name, label, model_name)),
                            RELATE_PREFIX + lookup_name, str(instance.pk), verbose_name, verbose_name) if view_perm else
                            '<a><span class="text-muted"><i class="icon fa fa-blank"></i> %s</span></a>' % verbose_name,

                            '<a class="add_link dropdown-menu-btn" href="%s?%s=%s"><i class="icon fa fa-plus pull-right"></i></a>' %
                          (
                            reverse('%s:%s_%s_add' % (
                                    self.admin_site.app_name, label, model_name)),
                            RELATE_PREFIX + lookup_name, str(
                instance.pk)) if add_perm else "",

                '</li>'))
            links.append(link)
        ul_html = '<ul class="dropdown-menu" role="menu">%s</ul>' % ''.join(
            links)
        return '<div class="dropdown related_menu pull-right"><a title="%s" class="relate_menu dropdown-toggle" data-toggle="dropdown"><i class="icon fa fa-list"></i></a>%s</div>' % (_('Related Objects'), ul_html)
    related_link.short_description = '&nbsp;'
    related_link.allow_tags = True
    related_link.allow_export = False
    related_link.is_column = False

    def get_list_display(self, list_display):
        if self.use_related and len(self.get_related_list()):
            list_display.append('related_link')
            self.admin_view.related_link = self.related_link
        return list_display

    def get_list_queryset(self,__):
        queryset = __()
        if '_rel_subParent__id__exact' in self.admin_view.request.GET:
            parent = int(self.admin_view.request.GET['_rel_subParent__id__exact'])
        else:
            parent = None
        queryset = queryset.filter(subParent_id=parent)
        return queryset





class BookmarkPlugin1(BaseAdminPlugin):
    selfmark = False
    list_bookmarks = []
    show_bookmarks = True
    menu_title = ''

    def init_request(self,*args,**kwargs):
        return bool(self.selfmark)

    def get_context(self, context):
            self.show_bookmarks = True
            bookmarks = []
            current_qs = '&'.join(['%s=%s' % (k, v) for k, v in sorted(
                filter(lambda i: bool(
                    i[1] and (i[0] in (COL_LIST_VAR, ORDER_VAR, SEARCH_VAR) or i[0].startswith(FILTER_PREFIX)
                              or i[0].startswith(RELATE_PREFIX))), self.request.GET.items()))])

            model_info = (self.opts.app_label, self.opts.model_name)
            has_selected = False
            menu_title = self.menu_title
            list_base_url = reverse('xadmin:%s_%s_changelist' %
                                    model_info, current_app=self.admin_site.name)

            # local bookmarks
            for bk in self.list_bookmarks:
                title = bk['title']
                params = dict(
                    [(FILTER_PREFIX + k, v) for (k, v) in bk['query'].items()])
                if 'order' in bk:
                    params[ORDER_VAR] = '.'.join(bk['order'])
                if 'cols' in bk:
                    params[COL_LIST_VAR] = '.'.join(bk['cols'])
                if 'search' in bk:
                    params[SEARCH_VAR] = bk['search']

                def check_item(i):
                    return bool(i[1]) or i[1] == False

                bk_qs = '&'.join(['%s=%s' % (k, v) for k, v in sorted(filter(check_item, params.items()))])

                url = list_base_url + '?' + bk_qs
                selected = (current_qs == bk_qs)

                bookmarks.append(
                    {'title': title, 'selected': selected, 'url': url})
                if selected:
                    menu_title = title
                    has_selected = True

            content_type = ContentType.objects.get_for_model(self.model)
            bk_model_info = (Bookmark._meta.app_label, Bookmark._meta.model_name)
            bookmarks_queryset = Bookmark.objects.filter(
                content_type=content_type,
                url_name='xadmin:%s_%s_changelist' % model_info
            ).filter(Q(user=self.user) | Q(is_share=True))

            for bk in bookmarks_queryset:
                selected = (current_qs == bk.query)

                if self.has_change_permission(bk):
                    change_or_detail = 'change'
                else:
                    change_or_detail = 'detail'

                bookmarks.append({'title': bk.title, 'selected': selected, 'url': bk.url, 'edit_url':
                    reverse('xadmin:%s_%s_%s' % (bk_model_info[0], bk_model_info[1], change_or_detail),
                            args=(bk.id,))})
                if selected:
                    menu_title = bk.title
                    has_selected = True

            post_url = reverse('xadmin:%s_%s_bookmark' % model_info,
                               current_app=self.admin_site.name)

            new_context = {
                'bk_menu_title': menu_title,
                'bk_bookmarks': bookmarks,
                'bk_current_qs': current_qs,
                'bk_has_selected': has_selected,
                'bk_list_base_url': list_base_url,
                'bk_post_url': post_url,
                'has_add_permission_bookmark': self.admin_view.request.user.has_perm('xadmin.add_bookmark'),
                'has_change_permission_bookmark': self.admin_view.request.user.has_perm('xadmin.change_bookmark')
            }
            context.update(new_context)
            return context


    def get_media(self, media):
        return media + self.vendor('xadmin.plugin.bookmark.js')



    def block_nav_menu(self, context, nodes):
        if self.show_bookmarks:
            nodes.insert(0, loader.render_to_string('xadmin/blocks/model_list.nav_menu.bookmarks.html',
                                                            context=get_context_dict(context)))


class IncorrectLookupParameters(Exception):
    pass


class SelfFilterPlugin(BaseAdminPlugin):
    list_filter = ()
    search_fields = ()
    free_query_filter = True
    selfilter = False

    def init_request(self, *args, **kwargs):
        return bool(self.selfilter)

    def lookup_allowed(self, lookup, value):
        model = self.model
        # Check FKey lookups that are allowed, so that popups produced by
        # ForeignKeyRawIdWidget, on the basis of ForeignKey.limit_choices_to,
        # are allowed to work.
        for l in model._meta.related_fkey_lookups:
            for k, v in widgets.url_params_from_lookup_dict(l).items():
                if k == lookup and v == value:
                    return True

        parts = lookup.split(LOOKUP_SEP)

        # Last term in lookup is a query term (__exact, __startswith etc)
        # This term can be ignored.
        if len(parts) > 1 and parts[-1] in QUERY_TERMS:
            parts.pop()

        # Special case -- foo__id__exact and foo__id queries are implied
        # if foo has been specificially included in the lookup list; so
        # drop __id if it is the last part. However, first we need to find
        # the pk attribute name.
        rel_name = None
        for part in parts[:-1]:
            try:
                field = model._meta.get_field(part)
            except FieldDoesNotExist:
                # Lookups on non-existants fields are ok, since they're ignored
                # later.
                return True
            if hasattr(field, 'rel'):
                model = field.rel.to
                rel_name = field.rel.get_related_field().name
            elif is_related_field(field):
                model = field.model
                rel_name = model._meta.pk.name
            else:
                rel_name = None
        if rel_name and len(parts) > 1 and parts[-1] == rel_name:
            parts.pop()

        if len(parts) == 1:
            return True
        clean_lookup = LOOKUP_SEP.join(parts)
        return clean_lookup in self.list_filter

    def get_list_queryset(self, queryset):
        lookup_params = dict([(smart_str(k)[len(FILTER_PREFIX):], v) for k, v in self.admin_view.params.items()
                              if smart_str(k).startswith(FILTER_PREFIX) and v != ''])
        for p_key, p_val in lookup_params.iteritems():
            if p_val == "False":
                lookup_params[p_key] = False
        use_distinct = False

        # for clean filters
        self.admin_view.has_query_param = bool(lookup_params)
        self.admin_view.clean_query_url = self.admin_view.get_query_string(remove=
                                                                           [k for k in self.request.GET.keys() if k.startswith(FILTER_PREFIX)])

        # Normalize the types of keys
        if not self.free_query_filter:
            for key, value in lookup_params.items():
                if not self.lookup_allowed(key, value):
                    raise SuspiciousOperation(
                        "Filtering by %s not allowed" % key)

        self.filter_specs = []
        if self.list_filter:
            for list_filter in self.list_filter:
                if callable(list_filter):
                    # This is simply a custom list filter class.
                    spec = list_filter(self.request, lookup_params,
                                       self.model, self)
                else:
                    field_path = None
                    field_parts = []
                    if isinstance(list_filter, (tuple, list)):
                        # This is a custom FieldListFilter class for a given field.
                        field, field_list_filter_class = list_filter
                    else:
                        # This is simply a field name, so use the default
                        # FieldListFilter class that has been registered for
                        # the type of the given field.
                        field, field_list_filter_class = list_filter, filter_manager.create
                    if not isinstance(field, models.Field):
                        field_path = field
                        field_parts = get_fields_from_path(
                            self.model, field_path)
                        field = field_parts[-1]
                    spec = field_list_filter_class(
                        field, self.request, lookup_params,
                        self.model, self.admin_view, field_path=field_path)

                    if len(field_parts)>1:
                        # Add related model name to title
                        spec.title = "%s %s"%(field_parts[-2].name,spec.title)

                    # Check if we need to use distinct()
                    use_distinct = (use_distinct or
                                    lookup_needs_distinct(self.opts, field_path))
                if spec and spec.has_output():
                    try:
                        new_qs = spec.do_filte(queryset)
                    except ValidationError, e:
                        new_qs = None
                        self.admin_view.message_user(_("<b>Filtering error:</b> %s") % e.messages[0], 'error')
                    if new_qs is not None:
                        queryset = new_qs

                    self.filter_specs.append(spec)

        self.has_filters = bool(self.filter_specs)
        self.admin_view.filter_specs = self.filter_specs
        self.admin_view.used_filter_num = len(
            filter(lambda f: f.is_used, self.filter_specs))

        try:
            for key, value in lookup_params.items():
                use_distinct = (
                    use_distinct or lookup_needs_distinct(self.opts, key))
        except FieldDoesNotExist, e:
            raise IncorrectLookupParameters(e)

        try:
            queryset = queryset.filter(**lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            raise
        except Exception, e:
            raise IncorrectLookupParameters(e)

        query = self.request.GET.get(SEARCH_VAR, '')

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        if self.search_fields and query:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in self.search_fields]
            for bit in query.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.opts, search_spec):
                        use_distinct = True
                        break
            self.admin_view.search_query = query


        if use_distinct:
            return queryset.distinct()
        else:
            return queryset

    # Media
    def get_media(self, media):
        if bool(filter(lambda s: isinstance(s, DateFieldListFilter), self.filter_specs)):
            media = media + self.vendor('datepicker.css', 'datepicker.js',
                                        'xadmin.widget.datetime.js')
        if bool(filter(lambda s: isinstance(s, RelatedFieldSearchFilter), self.filter_specs)):
            media = media + self.vendor(
                'select.js', 'select.css', 'xadmin.widget.select.js')
        return media + self.vendor('xadmin.plugin.filters.js')

    # Block Views
    def block_nav_menu(self, context, nodes):
        if self.has_filters:
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.nav_menu.filters.html',
                                                 context=get_context_dict(context)))

    def block_nav_form(self, context, nodes):
        if self.search_fields:
            context = get_context_dict(context or {})  # no error!
            context.update({
                'search_var': SEARCH_VAR,
                'remove_search_url': self.admin_view.get_query_string(remove=[SEARCH_VAR]),
                'search_form_params': self.admin_view.get_form_params(remove=[SEARCH_VAR])
            })
            nodes.append(
                loader.render_to_string(
                    'xadmin/blocks/model_list.nav_form.search_form.html',
                    context=context)
            )






class AgeListFilter():
    title = _(u'年龄段')
    parameter_name = 'ages'

    def lookups(self, request, model_admin):
        return (
            ('0', _(u'未成年')),
            ('1', _(u'成年人')),
            ('2', _(u'老年人')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(age__lt='18')
        if self.value() == '1':
            return queryset.filter(age__gte='18', age__lte='50')
        if self.value() == '2':
            return queryset.filter(age__gt='50')