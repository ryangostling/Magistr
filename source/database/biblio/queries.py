# Internal
from database.biblio.models import AffiliationPublication, Affiliation, AffiliationAuthor, Subject, AuthorSubject, \
    AuthorPublication, PublicationSubject, Author
from database.biblio.selects import affiliations, authors_publications, affiliations_authors, affiliations_publications, \
    authors, publications


def get_authors_by_pub_id(pub_id):
    author_list = ", ".join([auth.name for auth in
                             authors().join(AuthorPublication).where(AuthorPublication.publication == pub_id)
                             .order_by(Author.name)])
    return author_list

def get_affiliations_by_pub_id(pub_id):
    aff_list = ", ".join([aff.affiliation_name for aff in
                          affiliations().join(AffiliationPublication).where(AffiliationPublication.publication ==
                                                                        pub_id).order_by(Affiliation.affiliation_name)])
    return aff_list

def get_affiliations_by_author_id(author_id):
    aff_list = ", ".join([aff.affiliation_name for aff in
                          affiliations().join(AffiliationAuthor).where(AffiliationAuthor.author == author_id)
                         .order_by(Affiliation.affiliation_name)])
    return aff_list

def get_subjects_by_author_id(author_id):
    sub_list = ", ".join([sub.group for sub in Subject.select(Subject.group).distinct()
                         .join(AuthorSubject).where(AuthorSubject.author == author_id).order_by(Subject.group)])
    return sub_list

def get_pubs_count_by_author_id(author_id):
    count = authors_publications().where(AuthorPublication.author == author_id).count()
    return count

def get_subjects_by_publication_id(publication_id):
    sub_list = ", ".join([sub.group for sub in Subject.select(Subject.group).distinct()
                         .join(PublicationSubject).where(PublicationSubject.publication == publication_id)
                         .order_by(Subject.group)])
    return sub_list

def get_abbs_by_publication_id(publication_id):
    sub_list = ", ".join([sub.abbreviation for sub in Subject.select(Subject.abbreviation).distinct()
                         .join(PublicationSubject).where(PublicationSubject.publication == publication_id)
                         .order_by(Subject.abbreviation)])
    return sub_list

def get_authors_count_by_aff_id(aff_id):
    count = affiliations_authors().where(AffiliationAuthor.affiliation == aff_id).count()
    return count

def get_pubs_count_by_aff_id(aff_id):
    count = affiliations_publications().where(AffiliationPublication.affiliation == aff_id).count()
    return count

def get_sources(pub):
    sources = []
    if pub.scopus_id is not None:
        sources.append('Scopus')
    if pub.scholar_id is not None:
        sources.append('Google Scholar')
    if pub.core_id is not None:
        sources.append('CORE')
    if len(sources) == 0:
        sources.append('Internal')

    return '; '.join(sources)

def get_citations_count(uid):
    pubs = publications().join(AuthorPublication).where(AuthorPublication.author == uid)
    return sum([p.cited_by_count for p in pubs])
