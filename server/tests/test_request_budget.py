from tornado.testing import AsyncHTTPTestCase

from server.http import RequestBudget, application


def test_concurrency_is_bounded_without_consuming_refused_token():
    budget = RequestBudget(capacity=3, concurrent=1, clock=lambda: 100)
    assert budget.acquire()
    assert not budget.acquire() and budget.tokens == 2
    budget.release()
    assert budget.acquire()


def test_rate_budget_refills_but_cannot_accumulate_above_capacity():
    now = [100]
    budget = RequestBudget(capacity=1, per_second=2, clock=lambda: now[0])
    assert budget.acquire()
    budget.release()
    assert not budget.acquire()
    now[0] += 0.5
    assert budget.acquire()
    budget.release()
    now[0] += 10000
    assert budget.acquire()
    assert budget.tokens == 0


class BudgetTests(AsyncHTTPTestCase):
    def get_app(self):
        self.budget = RequestBudget(capacity=1, clock=lambda: 100)
        return application(request_budget=self.budget)

    def test_completed_requests_release_slots_and_health_is_independent(self):
        headers = {'Host':'platform.lazying.art'}
        assert self.fetch('/account',headers=headers).code == 200
        assert self.budget.active == 0
        response = self.fetch('/account',headers=headers)
        assert response.code == 429 and response.headers['Retry-After'] == '1'
        assert self.budget.active == 0
        assert self.fetch('/healthz',headers=headers).code == 200

    def test_foreign_hosts_do_not_consume_account_budget(self):
        assert self.fetch('/account',headers={'Host':'foreign.example'}).code == 400
        assert self.budget.tokens == 1 and self.budget.active == 0
