# coding=utf-8
from haystack import indexes
from haystack.indexes import MultiValueField
from models import *
from django.shortcuts import loader
from django.template import Context

import search_utils
# class FileExtendInfoIndex(indexes.SearchIndex, indexes.Indexable):
#     # 不需要进行全文检索，没有意义，为专题属性建索引，（field）为fieldId,(value)为fieldvalue
#     # filedValue = indexes.CharField(model_attr='filedValue', faceted=True)
#     text = indexes.NgramField(document=True)
#     fileId = indexes.IntegerField(model_attr='fileId',faceted=True)
#     fieldId = indexes.MultiValueField()
#
#     def get_model(self):
#         return FileExtendInfo
#
#     def index_queryset(self, using=None):
#         return self.get_model().objects.all()
#
#     def prepare_fieldId(self,obj):
#         pass
        #如果是树类型，则可以建立索引文档。


# 建立pdf索引示例
class BaseFileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')  # 标题u
    pubDate = indexes.DateTimeField(model_attr='pubDate',null=True)  # 出版时间
    creator = indexes.CharField(model_attr='creator',null=True)  # 作者/编者
    keywords = indexes.CharField(model_attr='keywords',null=True)  # 关键字
    check = indexes.BooleanField(model_attr='check',null=True)
    updateDate = indexes.DateTimeField(model_attr='updateDate', null=True)
# 用于面搜索和精确搜索
    fileType = indexes.MultiValueField()
    fileFormat = indexes.MultiValueField()
    spatial = indexes.MultiValueField()
    discipline = indexes.MultiValueField()
    language = indexes.MultiValueField()  # 需要prepare_language函数做预处理
    subjecttype = indexes.IntegerField(model_attr='subjecttype',null=True)  # 专题类型



    def get_model(self):
        return FileBaseInfo

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.order_by('-updateDate')  # check=True才检索出来

    def prepare(self, obj):
        data = super(BaseFileIndex, self).prepare(obj)
        if obj.attachment.path.split('/')[-1].split('.')[-1] == 'pdf':
            try:
                extracted_data = search_utils.parse_to_string(obj.attachment.path)  # 文件路径
            except:
                print(obj.filecode)
                extracted_data = ''
        else:
            extracted_data = ''
        t = loader.select_template(('search/indexes/himalaya/filebaseinfo_text.txt',))
        data['text'] = t.render({'object': obj, 'extracted': extracted_data})
        ext = SubjectTheme.objects.filter(subjectId=obj.subjecttype)
        for item in ext:
            if (int(item.fieldType) == 5 or int(item.fieldType) == 6):
                ex = []
                for key in FileExtendInfo.objects.filter(fieldId=item.id,fileId=obj.id):
                    tmp = Category.objects.get(id=int(key.filedValue))
                    val = []
                    while tmp.id != int(item.corrAttri):
                        val.append(tmp.attrName)
                        tmp = Category.objects.get(id=tmp.pid_id)
                    for i in range(1,len(val)+1):
                        ss = str(i)+ '/'
                        for j in range(0,i):
                            if j<i-1:
                                ss = ss + str(val[len(val)-1-j]).strip() +'/'
                            else:
                                ss = ss + str(val[len(val) - 1 - j]).strip()
                        ex.append(ss)
                    cer = ex[len(ex)-1].split('/', 1)
                    path = str(int(cer[0]) + 1) + '/' + cer[1]  + '/' + val[0]
                    ex.append(path)
            else:
                ex = []
                for key in FileExtendInfo.objects.filter(fieldId=item.id,fileId=obj.id):
                    ex.append(key.filedValue)
            if(len(ex)!=0):
                strs = str(item.id)+'_ext'
                data[strs] = ex
        return data

    def prepare_language(self, obj):
        return [lang.lanTypeName for lang in obj.language.all()]

    def prepare_spatial(self, obj):
        return [spa.spcaeTypeName for spa in obj.spatial.all()]

    def prepare_discipline(self, obj):
        return [dis.disciplineTypeName for dis in obj.discipline.all()]

    def prepare_fileFormat(self, obj):
        return [filemat.formatTypeName for filemat in obj.fileFormat.all()]

    def prepare_fileType(self, obj):
        return [file_type.fileTypeName for file_type in obj.fileType.all()]

class TravelDataIndex(indexes.SearchIndex, indexes.Indexable):

    # 用于面搜索和精确搜索
    text = indexes.NgramField(document=True, use_template=True)
    #traveldata表
    toa = indexes.DateTimeField(model_attr='toa', null=True)  # 出发时间
    tol = indexes.DateTimeField(model_attr='tol', null=True) #结束时间
    transportation = indexes.CharField(model_attr='transportation',null=True)  # 交通方式
    #所见所闻检索
    nation = indexes.CharField(model_attr='nation',null=True)
    police = indexes.CharField(model_attr='police',null=True)
    economy = indexes.CharField(model_attr='economy',null=True)
    agriculture = indexes.CharField(model_attr='agriculture',null=True)
    # custom = indexes.CharField(model_attr='custom',null=True)
    religion = indexes.CharField(model_attr='religion',null=True)
    history =indexes.CharField(model_attr='history',null=True)
    education =indexes.CharField(model_attr='education',null=True)
    geography = indexes.CharField(model_attr='geography',null=True)
    other = indexes.CharField(model_attr='other',null=True)

    RouteNameid = indexes.IntegerField(null=True)  # 路线id
    siteid = indexes.IntegerField(null=True)  #  地点id



    def get_model(self):
        return TravelData


    def prepare(self, obj):
        data = super(TravelDataIndex, self).prepare(obj)
        t = loader.select_template(('search/indexes/himalaya/traveldata_text.txt',))
        data['text'] = t.render({'object': obj})
        return data

    def prepare_siteid(self, obj):
        return obj.siteid_id

    def prepare_RouteNameid(self, obj):
        return obj.RouteName_id


class siteIndex(indexes.SearchIndex, indexes.Indexable):

    # 用于面搜索和精确搜索
    text = indexes.NgramField(document=True, use_template=True)
    #site表里
    sitenameCH = indexes.CharField(model_attr='sitenameCH',null=True)  # 中文地名
    siteNameEN = indexes.CharField(model_attr='sitenameEN',null=True)  # 英文地名


    def get_model(self):
        return Site

    def prepare(self, obj):
        data = super(siteIndex, self).prepare(obj)
        t = loader.select_template(('search/indexes/himalaya/site_text.txt',))
        data['text'] = t.render({'object': obj})
        return data



class routeIndex(indexes.SearchIndex, indexes.Indexable):

    # 用于面搜索和精确搜索
    text = indexes.NgramField(document=True, use_template=True)
    #route表里
    RouteName = indexes.CharField(model_attr='RouteName',null=True)  # 路线名
    RoutePer = indexes.CharField(model_attr='RoutePer',null=True)  # 游历者
    bookID = indexes.IntegerField(null=True)  # 游历者
    def get_model(self):
        return Route

    def prepare(self, obj):
        data = super(routeIndex, self).prepare(obj)
        t = loader.select_template(('search/indexes/himalaya/route_text.txt',))
        data['text'] = t.render({'object': obj})
        return data

    def prepare_bookID(self, obj):
        return obj.bookID_id


class booklistIndex(indexes.SearchIndex, indexes.Indexable):
    # 用于面搜索和精确搜索
    text = indexes.NgramField(document=True, use_template=True)
    #booklist表
    bNameCH = indexes.CharField(model_attr='bNameCH',null=True)  # 中文书名
    bNameEN = indexes.CharField(model_attr='bNameEN',null=True)  # 英文书名

    def get_model(self):
        return BookList

    def prepare(self, obj):
        data = super(booklistIndex, self).prepare(obj)
        t = loader.select_template(('search/indexes/himalaya/booklist_text.txt',))
        data['text'] = t.render({'object': obj})
        return data





