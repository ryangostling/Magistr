# Internal
from database.biblio.models import Affiliation, Author, Publication, Subject, AuthorPublication, AuthorSubject, \
    PublicationSubject, AffiliationPublication, AffiliationAuthor


def affiliations():
    return Affiliation.select()

def authors():
    return Author.select()

def publications():
    return Publication.select()

def subjects():
    return Subject.select()

def authors_publications():
    return AuthorPublication.select()

def authors_subjects():
    return AuthorSubject.select()

def publications_subjects():
    return PublicationSubject.select()

def affiliations_publications():
    return AffiliationPublication.select()

def affiliations_authors():
    return AffiliationAuthor.select()
