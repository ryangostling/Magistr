# Internal
from database.biblio.models import Author, Affiliation, Subject, Publication, AuthorPublication, AffiliationPublication, \
    AffiliationAuthor, AuthorSubject, PublicationSubject
from database.biblio.selects import authors, affiliations, subjects, publications, authors_publications, \
    affiliations_publications, affiliations_authors, authors_subjects, publications_subjects


class ScopusExtractor:
    def __init__(self):
        self.ids = dict()
        self.ids['authors'] = authors().order_by(Author.author_id.desc()) \
                                       .get().author_id + 1 if len(authors()) != 0 else 1
        self.ids['affiliations'] = affiliations().order_by(Affiliation.affiliation_id.desc()) \
                                       .get().affiliation_id + 1 if len(affiliations()) != 0 else 1
        self.ids['subjects'] = subjects().order_by(Subject.subject_id.desc()) \
                                       .get().subject_id + 1 if len(subjects()) != 0 else 1
        self.ids['publications'] = publications().order_by(Publication.publication_id.desc())\
                                       .get().publication_id + 1 if len(publications()) != 0 else 1
        self.ids['authors_publications'] = authors_publications()\
                                           .order_by(AuthorPublication.author_publication_id.desc())\
                                           .get().author_publication_id + 1 \
                                            if len(authors_publications()) != 0 else 1
        self.ids['affiliations_publications'] = affiliations_publications() \
                                                .order_by(AffiliationPublication.affiliation_publication_id.desc()) \
                                                .get().affiliation_publication_id + 1 \
                                                if len(affiliations_publications()) != 0 else 1
        self.ids['affiliations_authors'] = affiliations_authors() \
                                           .order_by(AffiliationAuthor.affiliation_author_id.desc()) \
                                           .get().affiliation_author_id + 1 \
                                            if len(affiliations_authors()) != 0 else 1
        self.ids['authors_subjects'] = authors_subjects() \
                                       .order_by(AuthorSubject.author_subject_id.desc()) \
                                       .get().author_subject_id + 1 \
                                        if len(authors_subjects()) != 0 else 1
        self.ids['publications_subjects'] = publications_subjects() \
                                        .order_by(PublicationSubject.publication_subject_id.desc()) \
                                        .get().publication_subject_id + 1 \
                                        if len(publications_subjects()) != 0 else 1

        self.subjects = {'AGRI': 'Agricultural and Biological Sciences', 'ARTS': 'Arts and Humanities',
                         'BIOC': 'Biochemistry, Genetics and Molecular Biology', 'CHEM': 'Chemistry',
                         'BUSI': 'Business, Management, and Accounting', 'CENG': 'Chemical Engineering',
                         'COMP': 'Computer Science', 'DECI': 'Decision Science', 'DENT': 'Dentistry',
                         'EART': 'Earth and Planetary Sciences', 'ECON': 'Economics, Econometrics and Finance',
                         'ENER': 'Energy', 'ENGI': 'Engineering', 'ENVI': 'Environmental Science',
                         'HEAL': 'Health Professions', 'IMMU': 'Immunology and Microbiology',
                         'MATE': 'Materials Science', 'MATH': 'Mathematics', 'MEDI': 'Medicine',
                         'MULT': 'Multidisciplinary', 'NEUR': 'Neuroscience', 'NURS': 'Nursing',
                         'PHAR': 'Pharmacology, Toxicology and Pharmaceutic', 'PHYS': 'Physics and Astronomy',
                         'PSYC': 'Psychology', 'SOCI': 'Social Sciences', 'VETE': 'Veterinary'}

    def create_affiliation(self, affiliation):
        print('create_affiliation')
        row = Affiliation(affiliation_id=self.ids['affiliations'], scopus_id=str(affiliation.identifier),
                          affiliation_name=affiliation.affiliation_name, city=affiliation.city,
                          country=affiliation.country, address=affiliation.address, url=affiliation.org_URL)
        self.ids['affiliations'] += 1
        return row

    def create_author(self, author):
        print('create_author')
        if author.given_name is not None:
            name = f'{author.surname} {author.given_name}'
        else:
            name = author.surname
        row = Author(author_id=self.ids['authors'], scopus_id=str(author.identifier),
                     surname=author.surname, name=name, h_index=author.h_index,
                     cited_by_count=author.cited_by_count, coauthors_count=author.coauthor_count)
        if str(author.identifier) == '57201382610':
            row.name = 'Koval Olexandr'
        self.ids['authors'] += 1
        return row

    def create_subject(self, subject):
        print('create_subject')
        if subject.abbreviation is not None and subject.abbreviation != '':
            group = self.subjects[subject.abbreviation]
        else:
            group = self.subjects['MULT']
        row = Subject(subject_id=self.ids['subjects'], full_title=subject.area,
                      group=group, abbreviation=subject.abbreviation, code=subject.code)
        self.ids['subjects'] += 1
        return row

    def create_publication(self, publication, abstract, keywords):
        print('create_publication')
        row = Publication(publication_id=self.ids['publications'], scopus_id=str(publication.identifier),
                          title=publication.title.title(), abstract=abstract, keywords=keywords,
                          url=publication.url, cited_by_count=publication.citedby_count,
                          pub_date=publication.coverDate, alternative_titles=publication.title)
        self.ids['publications'] += 1
        return row

    def create_author_publication(self, author, publication):
        print('create_author_publication')
        row = AuthorPublication(author_publication_id=self.ids['authors_publications'],
                                author=author, publication=publication)
        self.ids['authors_publications'] += 1
        return row

    def create_author_subject(self, author, subject):
        print('create_author_subject')
        row = AuthorSubject(author_subject_id=self.ids['authors_subjects'],
                            author=author, subject=subject)
        self.ids['authors_subjects'] += 1
        return row

    def create_publication_subject(self, publication, subject):
        print('create_publication_subject')
        row = PublicationSubject(publication_subject_id=self.ids['publications_subjects'],
                                 publication=publication, subject=subject)
        self.ids['publications_subjects'] += 1
        return row

    def create_affiliation_author(self, affiliation, author):
        print('create_affiliation_author')
        row = AffiliationAuthor(affiliation_author_id=self.ids['affiliations_authors'],
                                affiliation=affiliation, author=author)
        self.ids['affiliations_authors'] += 1
        return row

    def create_affiliation_publication(self, affiliation, publication):
        print('create_affiliation_publication')
        row = AffiliationPublication(affiliation_publication_id=self.ids['affiliations_publications'],
                                     affiliation=affiliation, publication=publication)
        self.ids['affiliations_publications'] += 1
        return row
