from django.utils.unittest import TestCase


class DynamiqBaseTests(TestCase):

    def assertEqualQ(self, Q1, Q2):
        self.assertEqual(str(Q1), str(Q2))
