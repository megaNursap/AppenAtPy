"""
Generating list of contributor user emails that were
created and validated in QA env
"""


def get():
    emails = []
    groups = [1, 10, 100, 2, 20, 200, 3, 30, 300, 4, 40, 400, 5, 50, 500, 6, 60, 600, 7, 70, 700, 8, 80, 800, 9, 90, 900]
    workers = range(1, 1000)
    for group_id in groups:
        for worker_id in workers:
            ele = {'worker_email': f"qa+performance+worker{group_id}+{worker_id}@figure-eight.com"}
            emails.append(ele)
    return emails
