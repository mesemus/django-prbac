# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function

# Standard Library Imports

# Django imports
from django.test import TestCase # https://code.djangoproject.com/ticket/20913

# External Library imports

# Local imports
from django_prbac.models import *
from django_prbac import arbitrary


class TestRole(TestCase):

    def test_has_permission_immediate_no_params(self):
        subrole = arbitrary.role()
        superrole1 = arbitrary.role()
        superrole2 = arbitrary.role()
        grant = arbitrary.grant(to_role=superrole1, from_role=subrole)

        self.assertTrue(subrole.instantiate({}).has_privilege(superrole1.instantiate({})))
        self.assertFalse(subrole.instantiate({}).has_privilege(superrole2.instantiate({})))


    def test_has_permission_transitive_no_params(self):
        subrole = arbitrary.role()
        midrole = arbitrary.role()
        superrole1 = arbitrary.role()
        superrole2 = arbitrary.role()
        grant = arbitrary.grant(to_role=midrole, from_role=subrole)
        grant = arbitrary.grant(to_role=superrole1, from_role=midrole)

        self.assertTrue(subrole.instantiate({}).has_privilege(superrole1.instantiate({})))
        self.assertFalse(subrole.instantiate({}).has_privilege(superrole2.instantiate({})))


    def test_has_permission_far_transitive_no_params(self):
        subrole = arbitrary.role()
        superrole1 = arbitrary.role()
        superrole2 = arbitrary.role()

        midroles = [arbitrary.role() for __ in xrange(0, 10)]

        arbitrary.grant(subrole, midroles[0])
        arbitrary.grant(midroles[-1], superrole1)

        # Link up all roles in the list that are adjacent
        for midsubrole, midsuperrole in zip(midroles[:-1], midroles[1:]):
            arbitrary.grant(from_role=midsubrole, to_role=midsuperrole)

        self.assertTrue(subrole.instantiate({}).has_privilege(superrole1.instantiate({})))
        self.assertFalse(subrole.instantiate({}).has_privilege(superrole2.instantiate({})))


    # TODO: The custom field types storing the parameters are a bit wonky; fix them first
    # def test_has_permission_immediate_params(self):
    #     subrole = arbitrary.role()
    #     superrole1 = arbitrary.role(parameters=set(['one']))
    #     grant = arbitrary.grant(to_role=superrole1, from_role=subrole, assignment=dict(one='foo'))
    #
    #     print(subrole.memberships_granted.all())
    #
    #     self.assertTrue(subrole.instantiate({}).has_privilege(superrole1.instantiate(dict(one='foo'))))
    #     self.assertFalse(subrole.instantiate({}).has_privilege(superrole1.instantiate(dict(one='baz'))))

class TestGrant(TestCase):

    def test_instantiated_to_role_smoke_test(self):
        """
        Basic smoke test:
        1. grant.instantiated_role({})[param] == grant.assignment[param] if param is free for the role
        2. grant.instantiated_role({})[param] does not exist if param is not free for the role
        """

        parameters = ['one']

        superrole = arbitrary.role(parameters=parameters)
        grant = arbitrary.grant(to_role=superrole, assignment={'one':'hello'})
        self.assertEqual(grant.instantiated_to_role({}).assignment, {'one':'hello'})

        grant = arbitrary.grant(to_role=superrole, assignment={'two': 'goodbye'})
        self.assertEqual(grant.instantiated_to_role({}).assignment, {})
