from fuzzywuzzy import fuzz

from database.biblio.models import AuthorPublication, Author
from database.biblio.selects import authors


def filter_publications_by_title(pubs, title):
    pubs_list = []
    for p in pubs:
        if any(filter(lambda t: fuzz.partial_ratio(t.lower(), title) >= 75, p.alternative_titles.split(' | '))):
            pubs_list.append(p)

    return pubs_list

def filter_publications_by_authors(pubs, selected_authors):
    pubs_list = []
    for p in pubs:
        auths = authors().join(AuthorPublication, on=(Author.author_id == AuthorPublication.author)) \
            .where(AuthorPublication.publication == p.publication_id)
        for a in auths:
            if any([fuzz.partial_ratio(a.name.lower(), au.lower()) >= 95 for au in selected_authors]):
                pubs_list.append(p)
                break
    return pubs_list

def filter_authors_by_name(authors, name):
    auth_list = []
    for a in authors:
        print(a.name.lower())
        if fuzz.partial_ratio(a.name.lower(), name.lower()) >= 93:
            auth_list.append(a)
    return auth_list

def filter_affiliations_by_name(affs, name):
    affs_list = []
    for a in affs:
        if fuzz.partial_ratio(name.lower(), a.affiliation_name.lower()) >= 90:
            affs_list.append(a)
    return affs_list

def filter_publications_by_sources(pubs, sources):
    pubs_list = []

    for p in pubs:
        if p.scopus_id is not None:
            if 'Scopus' in sources:
                pubs_list.append(p)
                continue
        if p.scholar_id is not None:
            if 'Google Scholar' in sources:
                pubs_list.append(p)
                continue
        if p.core_id is not None:
            if 'CORE' in sources:
                pubs_list.append(p)
                continue
        if p.scopus_id is None and p.scholar_id is None and p.core_id is None:
            pubs_list.append(p)

    return pubs_list
