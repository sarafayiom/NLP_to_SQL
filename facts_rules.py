import collections
import collections.abc
from xml.sax.saxutils import XMLGenerator

if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'Callable'):
    collections.Callable = collections.abc.Callable
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

 
import re
from experta import (
    Fact, Field, KnowledgeEngine, Rule, DefFacts,
    W, MATCH, AS, NOT, AND, OR, TEST
)


#  Facts (وحدات المعرفة)
 

class TableFact(Fact):
#يمثل اسم الجدول والمرادفات تبعو
    name     = Field(str,  mandatory=True)
    synonyms = Field(list, default=[])

class ColumnFact(Fact):
    #عمود الموجود في جدول
    table     = Field(str, mandatory=True)#اسم الجدول
    column    = Field(str, mandatory=True)#اسم العامود
    data_type = Field(str, default="TEXT")#نوع الداتا
    synonyms  = Field(list, default=[])#مرادفات العامود

class RelationFact(Fact):
     #العلاقة بين الجدول
    #يعني شو العلاقات الموجودة أصلا قبل ما المستخدم يدخل اي شي
    from_table = Field(str, mandatory=True)#من اي جدول
    from_col   = Field(str, mandatory=True)#من اي عامود
    to_table   = Field(str, mandatory=True)#لاي جدول
    to_col     = Field(str, mandatory=True)#لأي عامود

class TokenFact(Fact):
 # هي مشان قسم الجملة للكلمات كل كلمة الها index
    index = Field(int, mandatory=True)
    text  = Field(str, mandatory=True)

class NumberFact(Fact):
  #مشان اي رقم بالجملة 
    value = Field(float, mandatory=True)

class SentenceFact(Fact):
    # المشكلة 1: حقيقة الجملة الكاملة — تُمرَّر للمحرك قبل التشغيل
    # تُستخدم داخل Rules بدل self._sentence يلي ما بيشتغل
    text = Field(str, mandatory=True)

class MappedTableFact(Fact):
    # هي مشان لما اربط كلمة بجدول 
    original = Field(str, mandatory=True)
    table    = Field(str, mandatory=True)

class MappedColumnFact(Fact):
    #هي مشان لما اربط كلمة بعامود داخل جدول
    original = Field(str, mandatory=True)
    table    = Field(str, mandatory=True)
    column   = Field(str, mandatory=True)

class OperationFact(Fact):
    #نوع العملية: SELECT / COUNT / AVG / SUM / MAX / MIN
    op_type = Field(str, mandatory=True)

class SelectColumnFact(Fact):
 #شو الاعمدة يلي بدك تعرضها بselect
    table  = Field(str, mandatory=True)
    column = Field(str, mandatory=True)

class FromTableFact(Fact):
    # هي مشان المعلومات من اي جدول عم تجيب المعلومات 
    # مشان الfrom
    table = Field(str, mandatory=True)

class JoinFact(Fact):
    #رح أعمل JOIN فعلي
    from_table = Field(str, mandatory=True)
    from_col   = Field(str, mandatory=True)
    to_table   = Field(str, mandatory=True)
    to_col     = Field(str, mandatory=True)

class WhereFact(Fact):
    #where
    table    = Field(str,    mandatory=True)# أي جدول عم يطبق عليه الشرط
    column   = Field(str,    mandatory=True)# اي عامود 
    operator = Field(str,    mandatory=True)#طريقة المقارنة
    value    = Field(object, mandatory=True)#القيمة يلي عم نقارن معها
    kind     = Field(str,    default="numeric")  # نوع المقارنة: string / like / numeric / subquery / negation
    group_id = Field(int, default=0)#هي مشان اذا عندي شروط متعددة يعني عندي كذا where

class HavingFact(Fact):
    #شرط الفلترة المتقدمة بعد التجميع GROUP BY
    table    = Field(str,    mandatory=True)
    column   = Field(str,    mandatory=True)
    operator = Field(str,    mandatory=True)  # '>', '<', '='
    value    = Field(object, mandatory=True)  # رقم أو نص

class DistinctFact(Fact):
    # مشان لما المستخدم يطلب قيم فريدة / غير مكررة
    active = Field(bool, default=True)

class LogicalOperatorFact(Fact):
    operator = Field(str, mandatory=True)  # "AND" أو "OR"


# لما يكون عندي SELECT داخل SELECT
class SubqueryFact(Fact):
    table     = Field(str, mandatory=True)   # الجدول يلي بينطبق عليه الاستعلام الفرعي
    column    = Field(str, mandatory=True)   # العامود يلي بنحسب العملية عليه
    operation = Field(str, mandatory=True)   # العملية: AVG / MAX / MIN / SUM / COUNT

class BetweenFact(Fact):
    table     = Field(str,   mandatory=True)
    column    = Field(str,   mandatory=True)
    min_value = Field(float, mandatory=True)  # الحد الأدنى
    max_value = Field(float, mandatory=True)  # الحد الأعلى

class NegationFact(Fact):
    table    = Field(str,    mandatory=True)
    column   = Field(str,    mandatory=True)
    operator = Field(str,    mandatory=True)  # "!=" أو "NOT LIKE"
    value    = Field(object, mandatory=True)


# لما يكون عندي نفس الجدول عم يرتبط مع حالو
class SelfJoinFact(Fact):
    table    = Field(str, mandatory=True)  # الجدول يلي بينربط بنفسه
    from_col = Field(str, mandatory=True)  # عامود المفتاح الخارجي  
    to_col   = Field(str, mandatory=True)  # عامود المفتاح الرئيسي  
    alias1   = Field(str, mandatory=True)  # الاسم المستعار للنسخة الأولى  
    alias2   = Field(str, mandatory=True)  # الاسم المستعار للنسخة الثانية  
    
class GroupByFact(Fact):
    #تجميع البيانات 
    table  = Field(str, mandatory=True)
    column = Field(str, mandatory=True)

class OrderByFact(Fact):
    #ORDER BY
    table     = Field(str, mandatory=True)
    column    = Field(str, mandatory=True)
    direction = Field(str, default="ASC")

class LimitFact(Fact):
     # عدد النتائج
     # مثلا بدي اول 5 
    value = Field(int, mandatory=True)


class Phase(Fact):
    step = Field(str, default="START")

class SQLBuffer(Fact):
    text = Field(str, default="")

class ProcessedFact(Fact):
    fact_type = Field(str)
    table = Field(str)
    column = Field(str, default="")
    value = Field(object, default="")

class JoinedTable(Fact):
    table = Field(str)
class Phase(Fact):
    step = Field(str, mandatory=True)

class SQLBuffer(Fact):
    text = Field(str, default="")

class ProcessedFact(Fact):
    fact_type = Field(str, mandatory=True)
    table = Field(str, mandatory=True)

class FromTableFact(Fact):
    table = Field(str, mandatory=True)

class ProjectionFact(Fact):
    table = Field(str, mandatory=True)
    column = Field(str, mandatory=True)

class BetweenFact(Fact):
    table = Field(str, mandatory=True)
    column = Field(str, mandatory=True)
    min_value = Field(float, mandatory=True)
    max_value = Field(float, mandatory=True)

class NegationFact(Fact):
    table = Field(str, mandatory=True)
    column = Field(str, mandatory=True)
    operator = Field(str, mandatory=True)
    value = Field(str, mandatory=True)

class SelfJoinFact(Fact):
    table = Field(str, mandatory=True)
    from_col = Field(str, mandatory=True)
    to_col = Field(str, mandatory=True)
    alias1 = Field(str, mandatory=True)
    alias2 = Field(str, mandatory=True)
# القاموس الدلالي الكامل
 # عم اربط اسم كل جدول بكلمات الناس
#الإنسان ما بيعرف اسم الجدول الحقيقي مشان هيك عم اعطي مرادفات
 
TABLE_SYNONYMS = {
    "Album":        ["album","albums","ألبوم","ألبومات","البوم","البومات"],
    "Artist":       ["artist","artists","فنان","فنانين","مطرب","مطربين",
                     "موسيقي","موسيقيين","singer","singers"],
    "Customer":     ["customer","customers","عميل","عملاء","زبون","زبائن",
                     "مشتري","مشترين"],
    "Employee":     ["employee","employees","موظف","موظفين","موظفون",
                     "عامل","عمال","staff","worker","workers"],
    "Genre":        ["genre","genres","نوع","انواع","أنواع","تصنيف",
                     "تصنيفات","category","categories"],
    "Invoice":      ["invoice","invoices","فاتورة","فواتير","bill","bills",
                     "order","orders","طلب","طلبات","purchase","purchases","مشتريات"],
    "InvoiceLine":  ["invoiceline","invoicelines","بند","بنود","سطر","سطور"],
    "MediaType":    ["mediatype","mediatypes","وسيط","وسائط",
                     "media","format","formats","صيغة","صيغ"],
    "Playlist":     ["playlist","playlists","قائمة","قوائم",
                     "قائمة تشغيل","قوائم تشغيل"],
    "PlaylistTrack":["playlisttrack","playlisttracks"],
    "Track":        ["track","tracks","أغنية","اغنية","أغاني","اغاني",
                     "مقطوعة","مقطوعات","song","songs","music","موسيقى"],
}
# عم يربط عامود كل جدول بالمرادفات تبعو
COLUMN_SYNONYMS = {
    ("Artist",   "Name"):           ["name","اسم","اسمه","names","الاسم"],
    ("Artist",   "ArtistId"):       ["artistid","id","رقم","معرف"],

    ("Album",    "Title"):          ["title","عنوان","العنوان","اسم","name"],
    ("Album",    "AlbumId"):        ["albumid","id","رقم"],
    ("Album",    "ArtistId"):       ["artistid"],

    ("Track",    "Name"):           ["name","اسم","اسمها","الاسم","عنوان","title"],
    ("Track",    "Composer"):       ["composer","ملحن","موزع","مؤلف"],
    ("Track",    "Milliseconds"):   ["milliseconds","مدة","الوقت","duration",
                                     "length","طول","وقت"],
    ("Track",    "UnitPrice"):      ["unitprice","سعر","price","تكلفة","ثمن"],
    ("Track",    "Bytes"):          ["bytes","حجم","size"],
    ("Track",    "TrackId"):        ["trackid","id","رقم"],
    ("Track",    "GenreId"):        ["genreid"],
    ("Track",    "AlbumId"):        ["albumid"],

    ("Genre",    "Name"):           ["name","اسم","النوع","التصنيف"],
    ("Genre",    "GenreId"):        ["genreid","id"],

    ("Customer", "FirstName"):      ["firstname","الاسم","اسم","name"],
    ("Customer", "LastName"):       ["lastname","لقب","عائلة"],
    ("Customer", "Email"):          ["email","بريد","ايميل","إيميل"],
    ("Customer", "Country"):        ["country","دولة","بلد"],
    ("Customer", "City"):           ["city","مدينة","مدن"],
    ("Customer", "Phone"):          ["phone","هاتف","تلفون","موبايل"],
    ("Customer", "CustomerId"):     ["customerid","id","رقم"],

    ("Employee", "FirstName"):      ["firstname","الاسم","اسم"],
    ("Employee", "LastName"):       ["lastname","لقب"],
    ("Employee", "Title"):          ["title","لقب","منصب","وظيفة","مسمى"],
    ("Employee", "Email"):          ["email","بريد"],
    ("Employee", "HireDate"):       ["hiredate","تاريخ","توظيف","date"],
    ("Employee", "EmployeeId"):     ["employeeid","id","رقم"],

    ("Invoice",  "Total"):          ["total","مجموع","مبلغ","قيمة","amount",
                                     "إجمالي","اجمالي"],
    ("Invoice",  "InvoiceDate"):    ["invoicedate","تاريخ","date"],
    ("Invoice",  "BillingCountry"): ["billingcountry","دولة","بلد","country"],
    ("Invoice",  "CustomerId"):     ["customerid"],
    ("Invoice",  "InvoiceId"):      ["invoiceid","id","رقم"],

    ("InvoiceLine","UnitPrice"):    ["unitprice","سعر","price"],
    ("InvoiceLine","Quantity"):     ["quantity","كمية","عدد"],

    ("Playlist", "Name"):           ["name","اسم","عنوان"],
    ("Playlist", "PlaylistId"):     ["playlistid","id","رقم"],

    ("MediaType","Name"):           ["name","اسم","نوع","صيغة"],
}
# هي مشان نوع العملية
OPERATION_KEYWORDS = {
    "SELECT": ["اعرض","أظهر","اظهر","اريد","أريد","احضر","أحضر",
               "show","display","get","fetch","select","list","عرض",
               "اجلب","أجلب","ابحث","أبحث"],
    "COUNT":  ["عدد","احسب","كم","count","how many","عدّ","عد"],
    "AVG":    ["متوسط","average","avg","معدل"],
    "SUM":    ["مجموع","sum","إجمالي","اجمالي"],
    "MAX":    ["أعلى","اعلى","max","maximum","highest"],
    "MIN":    ["أقل","اقل","أصغر","اصغر","min","minimum","lowest"],
}
# هي مشان عمليات المقارنة
OPERATOR_KEYWORDS = {
    ">":    ["أكبر من","اكبر من","فوق","أعلى من","اعلى من",
             "greater than","more than","above","over"],
    "<":    ["أقل من","اقل من","تحت","أدنى من","ادنى من",
             "less than","below","under"],
    ">=":   ["أكبر من أو يساوي","على الأقل","على الاقل","at least"],
    "<=":   ["أقل من أو يساوي","على الأكثر","على الاكثر","at most"],
    "=":    ["يساوي","يساوى","equals","equal to","is"],
    "LIKE": ["مثل","يحتوي","يحتوي على","contains","like","تبدأ ب","يبدأ بـ"],
}
#ترتيب النتائج
ORDERBY_KEYWORDS = {
    "DESC": ["تنازلي","تنازليا","الأعلى أولاً","desc","descending",
             "الأكبر أولاً","من الأكبر"],
    "ASC":  ["تصاعدي","تصاعديا","ascending","asc",
             "من الأصغر","الأصغر أولاً"],
}
#هي الكلمات عم استخدمها لأعرف انو لازم شغل ترتيب
ORDER_TRIGGER   = ["رتّب","رتب","ترتيب","sort","order","order by","مرتب","مرتبة"]
#هي الكلمات بعرف انو لازم بدي عدد محدود من النتائج
LIMIT_TRIGGER   = ["أول","اول","أولى","اولى","first","top","limit","فقط","فحسب","اخر","أخر","last","final"]
#مشان اعرف انو في تجميع
GROUPBY_TRIGGER = ["لكل","per","group by","group","بحسب","حسب","تجميع","grouped"]
#الشرط يلي بعد التجميع
HAVING_TRIGGER  = ["أكثر من","اكثر من","لديهم","يمتلكون","يملكون",
                   "have more","having","اكثر"]
# مشان القيم الفريدة / غير المكررة
DISTINCT_KEYWORDS = ["فريد","فريدة","فريدين","مختلف","مختلفة","غير مكرر",
                     "غير مكررة","distinct","unique","different"]

# ترجمة القيم النصية المعروفة (دول / مدن / أنواع موسيقى)
#هي لأنو قاعدة البيانات عندي بالانجليزي فعملت ترجمة
STRING_VALUES_MAP = {
    # دول
    "كندا":"Canada","canada":"Canada",
    "فرنسا":"France","france":"France",
    "ألمانيا":"Germany","germany":"Germany",
    "أمريكا":"USA","usa":"USA","us":"USA",
    "المملكة المتحدة":"United Kingdom","uk":"United Kingdom",
    "البرازيل":"Brazil","brazil":"Brazil",
    "بلجيكا":"Belgium","belgium":"Belgium",
    "الدنمارك":"Denmark","denmark":"Denmark",
    "إيطاليا":"Italy","italy":"Italy",
    "النرويج":"Norway","norway":"Norway",
    "البرتغال":"Portugal","portugal":"Portugal",
    "إسبانيا":"Spain","spain":"Spain",
    "السويد":"Sweden","sweden":"Sweden",
    "هولندا":"Netherlands","netherlands":"Netherlands",
    "الأرجنتين":"Argentina","argentina":"Argentina",
    "أستراليا":"Australia","australia":"Australia",
    "الهند":"India","india":"India",
    "أيرلندا":"Ireland","ireland":"Ireland",
    "تشيكيا":"Czech Republic","czech":"Czech Republic",
    "فنلندا":"Finland","finland":"Finland",
    "المجر":"Hungary","hungary":"Hungary",
    "النمسا":"Austria","austria":"Austria",
    "بولندا":"Poland","poland":"Poland",
    # مدن
    "باريس":"Paris","paris":"Paris",
    "لندن":"London","london":"London",
    "برلين":"Berlin","berlin":"Berlin",
    "نيويورك":"New York","new york":"New York",
    "شيكاغو":"Chicago","chicago":"Chicago",
    "طوكيو":"Tokyo","tokyo":"Tokyo",
    "براغ":"Prague","prague":"Prague",
    "ستوكهولم":"Stockholm","stockholm":"Stockholm",
    "أوسلو":"Oslo","oslo":"Oslo",
    "ليزبن":"Lisbon","lisbon":"Lisbon",
    "برشلونة":"Barcelona","barcelona":"Barcelona",
    "مدريد":"Madrid","madrid":"Madrid",
    # أنواع موسيقى
    "روك":"Rock","rock":"Rock",
    "جاز":"Jazz","jazz":"Jazz",
    "كلاسيك":"Classical","classical":"Classical",
    "بوب":"Pop","pop":"Pop",
    "ميتال":"Metal","metal":"Metal",
    "بلوز":"Blues","blues":"Blues",
    "ريغي":"Reggae","reggae":"Reggae",
    "هيب هوب":"Hip Hop/Rap","hip hop":"Hip Hop/Rap",
    "إلكترونيك":"Electronica/Dance","electronic":"Electronica/Dance",
    "لاتيني":"Latin","latin":"Latin",
    "البديل":"Alternative & Punk","alternative":"Alternative & Punk",
    "ر اند ب":"R&B/Soul","r&b":"R&B/Soul",
    # وسائط
    "mp3":"MPEG audio file","mpeg":"MPEG audio file",
    "aac":"AAC audio file","aiff":"AIFF audio file",
}

#  العمود النصي الافتراضي لكل جدول مشان المستخدم اذا ماحدد نوع العامود
STRING_WHERE_COLUMN = {
    "Customer":  "Country",#هون يعني اي شرطwhere مطبق على جدول customer لح اختار العامودcountry
    "Invoice":   "BillingCountry",#هون بهمني بلد الفاتورة
    "Artist":    "Name",# بهمني اسم الفنان
    "Album":     "Title",#بهمني عنوان الالبوم
    "Track":     "Name",#بهمني اسم الغنية
    "Genre":     "Name",#بهمني نوع الموسيقى
    "Playlist":  "Name",#بهمني اسم القائمة
    "Employee":  "Country",#بهمني الموظف من اي بلد
    "MediaType": "Name",#بهمني اسمو نوع الملف
}

# العمود الرقمي الافتراضي لكل جدول  
NUMERIC_WHERE_COLUMN = {
    "Track":       "Milliseconds",#بهمني مدة الاغنية
    "Invoice":     "Total",#بهمني مجموع الفاتورة
    "InvoiceLine": "UnitPrice",#سعر كل وحدة
}

 
#  دوال التحليل اللغوي (NLP)
 
#هي الكلمات يلي مالها معنى في التحليل
STOP_WORDS = {
    "من","في","على","الذين","التي","الذي","الـ","و","أو",
    "مع","هم","هي","هو","لها","له","لي","الى","إلى",
    "عن","بـ","بين","كل","جميع","للـ","ب","يا",
    "the","a","an","of","in","on","with","who","which",
    "that","are","is","was","were","have","has","by",
    "for","at","to","and","or","all"
}

#توحيد الكلمات العربية حتى الكمبيوتر يفهمها بشكل ثابت
def normalize_arabic(text: str) -> str:#لح يدخل نص ولح يرجع نص 
    if not text:#مشان اذا النص فاضي
        return ""
    #مشان يشيل المسافات 
    #ويحول لاحرف صغيرة
    #ويشيل علامات التنصيص
    text = text.strip().lower().strip('"\'')
    #مشان اذا الكلمة بدات ب لل يشيل اول حرفين مثلا عنا للأغاني تصير أغاني
    if text.startswith("لل") and len(text) > 3:
        text = text[2:]
        #هي مشان ال التعريف
    if text.startswith("ال") and len(text) > 3:
        text = text[2:]
        #هي مشان كل الالفات تتحول للالف بلا همزة
    text = re.sub(r"[أإآ]", "ا", text)
    # هي مشان تحول التاء لهاء
    text = re.sub(r"ة$", "ه", text)
    # اذا كلمة اخرى ى حولها لياء
    text = re.sub(r"ى$", "ي", text)
    return text

#هي الدالة مشان تقسم الجملة لtokens
def tokenize_sentence(sentence: str):#هون لح يدخل جملة كاملة
 #عم حول الجملة للأجزاء
    s = sentence.lower().strip()# لح يصغر الأحرف ويشيل المسافات

     #هي مشان يطلع كل الارقام من الجملة
    numbers = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', s)]

    #  OR / AND
    #اذا في او أو or
    has_or  = bool(re.search(r'\bأو\b|\bor\b|\bاو\b', s))
   #اذا في و and
    has_and = (s.count(" و ") > 0 or " and " in s or
    #هي مشان اذا الجملة فيها رقمين او اكبر وفيها مقارنة كمان لح يعتبر and متل أغاني أطول من 3 و أقل من 10
               (len(numbers) >= 2 and detect_operator(sentence) is not None))

 
    string_values = []#لح تخزن القيم المهمة
    found_keys    = set()#منع تكرار
    temp = s#نسخة من الجملة الاصلية لانو لح نحذف منها لحد مانوصل من دون ما ناثر على الاصلية
    
    for k, v in sorted(STRING_VALUES_MAP.items(), key=lambda x: -len(x[0])):
        if k in temp and v not in found_keys:#هل الكلمة موجودة بالجملة وهل مو مستخدمة قبل
            string_values.append(v)#بنضيف قيمة للمصفوفة
            found_keys.add(v)#نمنع تكرارها
            temp = temp.replace(k, " ")#نشيل الكلمة من النص

    #نسخة جديدة من الجملة
    clean = s
    #هي ازالة كلمات المقارنة من الجملة
    for phrases in OPERATOR_KEYWORDS.values():
        for ph in sorted(phrases, key=len, reverse=True):
            clean = clean.replace(ph, " ")#حذفناها من الجملة
    clean = re.sub(r'\d+(?:\.\d+)?', ' ', clean)#عم شيل كل الارقام
    for k in STRING_VALUES_MAP:
        clean = clean.replace(k, " ")
#لح حول الكلمات لتكونز
    raw_tokens = re.split(r'[\s،,؟?!.\-"\'`]+', clean)
    tokens = [t.strip() for t in raw_tokens
              if t.strip() and t.strip() not in STOP_WORDS and len(t.strip()) > 1]

    return tokens, numbers, string_values, has_or, has_and


# يبحث عن عامل المقارنة
def detect_operator(sentence: str) -> str:
 # هل الجملة فيها مقارنة 
    s = sentence.lower()
    # هي رتب العمليات حسب اطول عملية
    # مشان مثلا كان عنا أكبر من او يساوي ياخدها كلها ماياخد اكبر من ويوقف 
    for op, phrases in sorted(OPERATOR_KEYWORDS.items(),
                               key=lambda x: -max(len(p) for p in x[1])):
        #بعد مارتب حسب اطول شي
        for phrase in sorted(phrases, key=len, reverse=True):
            if phrase in s:
                return op
    return None

#هي الدالة بتحدد الجهة
def detect_order_direction(sentence: str) -> str:
    s = sentence.lower()#يحول الجملة إلى أحرف صغيرة
    #يمر على كلمات الترتيب الموجودة في ORDERBY_KEYWORDS
    for direction, phrases in ORDERBY_KEYWORDS.items():
        for ph in phrases:
            if ph in s:#إذا وجد كلمة تدل على الترتيب
                return direction#رجع الاتجاه
    return "ASC"

#التحقق إذا كانت الجملة تحتوي أي كلمة من قائمة كلمات معينة
def sentence_has(sentence: str, keyword_list: list) -> bool:
    s = sentence.lower()
    return any(kw in s for kw in keyword_list)

#هاد التابع لح يبحث عن مسار الربط بين الجدولين
#لح تبلش بالجدول وبدك توصل لجدول
# relations هي قائمة العلاقات بين الجدوال
def find_join_path(from_t: str, to_t: str, relations: list) -> list:
    #queueسريع
    from collections import deque
    graph = {}#قاموس فارغ
    for ft, fc, tt, tc in relations:
        graph.setdefault(ft, []).append((fc, tt, tc))#إضافة العلاقة من الجدول الأول إلى الجدول الثاني داخل الـ Graph
        graph.setdefault(tt, []).append((tc, ft, fc))#إضافة العلاقة العكسية أيضًا حتى يمكن التنقل بين الجداول بالاتجاهين
#حفظ الجداول يلي زرناها 
    visited = {from_t}
    #إنشاء Queue ووضع جدول البداية فيها مع مسار فارغ
    queue   = deque([(from_t, [])])
    #طالما يوجد جداول لم يتم فحصها
    while queue:
        #أخذ أول جدول من الـ Queue مع المسار الذي أوصلنا إليه.
        cur, path = queue.popleft()
        if cur == to_t:#هل وصلنا إلى الجدول المطلوب
            return path#رجع مسار الربط كامل
        for fc, nb, tc in graph.get(cur, []):#المرور على جميع الجداول المرتبطة بالجدول الحالي
            if nb not in visited:#التأكد أننا لم نزره سابقًا
                visited.add(nb)#تسجيل الجدول كجدول تمت زيارته
                queue.append((nb, path + [(cur, fc, nb, tc)]))
    return []


 
#  النظام الخبير الرئيسي (Rules Engine)
 

class NLToSQLEngine(KnowledgeEngine):
 
#تحميل جميع الجداول يلي في قاعدة البيانات إلى المحرك
    @DefFacts()
    def load_tables(self):
        for name, syns in TABLE_SYNONYMS.items():
            yield TableFact(name=name, synonyms=syns)
#هي بتحمل الاعمدة
    @DefFacts()
    def load_columns(self):
        for (table, col), syns in COLUMN_SYNONYMS.items():
            if "id" in col.lower():# اذا كان موجود id باسم العامود
                dt = "INTEGER"#لح يكون نوع البيانات integer
            elif any(x in col.lower() for x in
                     ["price","total","bytes","milliseconds","quantity"]):
                dt = "NUMERIC"
            elif "date" in col.lower():
                dt = "DATE"
            else:
                dt = "TEXT"
            yield ColumnFact(table=table, column=col, data_type=dt, synonyms=syns)


    @DefFacts()
    #تعريف العلاقات بين الجداول للمحرك
    def load_relations(self):
        #فيها الجداول يلي مرتبطة ببعضها
        rels = [
            ("Album",        "ArtistId",    "Artist",    "ArtistId"),
            ("Track",        "AlbumId",     "Album",     "AlbumId"),
            ("Track",        "GenreId",     "Genre",     "GenreId"),
            ("Track",        "MediaTypeId", "MediaType", "MediaTypeId"),
            ("Invoice",      "CustomerId",  "Customer",  "CustomerId"),
            ("InvoiceLine",  "InvoiceId",   "Invoice",   "InvoiceId"),
            ("InvoiceLine",  "TrackId",     "Track",     "TrackId"),
            ("PlaylistTrack","PlaylistId",  "Playlist",  "PlaylistId"),
            ("PlaylistTrack","TrackId",     "Track",     "TrackId"),
            ("Customer",     "SupportRepId","Employee",  "EmployeeId"),
            ("Employee",     "ReportsTo",   "Employee",  "EmployeeId"),
        ]
        for ft, fc, tt, tc in rels:
            yield RelationFact(from_table=ft, from_col=fc,
                               to_table=tt, to_col=tc)
 
    #  اكتشاف نوع العملية من الكلمات

    @Rule(
        TokenFact(text=MATCH.word),
        NOT(OperationFact()),#إذا تم اكتشاف العملية بالفعل لا تكتشفها مرة أخرى
        TEST(lambda word: any(#العملية موجوةد شي بالقاموس
            normalize_arabic(word) in [normalize_arabic(k) for k in kws]
            for op, kws in OPERATION_KEYWORDS.items()#testبس بترجع اذا اي او لا
        ))
    )#لح نرجع ندور مرة تانية  العملية يلي بجملة موجودة بسطر  شو هي
    def detect_operation(self, word):
        for op, kws in OPERATION_KEYWORDS.items():
            if normalize_arabic(word) in [normalize_arabic(k) for k in kws]:
                self.declare(OperationFact(op_type=op))#أنشئ Fact جديدة
                break

    # اذا مافي عملية لح تكون العملية select
    @Rule(NOT(OperationFact()))
    def default_operation(self):
        self.declare(OperationFact(op_type="SELECT"))

 
    # ربط الكلمات بالجداول
    @Rule(
        TokenFact(text=MATCH.word),
        #جدول الكلمة
        TableFact(name=MATCH.tname, synonyms=MATCH.syns),
        #إذا كانت هي الكلمة مرتبطة بجدول من قبل لا تعالجها مرة ثانية
        NOT(MappedTableFact(original=MATCH.word)),
        TEST(lambda word, syns:# هل هي الكلمة موجودة بالمرادفات
             normalize_arabic(word) in [normalize_arabic(s) for s in syns])
    )#لح تشتغل هي الدالة بعد ماتنجح الشروط
    def map_to_table(self, word, tname, syns):
        #أنشئ حقيقة جديدة
        self.declare(MappedTableFact(original=word, table=tname))

    # ربط الكلمات بالأعمدة
#إذا وجدت كلمة في الجملة تشبه اسم عمود داخل جدول معين اربطها بهذا العمود
    @Rule(
        TokenFact(text=MATCH.word),
        #النظام يمر على كل الأعمدة الموجودة عنده
        ColumnFact(table=MATCH.tname, column=MATCH.col, synonyms=MATCH.syns),
        #لا تعالج نفس الكلمة لنفس الجدول مرتين
        NOT(MappedColumnFact(original=MATCH.word, table=MATCH.tname)),
        TEST(lambda word, syns:
             normalize_arabic(word) in [normalize_arabic(s) for s in syns])
    )
    def map_to_column(self, word, tname, col, syns):
        #انشا حقيقة جديدة واربطها بالعامود تبعها
        self.declare(MappedColumnFact(original=word, table=tname, column=col))

    
    #  إضافة الجداول المطلوبة تلقائياً إلى قائمة الجداول في from
    @Rule(
        MappedTableFact(table=MATCH.tname),
        NOT(FromTableFact(table=MATCH.tname))
    )
    def from_from_table(self, tname):
        self.declare(FromTableFact(table=tname))

  # هون  لح ضيف العامود الخاص بالجدول يلي عم دور عليه
    @Rule(
        MappedColumnFact(table=MATCH.tname),
        NOT(FromTableFact(table=MATCH.tname))
    )
    def from_column_table(self, tname):
        self.declare(FromTableFact(table=tname))

   
    # SELECT column للعمليات العادية
  
# مشان اذا كان المستخدم بدو عملية selectواختار عامود معين مشان ضيف هاد العامود لقائمة  اعمدة select

    @Rule(
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        OperationFact(op_type="SELECT"),
        NOT(SelectColumnFact(table=MATCH.tname, column=MATCH.col))
    )
    def select_column(self, tname, col):
        self.declare(SelectColumnFact(table=tname, column=col))

    #   للعمليات التجميعية
    @Rule(
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        OperationFact(op_type=MATCH.op),
        NOT(SelectColumnFact(table=MATCH.tname, column=MATCH.col)),
        #يتأكد انها عملية تجميعية
        TEST(lambda op: op in ("COUNT","AVG","SUM","MAX","MIN"))
    )
    def select_column_agg(self, tname, col, op):
        self.declare(SelectColumnFact(table=tname, column=col))

    # هي مشان SELECT * 
    @Rule(
        FromTableFact(table=MATCH.tname),
        OperationFact(op_type="SELECT"),
        NOT(SelectColumnFact(table=MATCH.tname))
    )
    def select_star(self, tname):
        self.declare(SelectColumnFact(table=tname, column="*"))
 
    # اكتشاف JOIN بين جدولين
 
    @Rule(
        FromTableFact(table=MATCH.t1),
        FromTableFact(table=MATCH.t2),
        RelationFact(from_table=MATCH.t1, from_col=MATCH.fc,
                     to_table=MATCH.t2, to_col=MATCH.tc),
        NOT(JoinFact(from_table=MATCH.t1, to_table=MATCH.t2)),
        TEST(lambda t1, t2: t1 != t2)
    )
    def join_direct(self, t1, fc, t2, tc):
        self.declare(JoinFact(from_table=t1, from_col=fc,
                              to_table=t2, to_col=tc))

    # اكتشاف JOIN إذا كانت العلاقة معكوسة
    @Rule(
        FromTableFact(table=MATCH.t1),
        FromTableFact(table=MATCH.t2),
        RelationFact(from_table=MATCH.t2, from_col=MATCH.fc,
                     to_table=MATCH.t1, to_col=MATCH.tc),
        NOT(JoinFact(from_table=MATCH.t2, to_table=MATCH.t1)),
        TEST(lambda t1, t2: t1 != t2)# تأكد انو الجدولين مختلفين
    )
    def join_reverse(self, t1, t2, fc, tc):
        self.declare(JoinFact(from_table=t2, from_col=fc,
                              to_table=t1, to_col=tc))


    #  GROUP BY تلقائي مع COUNT
    
    @Rule(
        OperationFact(op_type="COUNT"),
        FromTableFact(table=MATCH.tname),
        ColumnFact(table=MATCH.tname, column="Name"),
        NOT(GroupByFact(table=MATCH.tname))
    )
    def groupby_count(self, tname):
        self.declare(GroupByFact(table=tname, column="Name"))
 
    # مشان كل رقم موجود بالجملة يتحول إلى NumberFact داخل المحرك
    @Rule(
        TokenFact(text=MATCH.word),
        TEST(lambda word: re.fullmatch(r'\d+(?:\.\d+)?', word.strip()) is not None),
        NOT(NumberFact(value=MATCH.word))
    )
    def extract_number_fact(self, word):
        self.declare(NumberFact(value=float(word.strip())))

   
    # مشان لما المستخدم يطلب قيم فريدة / غير مكررة
    @Rule(
        TokenFact(text=MATCH.word),
        NOT(DistinctFact()),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in DISTINCT_KEYWORDS])
    )
    def detect_distinct(self, word):
        self.declare(DistinctFact(active=True))

 
    # هي مشان لما المستخدم يحط عامود مع رقم معناها هو شرط بwhere
    @Rule(
        SentenceFact(text=MATCH.sentence),#خود الجملة كاملة
        AS.nf << NumberFact(value=MATCH.val),#في رقم خزنو بnf وخزن قيمتو بvalue
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        ColumnFact(table=MATCH.tname, column=MATCH.col, data_type=MATCH.dtype),
        NOT(WhereFact(table=MATCH.tname, column=MATCH.col)),
        NOT(LimitFact(value=MATCH.val)),
        TEST(lambda dtype: dtype in ("NUMERIC", "INTEGER", "DATE")),# لازم يكون نوع العامود قابل للمقارنة
        salience=10
    )
    def where_numeric(self, val, tname, col, dtype, sentence, nf):
        op = detect_operator(sentence)# عم استخرج العملية
        self.declare(WhereFact(
            table=tname, column=col,
            operator=op or "=",
            value=val,
            kind="numeric"
        ))

 
    # مشان لما في رقم + جدول معروف لكن ما حدد عامود → يستخدم العامود الافتراضي
    @Rule(
        SentenceFact(text=MATCH.sentence),
        AS.nf << NumberFact(value=MATCH.val),
        FromTableFact(table=MATCH.tname),
        NOT(MappedColumnFact(table=MATCH.tname)),# هاد اهم شرط انو مافي عامود محدد مرتبط برقم
        NOT(WhereFact(table=MATCH.tname)),
        NOT(LimitFact(value=MATCH.val)),
          # هون مشان اتاكد اذا الجدول اصلا عندو عامود افتراضي
        TEST(lambda tname: tname in NUMERIC_WHERE_COLUMN),
        salience=0# اضعف اولوية
    )
    def where_numeric_default_column(self, val, tname, sentence, nf):
        col = NUMERIC_WHERE_COLUMN[tname]#النظام بجيب العمود الافتراضي
        op  = detect_operator(sentence)# عم يكتشف العملية
        self.declare(WhereFact(
            table=tname, column=col,
            operator=op or "=",
            value=val,
            kind="numeric"
        ))

 
 
    #  where_string
  # اعطني اغاني rock
  # لح تكون WHERE genre = 'ROCK'
    @Rule(
        TokenFact(text=MATCH.word),
        FromTableFact(table=MATCH.tname),
        TEST(lambda word: normalize_arabic(word) in
                  #القاموس القيم النصية المعروفة دول / مدن / أنواع موسيقى
             [normalize_arabic(k) for k in STRING_VALUES_MAP]),
                      # هاد القاموس يلي فيه العامود الافتراضي لكل  جدول 
        TEST(lambda tname: tname in STRING_WHERE_COLUMN),
        NOT(WhereFact(table=MATCH.tname, kind="string"))
    )
    def where_string(self, word, tname):
        col = STRING_WHERE_COLUMN[tname]
        val = STRING_VALUES_MAP.get(normalize_arabic(word),
              STRING_VALUES_MAP.get(word.lower(), word))
        self.declare(WhereFact(
            table=tname, column=col,
            operator="=",
            value=val,
            kind="string"
        ))

 
 #وظيفتها لما المستخدم يطلب WHERE column LIKE '%value%'
    @Rule(
        SentenceFact(text=MATCH.sentence),
        TokenFact(text=MATCH.word),
        FromTableFact(table=MATCH.tname),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in STRING_VALUES_MAP]),
        TEST(lambda tname: tname in STRING_WHERE_COLUMN),
        NOT(WhereFact(table=MATCH.tname, kind="like")),
        TEST(lambda sentence: detect_operator(sentence) == "LIKE")
    )
    def where_like(self, word, tname, sentence):
        col = STRING_WHERE_COLUMN[tname]
        val = STRING_VALUES_MAP.get(normalize_arabic(word),
              STRING_VALUES_MAP.get(word.lower(), word))
        self.declare(WhereFact(
            table=tname, column=col,
            operator="LIKE",
            value=f"%{val}%",
            kind="like"
        ))
 
 #اكتشاف الترتيب لما المستخدم يذكر عامود معينا مثلا  رتب العملاء حسب العمر تنازليا
    @Rule(
        SentenceFact(text=MATCH.sentence),
        TokenFact(text=MATCH.word),
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        NOT(OrderByFact(table=MATCH.tname)),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in ORDER_TRIGGER])
    )
    def orderby_from_trigger(self, word, tname, col, sentence):
        direction = detect_order_direction(sentence)#هي دالة لح تحدد الاتجاه
        self.declare(OrderByFact(table=tname, column=col, direction=direction))
 
    # هون لما المستخدم يكون بدو ترتيب بس ماحدد العامود مثلا رتب العملاء تنازليا
    #فالنظام هو يلي لح يختار العامود
    @Rule(
        SentenceFact(text=MATCH.sentence),
        TokenFact(text=MATCH.word),
        FromTableFact(table=MATCH.tname),
        NOT(OrderByFact(table=MATCH.tname)),
        NOT(MappedColumnFact(table=MATCH.tname)),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in ORDER_TRIGGER]),
        TEST(lambda tname: tname in NUMERIC_WHERE_COLUMN)
    )
    def orderby_default_column(self, word, tname, sentence):
        col       = NUMERIC_WHERE_COLUMN[tname]
        direction = detect_order_direction(sentence)
        self.declare(OrderByFact(table=tname, column=col, direction=direction))

    
 #استخراج LIMIT
    @Rule(
        TokenFact(text=MATCH.word),
        AS.nf << NumberFact(value=MATCH.val),
        NOT(LimitFact()),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in LIMIT_TRIGGER]),
        salience=100# هون حددت الاولوية عالية كتبر مشان ماتلقطها قواعد الwhere
    )
    def limit_from_trigger(self, word, val, nf):
        self.declare(LimitFact(value=int(val)))

 
   #هي انشاء havingبعد العمليات التجميعية
    @Rule(
        SentenceFact(text=MATCH.sentence),
        TokenFact(text=MATCH.word),
        OperationFact(op_type=MATCH.op),
        AS.nf << NumberFact(value=MATCH.val),
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        NOT(HavingFact(table=MATCH.tname)),
        TEST(lambda op: op in ("COUNT", "SUM", "AVG", "MAX", "MIN")),# havingلازم يكون لتجميع
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in HAVING_TRIGGER])
    )
    def having_from_trigger(self, word, op, val, tname, col, sentence, nf):
        oper = detect_operator(sentence)
        self.declare(HavingFact(
            table=tname, column=col,
            operator=oper or ">",
            value=val
        ))

 # هي مشان انشاء group
    @Rule(
        TokenFact(text=MATCH.word),
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        NOT(GroupByFact(table=MATCH.tname, column=MATCH.col)),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in GROUPBY_TRIGGER])
    )
    def groupby_from_trigger(self, word, tname, col):
        self.declare(GroupByFact(table=tname, column=col))
 
 #اكتشاف AND
    @Rule(
        SentenceFact(text=MATCH.sentence),
        NOT(LogicalOperatorFact()),
        TEST(lambda sentence: any(
            kw in sentence.lower()
            for kw in [" و ", " and ", "كذلك", "أيضا", "ايضا",
                       "بالإضافة", "بالاضافة", "plus", "also"]
        ))
    )
    def detect_logical_and(self, sentence):
        self.declare(LogicalOperatorFact(operator="AND"))
 
 #اكتشاف or
    @Rule(
        SentenceFact(text=MATCH.sentence),
        NOT(LogicalOperatorFact()),
        TEST(lambda sentence: any(
            kw in sentence.lower()
            for kw in ["أو", " او ", " or ", "either", "alternatively"]
        ))
    )
    def detect_logical_or(self, sentence):
        self.declare(LogicalOperatorFact(operator="OR"))
 
 # هي مشان لما المستخدم مايحط كلمة و مثلا اعرض العملاء من كندا اعمارهم اكبر من 20
    @Rule(
        WhereFact(table=MATCH.t1, column=MATCH.c1),
        WhereFact(table=MATCH.t2, column=MATCH.c2),
        NOT(LogicalOperatorFact()),
        TEST(lambda t1, c1, t2, c2: (t1, c1) != (t2, c2))# اذا اكتشف وجود شرطين مختلفين
    )
    def default_logical_and(self, t1, c1, t2, c2):
        self.declare(LogicalOperatorFact(operator="AND"))

 #إنشاء Subquery تلقائياً
    @Rule(
        SentenceFact(text=MATCH.sentence),
        TokenFact(text=MATCH.word),
        FromTableFact(table=MATCH.tname),
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),#اكتشاف العامود المناسب
        ColumnFact(table=MATCH.tname, column=MATCH.col, data_type=MATCH.dtype),#يجلب نوع العامود
        NOT(SubqueryFact(table=MATCH.tname)),#تأكد أنه لا يوجد Subquery لهذا الجدول مسبقاً
        NOT(WhereFact(table=MATCH.tname, kind="subquery")),
        TEST(lambda dtype: dtype in ("NUMERIC", "INTEGER")),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in
              ["المتوسط", "متوسط", "average", "avg", "معدل",
               "المجموع", "مجموع", "sum", "إجمالي", "اجمالي",
               "الأعلى", "اعلى", "أعلى", "max", "maximum",
               "الأقل", "اقل", "أقل", "min", "minimum"]])
    )
    def detect_subquery(self, word, tname, col, dtype, sentence):
        # تحديد نوع العملية من الكلمة المكتشفة
        nw = normalize_arabic(word)
        subq_op = (
            "AVG" if nw in [normalize_arabic(k) for k in
                             ["المتوسط","متوسط","average","avg","معدل"]]
            else "SUM" if nw in [normalize_arabic(k) for k in
                                  ["المجموع","مجموع","sum","إجمالي","اجمالي"]]
            else "MAX" if nw in [normalize_arabic(k) for k in
                                  ["الأعلى","اعلى","أعلى","max","maximum"]]
            else "MIN"
        )
        # المشكلة 3: نُنشئ SubqueryFact ونحفظه لنمرره كـ value لـ WhereFact
        subq = SubqueryFact(table=tname, column=col, operation=subq_op)
        self.declare(subq)
        op = detect_operator(sentence)# استخراج عملية المقارنة
        self.declare(WhereFact(
            table=tname, column=col,
            operator=op or ">",
            value=subq_op,   
            kind="subquery"
        ))

   #هي مشان ايجاد الطريق مشان المسار المعقد
    @Rule(
        FromTableFact(table=MATCH.t1),
        FromTableFact(table=MATCH.t2),
        NOT(JoinFact(from_table=MATCH.t1, to_table=MATCH.t2)),
        NOT(JoinFact(from_table=MATCH.t2, to_table=MATCH.t1)),
        NOT(RelationFact(from_table=MATCH.t1, to_table=MATCH.t2)),
        NOT(RelationFact(from_table=MATCH.t2, to_table=MATCH.t1)),
        TEST(lambda t1, t2: t1 != t2)# عم يتحقق انو الجدولين مو متل بعض
    )
    def resolve_complex_joins(self, t1, t2):
        # قائمة العلاقات الثابتة — نفس القائمة في load_relations
        rels = [
            ("Album",        "ArtistId",    "Artist",    "ArtistId"),
            ("Track",        "AlbumId",     "Album",     "AlbumId"),
            ("Track",        "GenreId",     "Genre",     "GenreId"),
            ("Track",        "MediaTypeId", "MediaType", "MediaTypeId"),
            ("Invoice",      "CustomerId",  "Customer",  "CustomerId"),
            ("InvoiceLine",  "InvoiceId",   "Invoice",   "InvoiceId"),
            ("InvoiceLine",  "TrackId",     "Track",     "TrackId"),
            ("PlaylistTrack","PlaylistId",  "Playlist",  "PlaylistId"),
            ("PlaylistTrack","TrackId",     "Track",     "TrackId"),
            ("Customer",     "SupportRepId","Employee",  "EmployeeId"),
            ("Employee",     "ReportsTo",   "Employee",  "EmployeeId"),
        ]
        path = find_join_path(t1, t2, rels)

        for (ft, fc, tt, tc) in path:
            self.declare(FromTableFact(table=ft))
            self.declare(FromTableFact(table=tt))
            self.declare(JoinFact(from_table=ft, from_col=fc,
                                  to_table=tt, to_col=tc))
 
    @Rule(
        SentenceFact(text=MATCH.sentence),
        FromTableFact(table=MATCH.tname),
        MappedColumnFact(table=MATCH.tname, column=MATCH.col),
        ColumnFact(
            table=MATCH.tname,
            column=MATCH.col,
            data_type=MATCH.dtype
        ),
        NOT(
            BetweenFact(
                table=MATCH.tname,
                column=MATCH.col
            )
        ),
        TEST(lambda dtype: dtype in ("INTEGER", "NUMERIC")),#هي مشان القاعدة ماتشتغل غير الارقام
        salience=20
    )
    def detect_between(self, sentence, tname, col, dtype):

        nums = re.findall(r'\d+(?:\.\d+)?', sentence)# هي مشان يبحث عن الارقام بالجملة
        if len(nums) >= 2:# هي مشان يتأكد يكون في رقمين قارن بيناتهم

            min_val = float(nums[0])
            max_val = float(nums[1])

            if (
                "بين" in sentence
                or "من" in sentence and "إلى" in sentence
            ):

                self.declare(
                    BetweenFact(
                        table=tname,
                        column=col,
                        min_value=min_val,
                        max_value=max_val
                    )
                )

 
    @Rule(
        SentenceFact(text=MATCH.sentence),
        FromTableFact(table=MATCH.tname),
        TokenFact(text=MATCH.word),
        NOT(NegationFact(table=MATCH.tname)),
        TEST(lambda tname: tname in STRING_WHERE_COLUMN),
        TEST(lambda sentence: any(
            normalize_arabic(neg) in normalize_arabic(sentence)
            for neg in ["لا يحتوي","ليس","غير","لا يساوي","لايساوي",
                        "not","doesn't","does not","!=","لا يعمل",
                        "لا ينتمي","لا يسكن","لا يقع"]
        )),
        TEST(lambda word: normalize_arabic(word) in
             [normalize_arabic(k) for k in STRING_VALUES_MAP]),
        salience=30   
    )
    def detect_negation(self, sentence, tname, word):
        col = STRING_WHERE_COLUMN[tname]
        val = STRING_VALUES_MAP.get(normalize_arabic(word),
              STRING_VALUES_MAP.get(word.lower(), word))
     
        op = (
            "NOT LIKE"
            if any(normalize_arabic(neg) in normalize_arabic(sentence)
                   for neg in ["لا يحتوي","not like","لا يشمل"])
            else "!="
        )
        val_out = f"%{val}%" if op == "NOT LIKE" else val
        self.declare(NegationFact(
            table=tname,
            column=col,
            operator=op,
            value=val_out
        ))

 # هي مشان لما يكون الجدول مرتبط بنفسو
    @Rule(
        FromTableFact(table=MATCH.tname),
        RelationFact(from_table=MATCH.tname, from_col=MATCH.fc,
                     to_table=MATCH.tname, to_col=MATCH.tc),
        NOT(SelfJoinFact(table=MATCH.tname)),
        TEST(lambda tname, fc, tc: fc != tc)#هي مشان يكون العامودين يلي عم اربطهم مع بعض مختلفين
    )
    def detect_self_join(self, tname, fc, tc):
        alias1 = f"{tname}1"# هون لح احتاج اسمين مستعارين
        alias2 = f"{tname}2"
        self.declare(SelfJoinFact(
            table=tname,
            from_col=fc,
            to_col=tc,
            alias1=alias1,
            alias2=alias2
        ))























#SQL Generator
#هدول قواعد المولد
    @Rule(NOT(Phase()), salience=-100)
    def rule_init_generator(self):
        self.declare(SQLBuffer(text=""))
        self.declare(Phase(step="START"))

    @Rule(AS.p << Phase(step="START"), AS.b << SQLBuffer(text=""), salience=-100)
    def rule_start_to_select(self, p, b):
        self.modify(b, text="") 
        self.modify(p, step="SELECT_COLUMNS")


    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column=MATCH.c),
        TEST(lambda c: c != "*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column=MATCH.c)),
        OR(
            NOT(OperationFact()),
            OperationFact(op_type="SELECT")
        ),
        AS.b << SQLBuffer(text=""),
        salience=-90 
    )
    def rule_add_first_select_column_plain_fixed(self, b, t, c):
        self.declare(ProcessedFact(fact_type="select", table=t, column=c))
        self.modify(b, text=f"SELECT {t}.{c}")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column="*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column="*")),
        OR(
            NOT(OperationFact()),
            OperationFact(op_type="SELECT")
        ),
        AS.b << SQLBuffer(text=""), 
        salience=-90
    )
    def rule_add_first_select_star_plain_fixed(self, b, t):
        self.declare(ProcessedFact(fact_type="select", table=t, column="*"))
        self.modify(b, text="SELECT *")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column=MATCH.c),
        TEST(lambda c: c != "*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column=MATCH.c)),
        OperationFact(op_type=MATCH.op),
        TEST(lambda op: op.upper() != "SELECT"),
        AS.b << SQLBuffer(text=""), 
        salience=-100
    )
    def rule_add_first_select_column_with_op(self, b, t, c, op):
        self.declare(ProcessedFact(fact_type="select", table=t, column=c))
        self.modify(b, text=f"SELECT {op}({t}.{c})")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column="*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column="*")),
        OperationFact(op_type=MATCH.op),
        TEST(lambda op: op.upper() != "SELECT"),
        AS.b << SQLBuffer(text=""),
        salience=-100
    )
    def rule_add_first_select_star_with_op(self, b, t, op):
        self.declare(ProcessedFact(fact_type="select", table=t, column="*"))
        self.modify(b, text=f"SELECT {op}(*)")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column=MATCH.c),
        TEST(lambda c: c != "*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column=MATCH.c)),
        OperationFact(op_type=MATCH.op),
        TEST(lambda op: op.upper() != "SELECT"),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt != ""),
        salience=-100
    )
    def rule_add_next_select_column_with_op(self, b, t, c, txt, op):
        self.declare(ProcessedFact(fact_type="select", table=t, column=c))
        self.modify(b, text=f"{txt}, {op}({t}.{c})")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column="*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column="*")),
        OperationFact(op_type=MATCH.op),
        TEST(lambda op: op.upper() != "SELECT"),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt != ""),
        salience=-100
    )
    def rule_add_next_select_star_with_op(self, b, t, txt, op):
        self.declare(ProcessedFact(fact_type="select", table=t, column="*"))
        self.modify(b, text=f"{txt}, {op}(*)")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column=MATCH.c),
        TEST(lambda c: c != "*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column=MATCH.c)),
        OR(
            NOT(OperationFact()),
            OperationFact(op_type="SELECT")
        ),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt != ""),
        salience=-90 
    )
    def rule_add_next_select_column_plain_fixed(self, b, t, c, txt):
        self.declare(ProcessedFact(fact_type="select", table=t, column=c))
        self.modify(b, text=f"{txt}, {t}.{c}")

    @Rule(
        Phase(step="SELECT_COLUMNS"),
        SelectColumnFact(table=MATCH.t, column="*"),
        NOT(ProcessedFact(fact_type="select", table=MATCH.t, column="*")),
        OR(
            NOT(OperationFact()),
            OperationFact(op_type="SELECT")
        ),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt != ""),
        salience=-90
    )
    def rule_add_next_select_star_plain_fixed(self, b, t, txt):
        self.declare(ProcessedFact(fact_type="select", table=t, column="*"))
        self.modify(b, text=f"{txt}, *")

    @Rule(AS.p << Phase(step="SELECT_COLUMNS"), AS.b << SQLBuffer(text=MATCH.txt), salience=-110)
    def rule_transition_to_from(self, p, b, txt):
        self.modify(b, text=f"{txt} FROM ")
        self.modify(p, step="FROM_TABLES")


    @Rule(
        Phase(step="FROM_TABLES"),
        FromTableFact(table=MATCH.t),
        NOT(JoinFact()),
        NOT(ProcessedFact(fact_type="from", table=MATCH.t)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" FROM ")),
        salience=-100
    )
    def rule_add_first_pure_table(self, b, t, txt):
        self.declare(ProcessedFact(fact_type="from", table=t))
        self.modify(b, text=f"{txt}{t}")

    @Rule(
        Phase(step="FROM_TABLES"),
        FromTableFact(table=MATCH.t),
        NOT(JoinFact()),
        NOT(ProcessedFact(fact_type="from", table=MATCH.t)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" FROM ")),
        salience=-100
    )
    def rule_add_next_pure_table(self, b, t, txt):
        self.declare(ProcessedFact(fact_type="from", table=t))
        self.modify(b, text=f"{txt}, {t}")

    @Rule(
        Phase(step="FROM_TABLES"),
        JoinFact(from_table=MATCH.t1, from_col=MATCH.c1, to_table=MATCH.t2, to_col=MATCH.c2),
        NOT(JoinedTable(table=MATCH.t1)),
        NOT(JoinedTable(table=MATCH.t2)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" FROM ")),
        salience=-90
    )
    def rule_add_first_join(self, b, t1, c1, t2, c2, txt):
        self.declare(JoinedTable(table=t1))
        self.declare(JoinedTable(table=t2))
        self.modify(b, text=f"{txt}{t1} JOIN {t2} ON {t1}.{c1} = {t2}.{c2}")

 
    @Rule(
        Phase(step="FROM_TABLES"),
        JoinFact(from_table=MATCH.t1, from_col=MATCH.c1, to_table=MATCH.t2, to_col=MATCH.c2),
        JoinedTable(table=MATCH.t1),
        NOT(JoinedTable(table=MATCH.t2)),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-95
    )
    def rule_add_next_join_table(self, b, t1, c1, t2, c2, txt):
        self.declare(JoinedTable(table=t2))
        self.modify(b, text=f"{txt} JOIN {t2} ON {t1}.{c1} = {t2}.{c2}")

    @Rule(
    Phase(step="FROM_TABLES"),
    SelfJoinFact(table=MATCH.t, from_col=MATCH.fc, to_col=MATCH.tc, alias1=MATCH.a1, alias2=MATCH.a2),
    NOT(ProcessedFact(fact_type="self_join_finalized", table=MATCH.t)),
    AS.b << SQLBuffer(text=MATCH.txt),
    TEST(lambda txt: " FROM " in txt),
    salience=200
)
    def rule_self_join_with_from(self, b, t, fc, tc, a1, a2, txt):
     self.declare(ProcessedFact(fact_type="self_join_finalized", table=t))
     self.declare(ProcessedFact(fact_type="from", table=t)) 

     fixed_txt = txt.replace("Employee1.FirstName2.FirstName", "Employee1.FirstName, Employee2.FirstName")
     fixed_txt = fixed_txt.replace("Employee1.FirstNameEmployee2.FirstName", "Employee1.FirstName, Employee2.FirstName")
    
     clean_join = f" FROM {t} AS {a1} JOIN {t} AS {a2} ON {a1}.{fc} = {a2}.{tc}"
     txt_replaced = fixed_txt.split(" FROM ")[0] + clean_join
    
     self.modify(b, text=txt_replaced)


    @Rule(
        Phase(step="FROM_TABLES"),
        SelfJoinFact(table=MATCH.t, from_col=MATCH.fc, to_col=MATCH.tc, alias1=MATCH.a1, alias2=MATCH.a2),
        NOT(ProcessedFact(fact_type="self_join", table=MATCH.t)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: " FROM " not in txt),
        salience=150
    )
    def rule_self_join_without_from(self, b, t, fc, tc, a1, a2, txt):
        self.declare(ProcessedFact(fact_type="self_join", table=t))
        self.declare(ProcessedFact(fact_type="from", table=t))
        self.declare(ProcessedFact(fact_type="from_table", table=t))
        fixed_txt = txt.replace("Employee1.FirstName2.FirstName", "Employee1.FirstName, Employee2.FirstName")
        fixed_txt = fixed_txt.replace("Employee1.FirstNameEmployee2.FirstName", "Employee1.FirstName, Employee2.FirstName")
        
        clean_join = f" FROM {t} AS {a1} JOIN {t} AS {a2} ON {a1}.{fc} = {a2}.{tc}"
        txt_replaced = f"{fixed_txt}{clean_join}"
        txt_replaced = txt_replaced.replace(f", {t}", "").replace(f",{t}", "")
        
        self.modify(b, text=txt_replaced)

    @Rule(
        AS.p << Phase(step="WHERE_START"),
        WhereFact(),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=10
    )
    def rule_write_where_keyword(self, p, b, txt):
        self.modify(b, text=f"{txt} WHERE ")
        self.modify(p, step="WHERE_BODY")
    @Rule(
        AS.p << Phase(step="WHERE_START"),
        NOT(WhereFact()),
        OR(BetweenFact(), NegationFact()),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=10
    )
    def rule_write_where_keyword_new_facts(self, p, b, txt):
        self.modify(b, text=f"{txt} WHERE ")
        self.modify(p, step="WHERE_BODY")

    @Rule(AS.p << Phase(step="WHERE_START"), salience=-105)
    def rule_skip_where(self, p):
        self.modify(p, step="GROUP_BY")

    @Rule(
        AS.p << Phase(step="WHERE_BODY"), 
        salience=-1000
    )
    def rule_transition_from_where_to_groupby(self, p):
        self.modify(p, step="GROUP_BY")
    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="string"),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_first_where_string(self, b, t, c, op, val, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt}{t}.{c} {op} '{val}'")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="like"),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_first_where_like(self, b, t, c, op, val, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt}{t}.{c} {op} '{val}'")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="numeric"),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_first_where_numeric(self, b, t, c, op, val, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt}{t}.{c} {op} {val}")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator="LIKE", value=MATCH.val, kind="string"),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" WHERE ")),
        salience=-95
    )
    def rule_first_where_like(self, b, t, c, val, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt}{t}.{c} LIKE '{val}'")
    
    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator="BETWEEN", value=MATCH.val, kind="numeric"),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: txt.endswith(" WHERE ")),
        salience=-80
    )
    def rule_first_where_between(self, b, t, c, val, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt}{t}.{c} BETWEEN {val[0]} AND {val[1]}")
    @Rule(
    Phase(step="WHERE_BODY"),
    BetweenFact(table=MATCH.t, column=MATCH.c, min_value=MATCH.mn, max_value=MATCH.mx),
    NOT(ProcessedFact(fact_type="between", table=MATCH.t, column=MATCH.c)),
    AS.b << SQLBuffer(text=MATCH.txt),
    TEST(lambda txt: txt.endswith(" WHERE ")),
    salience=-80
)
    def rule_between_first(self, b, t, c, mn, mx, txt):
     self.declare(ProcessedFact(fact_type="between", table=t, column=c))
     self.modify(b, text=f"{txt}{t}.{c} BETWEEN {mn} AND {mx}")
    @Rule(
    Phase(step="WHERE_BODY"),
    NegationFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val),
    NOT(ProcessedFact(fact_type="negation", table=MATCH.t, column=MATCH.c)),
    AS.b << SQLBuffer(text=MATCH.txt),
    TEST(lambda txt: txt.endswith(" WHERE ")),
    salience=-81
)
    def rule_negation_first(self, b, t, c, op, val, txt):
     self.declare(ProcessedFact(fact_type="negation", table=t, column=c))
     self.modify(b, text=f"{txt}{t}.{c} {op} '{val}'")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="string"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_next_where_string(self, b, t, c, op, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} {op} '{val}'")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="numeric"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_next_where_numeric(self, b, t, c, op, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} {op} {val}")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="string"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_next_where_string(self, b, t, c, op, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} {op} '{val}'")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="like"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_next_where_like(self, b, t, c, op, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} {op} '{val}'")

 
    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val, kind="numeric"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_add_next_where_numeric(self, b, t, c, op, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} {op} {val}")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator="LIKE", value=MATCH.val, kind="string"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_next_where_like(self, b, t, c, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} LIKE '{val}'")
    
    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator="BETWEEN", value=MATCH.val, kind="numeric"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_next_where_between(self, b, t, c, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        self.modify(b, text=f"{txt} {log_op} {t}.{c} BETWEEN {val[0]} AND {val[1]}")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator="IN", value=MATCH.val, kind="numeric"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_next_where_in_numeric(self, b, t, c, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        formatted_values = ", ".join(val) 
        self.modify(b, text=f"{txt} {log_op} {t}.{c} IN ({formatted_values})")

    @Rule(
        Phase(step="WHERE_BODY"),
        WhereFact(table=MATCH.t, column=MATCH.c, operator="IN", value=MATCH.val, kind="string"),
        LogicalOperatorFact(operator=MATCH.log_op),
        NOT(ProcessedFact(fact_type="where", table=MATCH.t, column=MATCH.c, value=MATCH.val)),
        AS.b << SQLBuffer(text=MATCH.txt),
        TEST(lambda txt: not txt.endswith(" WHERE ")),
        salience=-100
    )
    def rule_next_where_in_string(self, b, t, c, val, log_op, txt):
        self.declare(ProcessedFact(fact_type="where", table=t, column=c, value=val))
        formatted_values = "'" + "', '".join(val) + "'"
        self.modify(b, text=f"{txt} {log_op} {t}.{c} IN ({formatted_values})")
    @Rule(
    Phase(step="WHERE_BODY"),
    BetweenFact(table=MATCH.t, column=MATCH.c, min_value=MATCH.mn, max_value=MATCH.mx),
    NOT(ProcessedFact(fact_type="between", table=MATCH.t, column=MATCH.c)),
    AS.b << SQLBuffer(text=MATCH.txt),
    TEST(lambda txt: not txt.endswith(" WHERE ")),
    salience=-80
)
    def rule_between_next(self, b, t, c, mn, mx, txt):
     self.declare(ProcessedFact(fact_type="between", table=t, column=c))
     self.modify(b, text=f"{txt} AND {t}.{c} BETWEEN {mn} AND {mx}")

    @Rule(
    Phase(step="WHERE_BODY"),
    NegationFact(table=MATCH.t, column=MATCH.c, operator=MATCH.op, value=MATCH.val),
    NOT(ProcessedFact(fact_type="negation", table=MATCH.t, column=MATCH.c)),
    AS.b << SQLBuffer(text=MATCH.txt),
    TEST(lambda txt: not txt.endswith(" WHERE ")),
    salience=-81
)
    def rule_negation_next(self, b, t, c, op, val, txt):
     self.declare(ProcessedFact(fact_type="negation", table=t, column=c))
     self.modify(b, text=f"{txt} AND {t}.{c} {op} '{val}'")
    
    @Rule(
        AS.p << Phase(step="GROUP_BY"),
        GroupByFact(table=MATCH.t, column=MATCH.c),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-100
    )
    def rule_add_groupby(self, p, b, t, c, txt):
        self.modify(b, text=f"{txt} GROUP BY {t}.{c}")
        self.modify(p, step="HAVING")

    @Rule(AS.p << Phase(step="GROUP_BY"), salience=-105)
    def rule_skip_groupby(self, p):
        self.modify(p, step="HAVING")

    @Rule(
        Phase(step="HAVING"),
        HavingFact(table=MATCH.t, column="*", op_type=MATCH.op, operator=MATCH.cond_op, value=MATCH.val),
        NOT(ProcessedFact(fact_type="having")),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-100
    )
    def rule_add_having_star(self, b, t, op, cond_op, val, txt):
        self.declare(ProcessedFact(fact_type="having"))
        self.modify(b, text=f"{txt} HAVING {op}(*) {cond_op} {val}")

    @Rule(
        Phase(step="HAVING"),
        HavingFact(table=MATCH.t, column=MATCH.c, op_type=MATCH.op, operator=MATCH.cond_op, value=MATCH.val),
        TEST(lambda c: c != "*"),
        NOT(ProcessedFact(fact_type="having")),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-100
    )
    def rule_add_having_column(self, b, t, c, op, cond_op, val, txt):
        self.declare(ProcessedFact(fact_type="having"))
        self.modify(b, text=f"{txt} HAVING {op}({t}.{c}) {cond_op} {val}")
    @Rule(AS.p << Phase(step="HAVING"), salience=-110)
    def rule_transition_to_orderby(self, p):
        self.modify(p, step="ORDER_BY")
    @Rule(
        AS.p << Phase(step="ORDER_BY"),
        OrderByFact(table=MATCH.t, column=MATCH.c, direction=MATCH.d),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-100
    )
    def rule_add_orderby(self, p, b, t, c, d, txt):
        self.modify(b, text=f"{txt} ORDER BY {t}.{c} {d}")
        self.modify(p, step="LIMIT")

    @Rule(AS.p << Phase(step="ORDER_BY"), salience=-105)
    def rule_skip_orderby(self, p):
        self.modify(p, step="LIMIT")

    @Rule(
        AS.p << Phase(step="LIMIT"),
        LimitFact(value=MATCH.val),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-100
    )
    def rule_add_limit(self, p, b, val, txt):
        self.modify(b, text=f"{txt} LIMIT {val}")
        self.modify(p, step="COMPLETED")

    @Rule(AS.p << Phase(step="LIMIT"), salience=-105)
    def rule_skip_limit(self, p):
        self.modify(p, step="COMPLETED")

    @Rule(
        AS.p << Phase(step="COMPLETED"),
        AS.b << SQLBuffer(text=MATCH.txt),
        salience=-100
    )
    def rule_finalize_query(self, p, b, txt):
        final_sql = txt.strip() + ";"
        self.modify(b, text=final_sql)
        self.modify(p, step="DONE")
        print("\n" + "-"*50)
        print(" [EXPERT SYSTEM OUTPUT]")
        print(" " + final_sql)
        print("-"*50)

#هاد تيست بسيط
# engine = NLToSQLEngine()
# engine.reset()
 
# engine.declare(SentenceFact(text="اعرض الفنانين"))
# engine.declare(TokenFact(index=0, text="اعرض"))
# engine.declare(TokenFact(index=1, text="فنان"))
# engine.declare(WhereFact(table="Artist", column="ArtistId", operator=">", value=5, kind="numeric"))
# engine.declare(LogicalOperatorFact(operator="AND"))
# engine.declare(WhereFact(table="Artist", column="Status", operator="=", value="Active", kind="string"))
# engine.run()

#تيست مع تعقيد اكبر
# engine = NLToSQLEngine()
# engine.reset()
# engine.declare(SentenceFact(text="استعلام مركب"))

# engine.declare(SelectColumnFact(table="Artist", column="Name"))
# engine.declare(SelectColumnFact(table="Album", column="Title"))

# engine.declare(JoinFact(from_table="Artist", from_col="ArtistId", to_table="Album", to_col="ArtistId"))

# engine.declare(WhereFact(table="Artist", column="ArtistId", operator=">", value="5", kind="numeric"))

# engine.declare(LimitFact(value=10))

# engine.run()

engine = NLToSQLEngine()
engine.reset()

engine.declare(SentenceFact(text="استعلام تجميعي"))

engine.declare(SelectColumnFact(table="Album", column="*"))
engine.declare(OperationFact(op_type="COUNT")) 

engine.declare(FromTableFact(table="Album"))
engine.declare(WhereFact(table="Album", column="Genre", operator="=", value="Classic", kind="string"))

engine.declare(GroupByFact(table="Album", column="ArtistId"))

engine.run()

for fid, fact in engine.facts.items():
    print(f"Fact #{fid}: {type(fact).__name__} -> {fact}")

    if type(fact).__name__ == "SQLBuffer":
        print(f"{fact['text']}\n")