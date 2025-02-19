"""
Generating list of requestor user emails that were
created and validated in Integration env
"""

def get():
    template = 'qa+performance2+user{_id}@figure-eight.com'
    emails = [template.format(_id=i) for i in range(100)]
    return [{'user_email': e} for e in emails]
