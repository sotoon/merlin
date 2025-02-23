from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from api.models import Form, FormAssignment, User, Cycle, FormResponse, Question

class FormAssignedByAPITestCase(APITestCase):

    def setUp(self):
        self.cycle = Cycle.objects.create(
            name="Test Cycle",
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() + timedelta(days=5),
        )

        # Create users
        self.user_leader = User.objects.create(email="leader@example.com", password="password123", name="Leader User")
        self.user_member1 = User.objects.create(email="member1@example.com", password="password123", name="Member User 1")
        self.user_member2 = User.objects.create(email="member2@example.com", password="password123", name="Member User 2")

        # Create forms
        self.form1 = Form.objects.create(name="Form 1", is_default=False, form_type="TL", cycle=self.cycle)
        self.form2 = Form.objects.create(name="Form 2", is_default=False, form_type="TL", cycle=self.cycle)
        self.form3 = Form.objects.create(name="Form 3", is_default=False, form_type="PM", cycle=self.cycle)

        # Assign forms where `user_leader` is the `assigned_by`
        FormAssignment.objects.create(form=self.form1, assigned_to=self.user_member1, assigned_by=self.user_leader, deadline=self.cycle.end_date)
        FormAssignment.objects.create(form=self.form2, assigned_to=self.user_member2, assigned_by=self.user_leader, deadline=self.cycle.end_date)

        # Assign a form where `user_member1` is `assigned_by` (should NOT be returned in the test)
        FormAssignment.objects.create(form=self.form3, assigned_to=self.user_member2, assigned_by=self.user_member1, deadline=self.cycle.end_date)

    def test_list_forms_assigned_by_current_user(self):
        """Test that only forms assigned BY the current user are returned"""
        url = "/api/forms/assigned-by/"

        # Authenticate as the leader
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        form_ids = [form["id"] for form in response.data]
        self.assertIn(self.form1.id, form_ids)
        self.assertIn(self.form2.id, form_ids)
        self.assertNotIn(self.form3.id, form_ids)

    def test_no_forms_if_not_assigned_by_current_user(self):
        """Test that a user who has not assigned any forms gets an empty response"""
        url = "/api/forms/assigned-by/"

        # Authenticate as a user who hasn't assigned any forms
        self.client.force_authenticate(user=self.user_member2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class FormResultsAPITestCase(APITestCase):
    
    def setUp(self):
        # Create a cycle that ended in the past
        self.cycle = Cycle.objects.create(
            name="Test Cycle",
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=5)
        )

        # Create unique users for testing
        self.user_leader = User.objects.create(email="leader_1@example.com", password="password123", name="Leader User")
        self.user_member = User.objects.create(email="member_1@example.com", password="password123", name="Member User")
        self.manager_user = User.objects.create(email="manager@example.com", password="password123", name="Manager User")
        
        self.user_leader.leader = self.manager_user
        self.user_leader.save()

        # Create a default form (results shown after cycle.end_date)
        self.form_default = Form.objects.create(
            name="Default Form",
            is_default=True,
            form_type="TL",
            cycle=self.cycle
        )

        # Create a manually assigned form (results shown after assignment deadline)
        self.form_manual = Form.objects.create(
            name="Manual Form",
            is_default=False,
            form_type="PM",
            cycle=self.cycle
        )

        # Create questions for the form
        self.question_default = Question.objects.create(
            form=self.form_default,
            question_text="Test Default Q1?",
            category="Cat.1",
            scale_min=1,
            scale_max=5
        )
        self.question_manual = Question.objects.create(
            form=self.form_manual,
            question_text="Test Manual Q2?",
            category="Cat.2",
            scale_min=1,
            scale_max=5
        )

        # Assign form to user as assigned_by (leader)
        self.assignment_default = FormAssignment.objects.create(
            form=self.form_default,
            assigned_to=self.user_member,
            assigned_by=self.user_leader,
            deadline=self.cycle.end_date    # Passed
        )

        # For manual form, create two assignments:
        # One with a passed deadline...
        self.assignment_manual_passed = FormAssignment.objects.create(
            form=self.form_manual,
            assigned_to=self.user_member,
            assigned_by=self.user_leader,
            deadline=timezone.now().date() - timedelta(days=1)  # Passed
        )
        # ...and one with a future deadline.
        self.assignment_manual_future = FormAssignment.objects.create(
            form=self.form_manual,
            assigned_to=self.user_member,
            assigned_by=self.user_leader,
            deadline=timezone.now().date() + timedelta(days=1)  # Not passed
        )

        # Create responses for the user member
        FormResponse.objects.create(
            form=self.form_default,
            user=self.user_member,
            question=self.question_default,
            answer="5",
            date_created=timezone.now()
        )

        FormResponse.objects.create(
            form=self.form_manual,
            user=self.user_member,
            question=self.question_manual,
            answer="3",
            date_created=timezone.now()
        )

    def test_results_with_invalid_cycle(self):
        """Test that results are blocked if cycle has not ended"""
        # Set cycle end date to a future date (for this test)
        future_cycle = Cycle.objects.create(
            name="Future Test Cycle",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10)
        )
        url = f"/api/forms/{self.form_default.id}/results/?cycle_id={future_cycle.id}"
        
        # Leader is assigned_by, so they can view the results
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Results for this form are not available until the cycle ends.")
    
    def test_results_with_valid_cycle_and_assigned_by_default(self):
        """
        For a default form, since the cycle has ended and the assignment deadline is met,
        the assigned_by user should get a 200 OK response with aggregated results.
        """
        url = f"/api/forms/{self.form_default.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect the response to be a list with at least one aggregated result.
        self.assertIsInstance(response.data, list)
        # Check that each item contains the aggregated fields and user info.
        for result in response.data:
            self.assertIn("total_average", result)
            self.assertIn("categories", result)
            self.assertIn("questions", result)
            self.assertIn("assigned_by", result)
            self.assertIn("assigned_by_name", result)

           # Since self.user_leader is the assessed user in this test, assigned_by should match.
            self.assertEqual(result["assigned_by"], self.user_leader.id)
            self.assertEqual(result["assigned_by_name"], self.user_leader.name)

    def test_results_with_valid_cycle_and_assigned_by_manual(self):
        """
        For a manually assigned form with a passed deadline (assignment_manual_passed),
        the assigned_by user should receive a 200 OK response.
        """
        url = f"/api/forms/{self.form_manual.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        # Both assignments exist; this query should pick the one with deadline <= today.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        for result in response.data:
            self.assertIn("total_average", result)
            self.assertIn("assigned_by", result)
            self.assertIn("assigned_by_name", result)
            # The result's assessed user should be self.user_leader
            self.assertEqual(result["assigned_by"], self.user_leader.id)
            self.assertEqual(result["assigned_by_name"], self.user_leader.name)

    def test_results_without_permission(self):
        """
        A user who is neither the assessed user nor the leader of the assessed user should get a 403 Forbidden.
        """
        url = f"/api/forms/{self.form_default.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_member)  # Not the assigned_by
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You are not authorized to view results for this form.")

    def test_results_with_deadline_not_met_manual(self):
        """
        For a manually assigned form, if the only assignment has a future deadline,
        results should not be shown and a 400 error is returned.
        """
        # Remove the passed-deadline assignment so that only the future one remains.
        self.assignment_manual_passed.delete()
        
        url = f"/api/forms/{self.form_manual.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Results for this form are not available until the deadline passes", response.data["detail"])
    
    def test_results_accessible_by_manager(self):
        """
        Test that a manager (i.e., the leader of the assessed user) can see the results.
        """
        url = f"/api/forms/{self.form_default.id}/results/?cycle_id={self.cycle.id}"
        # Authenticate as the manager (manager_user), which is the leader of user_leader.
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        for result in response.data:
            # The results should reflect that the assessed user is user_leader.
            self.assertEqual(result["assigned_by"], self.user_leader.id)
            self.assertEqual(result["assigned_by_name"], self.user_leader.name)
