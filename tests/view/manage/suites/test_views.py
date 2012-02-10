# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for suite management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class SuitesTest(case.view.manage.ListViewFinderTestCase):
    """Test for suites manage list view."""
    form_id = "manage-suites-form"
    perm = "manage_suites"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.SuiteFactory


    @property
    def url(self):
        """Shortcut for manage-suites url."""
        return reverse("manage_suites")


    def test_filter_by_status(self):
        """Can filter by status."""
        self.factory.create(name="Foo 1", status=self.model.Suite.STATUS.active)
        self.factory.create(name="Foo 2", status=self.model.Suite.STATUS.draft)

        res = self.get(params={"filter-status": "active"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_product(self):
        """Can filter by product."""
        one = self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-product": str(one.product.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_run(self):
        """Can filter by run."""
        one = self.factory.create(name="Foo 1")
        rs = self.F.RunSuiteFactory.create(suite=one)
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-run": str(rs.run.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_description(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1", description="foo bar")
        self.factory.create(name="Foo 2", description="bar baz")

        res = self.get(params={"filter-description": "foo"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_case_id(self):
        """Can filter by included case id."""
        one = self.factory.create(name="Foo 1")
        sc = self.F.SuiteCaseFactory.create(suite=one)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-case": str(sc.case.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_sort_by_status(self):
        """Can sort by status."""
        self.factory.create(name="Suite 1", status=self.model.Suite.STATUS.active)
        self.factory.create(name="Suite 2", status=self.model.Suite.STATUS.draft)

        res = self.get(
            params={"sortfield": "status", "sortdirection": "desc"})

        self.assertOrderInList(res, "Suite 2", "Suite 1")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Suite 1")
        self.factory.create(name="Suite 2")

        res = self.get(
            params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Suite 2", "Suite 1")


    def test_sort_by_product(self):
        """Can sort by product."""
        pb = self.F.ProductFactory.create(name="B")
        pa = self.F.ProductFactory.create(name="A")
        self.factory.create(name="Foo 1", product=pb)
        self.factory.create(name="Foo 2", product=pa)

        res = self.get(
            params={"sortfield": "product", "sortdirection": "asc"})

        self.assertOrderInList(res, "Foo 2", "Foo 1")


    def test_link_to_manage_cases(self):
        """Contains link to manage cases in suite."""
        s = self.factory.create(name="Foo")

        res = self.get()

        self.assertElement(
            res.html,
            "a",
            href="{0}?filter-suite={1}".format(
                reverse("manage_cases"), str(s.id)
                )
            )



class SuiteDetailTest(case.view.AuthenticatedViewTestCase):
    """Test for suite-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a suite."""
        super(SuiteDetailTest, self).setUp()
        self.testsuite = self.F.SuiteFactory.create()


    @property
    def url(self):
        """Shortcut for suite detail url."""
        return reverse(
            "manage_suite_details",
            kwargs=dict(suite_id=self.testsuite.id)
            )


    def test_details_description(self):
        """Details lists description."""
        self.testsuite.description = "foodesc"
        self.testsuite.save()

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("foodesc")



class AddSuiteTest(case.view.FormViewTestCase):
    """Tests for add suite view."""
    form_id = "suite-add-form"


    @property
    def url(self):
        """Shortcut for add-suite url."""
        return reverse("manage_suite_add")


    def setUp(self):
        """Add manage-suites permission to user."""
        super(AddSuiteTest, self).setUp()
        self.add_perm("manage_suites")


    def test_success(self):
        """Can add a suite with basic data."""
        p = self.F.ProductFactory.create()
        form = self.get_form()
        form["product"] = str(p.id)
        form["name"] = "Foo Suite"
        form["description"] = "Foo desc"
        form["status"] = "active"

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_suites"))

        res.follow().mustcontain("Suite 'Foo Suite' added.")

        s = p.suites.get()
        self.assertEqual(s.name, "Foo Suite")
        self.assertEqual(s.description, "Foo desc")
        self.assertEqual(s.status, "active")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_suites_permission(self):
        """Requires manage-suites permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)



class EditSuiteTest(case.view.FormViewTestCase):
    """Tests for edit-suite view."""
    form_id = "suite-edit-form"


    def setUp(self):
        """Setup for edit tests; create suite, add perm."""
        super(EditSuiteTest, self).setUp()
        self.testsuite = self.F.SuiteFactory.create()
        self.add_perm("manage_suites")


    @property
    def url(self):
        """Shortcut for edit-suite url."""
        return reverse(
            "manage_suite_edit", kwargs=dict(suite_id=self.testsuite.id))


    def test_requires_manage_suites_permission(self):
        """Requires manage-suites permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)


    def test_save_basic(self):
        """Can save updates; redirects to manage suites list."""
        form = self.get_form()
        form["name"] = "New Foo"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_suites"))

        res.follow().mustcontain("Saved 'New Foo'.")

        r = self.refresh(self.testsuite)
        self.assertEqual(r.name, "New Foo")



    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["name"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")