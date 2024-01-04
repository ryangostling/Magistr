# External
from peewee import PrimaryKeyField, CharField, ForeignKeyField, IntegerField, TextField, DateField

# Internal
from database.biblio.context import BaseModel


# Таблиця організацій
class Affiliation(BaseModel):
    affiliation_id = IntegerField(primary_key=True)

    affiliation_name = CharField(null=True)
    city = CharField(null=True)
    country = CharField(null=True)
    address = CharField(null=True)
    url = CharField(null=True)
    scopus_id = CharField(null=True)

    class Meta:
        db_table = "Affiliations"

# Таблиця авторів
class Author(BaseModel):
    author_id = IntegerField(primary_key=True)

    surname = CharField(null=True)
    name = CharField(null=True)
    h_index = IntegerField(default=0)
    cited_by_count = IntegerField(default=0)
    coauthors_count = IntegerField(default=0)
    scopus_id = CharField(null=True)
    orcid = CharField(null=True)

    class Meta:
        db_table = "Authors"


# Таблиця публікацій
class Publication(BaseModel):
    publication_id = IntegerField(primary_key=True)

    title = TextField(null=True)
    abstract = TextField(null=True)
    url = TextField(null=True)
    cited_by_count = IntegerField(default=0)
    pub_date = DateField(null=True)
    scopus_id = CharField(null=True)
    scholar_id = CharField(null=True)
    core_id = CharField(null=True)
    keywords = TextField(null=True)
    alternative_titles = TextField(null=True)

    class Meta:
        db_table = "Publications"

# Таблиця тем
class Subject(BaseModel):
    subject_id = PrimaryKeyField()

    full_title = CharField(null=True)
    abbreviation = CharField(null=True)
    group = CharField(null=True)
    code = IntegerField(null=True)

    class Meta:
        db_table = "Subjects"

# Таблиця зв'язку авторів з публікаціями
class AuthorPublication(BaseModel):
    author_publication_id = IntegerField(primary_key=True)
    author = ForeignKeyField(Author, backref="AuthorsPublications")
    publication = ForeignKeyField(Publication, backref="AuthorsPublications")

    class Meta:
        db_table = "AuthorsPublications"

# Таблиця зв'язку організацій з публікаціями
class AffiliationPublication(BaseModel):
    affiliation_publication_id = IntegerField(primary_key=True)
    affiliation = ForeignKeyField(Affiliation, backref="AffiliationsPublications")
    publication = ForeignKeyField(Publication, backref="AffiliationsPublications")

    class Meta:
        db_table = "AffiliationsPublications"

# Таблиця зв'язку організацій з авторами
class AffiliationAuthor(BaseModel):
    affiliation_author_id = IntegerField(primary_key=True)
    affiliation = ForeignKeyField(Affiliation, backref="AffiliationsAuthors")
    author = ForeignKeyField(Author, backref="AffiliationsAuthors")

    class Meta:
        db_table = "AffiliationsAuthors"

# Таблиця зв'язку авторів з темами
class AuthorSubject(BaseModel):
    author_subject_id = IntegerField(primary_key=True)
    author = ForeignKeyField(Author, backref="AuthorsSubjects")
    subject = ForeignKeyField(Subject, backref="AuthorsSubjects")

    class Meta:
        db_table = "AuthorsSubjects"

# Таблиця зв'язку публікацій з темами
class PublicationSubject(BaseModel):
    publication_subject_id = IntegerField(primary_key=True)
    publication = ForeignKeyField(Publication, backref="PublicationsSubjects")
    subject = ForeignKeyField(Subject, backref="PublicationsSubjects")

    class Meta:
        db_table = "PublicationsSubjects"
