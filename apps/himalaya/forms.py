# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from adminx import *
from django.dispatch import receiver
from .models import FileBaseInfo
from django.db.models import signals
from django.forms import ModelForm, CharField, TextInput
from django import forms
import datetime
from django.contrib.admin import widgets

class FileTypeForm(forms.ModelForm):
	print 'asdf'
	#@receiver(signals.m2m_changed, sender=FileBaseInfo.fileType.though)
	def save(self, commit=True):
		#super(FileTypeForm, self).save()

		print 'save file Type'
		pass


	class Meta:
		model = FileType
		fields = '__all__'


class FileBaseInfoForm(forms.ModelForm):
	pubdate = forms.IntegerField(required=False)


	class Meta:
		model = FileBaseInfo
		fields = '__all__'


class ViewForm(forms.ModelForm):
	class Meta:
		model = View
		fields = '__all__'

	def clean_viewPath(self):
		vp = self.cleaned_data['viewPath']
		if not vp.name.endswith('.zip'):
			raise forms.ValidationError('zip only')
		return vp






class FieldSearchForm(forms.Form):
	"""搜索表单"""
	title = forms.CharField(label='标题', max_length=50, required=False)
	keywords = forms.CharField(label='关键词', max_length=50, required=False)
	creator = forms.CharField(label='作者', max_length=50, required=False)
	language = forms.CharField(label='语言类型', max_length=50, required=False)
	file_type = forms.CharField(label='文件类型', max_length=50, required=False)
	start_date = forms.DateField(label='起始日期', widget=forms.SelectDateWidget(years=range(1970, 2055)), required=False)
	end_date = forms.DateField(label='结束日期', widget=forms.SelectDateWidget(years=range(1970, 2055)), required=False)


class SujectThemeForm(forms.ModelForm):
	qiantaiid = forms.IntegerField(show_hidden_initial=False)
	treenum = forms.IntegerField(show_hidden_initial=False)

	class Meta:
		model = SubjectTheme
		fields = ('fieldName', 'fieldType', 'isPrompt', 'promtInfo', 'isMust')



		# class FileTypeForm(forms.ModelForm):
		#
		# 	class Meta:
		# 		model=FileType
		# 		fields=('fileTypeName')


class RouteForm(forms.ModelForm):


	class Meta:
		model = Route
		fields = '__all__'


class site_form(forms.ModelForm):


	class Meta:
		model = Site
		fields ='__all__'


class traveldata_form(forms.ModelForm):


	class Meta:
		model = TravelData
		fields =('siteid','toa','tol','transportation','nation','police','economy','agriculture','custom','religion','history','education','geography','other','inputUser','DataPage','mileage')
