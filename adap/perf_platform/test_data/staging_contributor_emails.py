"""
Generating list of contributor user emails that were
created and validated in Staging env
"""


def get():
    emails = []
    groups = range(1, 10)
    workers = range(1, 1000)
    for group_id in groups:
        for worker_id in workers:
            ele = {'worker_email': f"stage+load+worker{group_id}+{worker_id}@figure-eight.com"}
            emails.append(ele)
    return emails
