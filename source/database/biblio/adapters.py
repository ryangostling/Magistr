def aff_pub_to_dict(a_p):
    return {'affiliation_publication_id': a_p.affiliation_publication_id,
            'affiliation': a_p.affiliation.affiliation_id,
            'publication': a_p.publication.publication_id}

def auth_pub_to_dict(a_p):
    return {'author_publication_id': a_p.author_publication_id,
            'author': a_p.author.author_id,
            'publication': a_p.publication.publication_id}

def aff_auth_to_dict(a_a):
    return {'affiliation_author_id': a_a.affiliation_author_id,
            'affiliation': a_a.affiliation.affiliation_id,
            'author': a_a.author.author_id}

def auth_sub_to_dict(a_s):
    return {'author_subject_id': a_s.author_subject_id,
            'author': a_s.author.author_id,
            'subject': a_s.subject.subject_id}

def pub_sub_to_dict(p_s):
    return {'publication_subject_id': p_s.publication_subject_id,
            'publication': p_s.publication.publication_id,
            'subject': p_s.subject.subject_id}
