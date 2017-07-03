from haystack.exceptions import NotHandled
from django.db import models
from haystack import signals
from .models import *

from collections import OrderedDict

from haystack.signals import RealtimeSignalProcessor
from django.core.exceptions import ObjectDoesNotExist

class BatchingSignalProcessor(RealtimeSignalProcessor):
    """
    RealtimeSignalProcessor connects to Django model signals
    we store them locally for processing later - must call
    ``flush_changes`` from somewhere else (eg middleware)
    """

    # Haystack instantiates this as a singleton

    _change_list = OrderedDict()

    def _add_change(self, method, sender, instance):
        key = (sender, instance.pk)
        if key in self._change_list:
            del self._change_list[key]
        self._change_list[key] = (method, instance)

    def handle_save(self, sender, instance, created, raw, **kwargs):
        method = super(BatchingSignalProcessor, self).handle_save
        self._add_change(method, sender, instance)

    def handle_delete(self, sender, instance, **kwargs):
        method = super(BatchingSignalProcessor, self).handle_delete
        self._add_change(method, sender, instance)

    def flush_changes(self):
        while True:
            try:
                (sender, pk), (method, instance) = self._change_list.popitem(last=False)
            except KeyError:
                break
            else:
                method(sender, instance)

class lanM2MSignalProcessor(signals.BaseSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        """
		Given an individual model instance, determine which backends the
		update should be sent to & update the object on those backends.
		"""
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            try:
                index = self.connections[using].get_unified_index().get_index(instance.__class__)
                index.update_object(instance, using=using)
            except NotHandled:

                pass
    def _setup(self):
        # Listen only to the ``User`` model.
        models.signals.m2m_changed.connect(self.handle_save(), sender=FileBaseInfo.language)
        models.signals.m2m_changed.connect(self.handle_delete, sender=FileBaseInfo.language)

    def teardown(self):
        # Disconnect only for the ``User`` model.
        # index = self.connections[using].get_unified_index().get_index(instance.__class__)
        models.signals.m2m_changed.disconnect(self.handle_save, sender=FileBaseInfo.language)
        models.signals.m2m_changed.disconnect(self.handle_delete, sender=FileBaseInfo.language)

def save(self,instance,tmp):
    for item in FileExtendInfo.objects.filter(fieldId=tmp.id, filedValue=str(instance.id)):
        try:
            related_obj=FileBaseInfo.objects.get(id=item.fileId)
            self.handle_save(related_obj.__class__, related_obj)
            for ite in Category.objects.filter(pid=instance):
                save(self, ite, tmp)
        except ObjectDoesNotExist:
            pass

def delete(self,instance,tmp):
    for item in FileExtendInfo.objects.filter(fieldId=tmp.id, filedValue=str(instance.id)):
        try:
            related_obj=FileBaseInfo.objects.get(id=item.fileId)
            self.handle_delete(related_obj.__class__, related_obj)
            for ite in Category.objects.filter(pid=instance):
                delete(self, ite, tmp)
        except ObjectDoesNotExist:
            pass

class RelatedRealtimeSignalProcessor(RealtimeSignalProcessor):
# Extension to haystack's RealtimeSignalProcessor not only causing the
# search_index to update on saved model, but also for image url, which is needed to show
# images on search results
    def handle_save(self, sender, instance, **kwargs):
        print 'test', instance._meta.db_table
        if hasattr(instance, 'filebaseinfo_set'):
            for related_obj in instance.filebaseinfo_set.all():
                self.handle_save(related_obj.__class__, related_obj)
        if hasattr(instance,'_meta') and instance._meta.db_table=='himalaya_category':
            tmp = instance
            while tmp.pid_id and tmp.pid_id !=0:
                tmp = Category.objects.get(id=tmp.pid_id)
            try:
                tms = SubjectTheme.objects.get(corrAttri=tmp.id)
                save(self, instance,tms)
            except ObjectDoesNotExist:
                pass
        return super(RelatedRealtimeSignalProcessor, self).handle_save(sender, instance, **kwargs)

    def handle_delete(self, sender, instance, **kwargs):
        # uselesss
        if hasattr(instance, 'filebaseinfo_set'):
            for related_obj in instance.filebaseinfo_set.all():
                print(related_obj,related_obj.__class__)
                self.handle_delete(related_obj.__class__, related_obj)
        if hasattr(instance,'_meta') and instance._meta.db_table=='himalaya_category':
            tmp = instance
            while tmp.pid_id != 0:
                tmp = Category.objects.get(id=tmp.pid_id)
            try:
                tms = SubjectTheme.objects.get(corrAttri=tmp.id)
                delete(self, instance, tms)
            except ObjectDoesNotExist:
                pass
        return super(RelatedRealtimeSignalProcessor, self).handle_delete(sender, instance, **kwargs)