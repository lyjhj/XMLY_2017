# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-04-06 13:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('himalaya', '0020_auto_20161122_2145'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookList',
            fields=[
                ('bookID', models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='\u4e66\u76eeID')),
                ('author', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u4f5c\u8005')),
                ('nationality', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u4f5c\u8005\u56fd\u522b')),
                ('bNameCH', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u8457\u4f5c\u540d\u79f0\uff08CH\uff09')),
                ('bNameEN', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u8457\u4f5c\u540d\u79f0\uff08EN\uff09')),
                ('translator', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u8bd1\u8005')),
                ('press', models.CharField(blank=True, max_length=2000, null=True, verbose_name='\u51fa\u7248\u793e')),
                ('pubdate', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u51fa\u7248\u65f6\u95f4')),
                ('Publication', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u51fa\u7248\u520a\u7269')),
                ('dopub', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u520a\u7269\u65e5\u671f')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='\u9898\u89e3')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='\u5907\u6ce8')),
                ('inputUser', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u5f55\u5165\u4eba')),
                ('inputTime', models.DateField(auto_now_add=True, verbose_name='\u5f55\u5165\u65f6\u95f4')),
                ('pageNum', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6240\u5728\u520a\u7269\u9875\u7801')),
            ],
            options={
                'verbose_name': '\u4e66\u76ee\u5217\u8868',
                'verbose_name_plural': '\u4e66\u76ee\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RouteName', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u7ebf\u8def\u540d\u79f0')),
                ('RoutePer', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u6e38\u5386\u4eba')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='\u5907\u6ce8')),
                ('bookID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='himalaya.BookList', verbose_name='\u4e66\u76eeID')),
            ],
            options={
                'verbose_name': '\u6e38\u5386\u7ebf\u8def',
                'verbose_name_plural': '\u6e38\u5386\u7ebf\u8def',
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sitenameCH', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u5730\u70b9')),
                ('sitenameEN', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u82f1\u6587/\u62fc\u97f3')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name='\u7ecf\u5ea6')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name='\u7eac\u5ea6')),
                ('altitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name='\u6d77\u62d4')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='himalaya.Category', verbose_name='\u6240\u5c5e\u884c\u653f\u533a')),
            ],
            options={
                'verbose_name': '\u5730\u70b9\u4fe1\u606f',
                'verbose_name_plural': '\u5730\u70b9\u4fe1\u606f',
            },
        ),
        migrations.CreateModel(
            name='TravelData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('toa', models.DateField(blank=True, null=True, verbose_name='\u5230\u8fbe\u65f6\u95f4')),
                ('tol', models.DateField(blank=True, null=True, verbose_name='\u79bb\u5f00\u65f6\u95f4')),
                ('transportation', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u4ea4\u901a\u65b9\u5f0f')),
                ('nation', models.TextField(blank=True, null=True, verbose_name='\u6e38\u5386\u5730\u6c11\u65cf')),
                ('police', models.TextField(blank=True, null=True, verbose_name='\u6e38\u5386\u5730\u6cbb\u5b89')),
                ('economy', models.TextField(blank=True, null=True, verbose_name='\u6e38\u5386\u5730\u7ecf\u6d4e')),
                ('agriculture', models.TextField(blank=True, null=True, verbose_name='\u6e38\u5386\u5730\u519c\u4e1a')),
                ('custom', models.TextField(blank=True, null=True, verbose_name='\u98ce\u4fd7\u6587\u5316')),
                ('religion', models.TextField(blank=True, null=True, verbose_name='\u5b97\u6559')),
                ('history', models.TextField(blank=True, null=True, verbose_name='\u5386\u53f2')),
                ('education', models.TextField(blank=True, null=True, verbose_name='\u6e38\u5386\u5730\u6559\u80b2')),
                ('geography', models.TextField(blank=True, null=True, verbose_name='\u81ea\u7136\u5730\u7406')),
                ('other', models.TextField(blank=True, null=True, verbose_name='\u5176\u4ed6')),
                ('inputUser', models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u5f55\u5165\u4eba')),
                ('inputTime', models.DateField(auto_now_add=True, verbose_name='\u5f55\u5165\u65f6\u95f4')),
                ('DataPage', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6570\u636e\u9875\u7801')),
                ('order', models.IntegerField(blank=True, null=True, verbose_name='\u5e8f\u5217\u53f7')),
                ('RouteName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='himalaya.Route', verbose_name='\u7ebf\u8def')),
                ('siteid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='himalaya.Site', verbose_name='\u5730\u70b9')),
            ],
            options={
                'verbose_name': '\u6e38\u5386\u70b9\u6570\u636e',
                'verbose_name_plural': '\u6e38\u5386\u70b9\u6570\u636e',
            },
        ),
        migrations.CreateModel(
            name='Travelgraph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graph', models.ImageField(blank=True, null=True, upload_to='himalaya/travelgraph')),
                ('traverData', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='himalaya.TravelData')),
            ],
            options={
                'verbose_name': '\u6e38\u5386\u5730\u56fe\u7247',
                'verbose_name_plural': '\u6e38\u5386\u5730\u56fe\u7247',
            },
        ),
        migrations.AlterField(
            model_name='filebaseinfo',
            name='subjecttype',
            field=models.IntegerField(blank=True, default=-1, editable=False, verbose_name='\u4e13\u9898\u7c7b\u578b'),
        ),
    ]
