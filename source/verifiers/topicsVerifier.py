from database.biblio.models import Publication, Subject, PublicationSubject
from database.biblio.selects import publications_subjects
from verifiers.base_verifier import BaseVerifier


class TopicsVerifier(BaseVerifier):

    next_verifier = None
    isStrict = True
    succeed = None
    fail = None
    flag = False

    def __init__(self, isStrict, succeed, fail, topics):
        self.topics = topics
        super().__init__(isStrict, succeed, fail)

    # Метод верифікації
    def verify(self, p, verified_pubs, pub_affs):
        # Формування списку тем для даної публікації
        ps = [s.publication_subject_id for s in publications_subjects().join(Publication)
            .where(PublicationSubject.publication.publication_id == p.publication_id)]
        p_topics = [s.subject.group for s in publications_subjects().join(Subject)
                  if s.publication_subject_id in ps]

        # Якщо перевірка строга
        if self.isStrict:
            # Якщо є збіг по темам
            if len(list(set(self.topics) & set(p_topics))) != 0:
                # Відмічення прапору успіху
                self.flag = True
                # Передача запиту базовому обробнику
                super().verify(p, verified_pubs, pub_affs)
        else:
            # Якщо є збіг по темам
            if len(list(set(self.topics) & set(p_topics))) != 0:
                # Відмічення прапору успіху
                self.flag = True
                # Якщо статті ще немає у списку верифікованих, то додати її
                if p not in verified_pubs:
                    verified_pubs.append(p)
            # Передача запиту базовому обробнику
            super().verify(p, verified_pubs, pub_affs)
