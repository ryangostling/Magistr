# External
from datetime import datetime

# Internal
from database.biblio.models import Publication, AuthorPublication, AffiliationPublication
from database.biblio.selects import publications, authors_publications, affiliations_publications


class CoreExtractor:
    def __init__(self):
        self.ids = dict()
        self.ids['publications'] = publications().order_by(Publication.publication_id.desc())\
                                       .get().publication_id + 1 if len(publications()) != 0 else 1
        self.ids['authors_publications'] = authors_publications()\
                                       .order_by(AuthorPublication.author_publication_id.desc())\
                                       .get().author_publication_id + 1 if len(authors_publications()) != 0\
                                        else 1
        self.ids['affiliations_publications'] = affiliations_publications()\
                                       .order_by(AffiliationPublication.affiliation_publication_id.desc())\
                                       .get().affiliation_publication_id + 1 if len(affiliations_publications()) != 0\
                                        else 1

    def create_publication(self, publication, title, abstract, keywords, alternative_titles):
        print('create_publication')
        if 'year' in publication:
            pub_date = datetime(int(publication['year']), 1, 1)
        else:
            pub_date = datetime.now()
        if len(publication['fulltextUrls']) != 0:
            url = publication['fulltextUrls'][0]
        else:
            url = ''
        row = Publication(publication_id=self.ids['publications'], title=title.title(), url=url,
                          abstract=abstract, cited_by_count=len(publication['citations']), keywords=keywords,
                          pub_date=pub_date, core_id=publication['id'], alternative_titles=alternative_titles)
        self.ids['publications'] += 1
        return row

    def create_author_publication(self, author, publication):
        print('create_author_publication')
        row = AuthorPublication(author_publication_id=self.ids['authors_publications'],
                                author=author, publication=publication)
        self.ids['authors_publications'] += 1
        return row

    def create_affiliation_publication(self, affiliation, publication):
        print('create_affiliation_publication')
        row = AffiliationPublication(affiliation_publication_id=self.ids['affiliations_publications'],
                                     affiliation=affiliation, publication=publication)
        self.ids['affiliations_publications'] += 1
        return row
