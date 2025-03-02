from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta, datetime, time

from api.models import Form, FormAssignment, User, Cycle, FormResponse, Question
from api.serializers import FormSerializer
from api.utils import calculate_form_results


class FormAssignedByAPITestCase(APITestCase):

    def setUp(self):
        self.cycle = Cycle.objects.create(
            name="Test Cycle",
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=5),
        )

        # Create users
        self.user_manager = User.objects.create(email="manager@example.com", password="password123", name="Manager User")
        self.user_leader = User.objects.create(email="leader@example.com", password="password123", name="Leader User")
        self.user_leader2 = User.objects.create(email="leader2@example.com", password="password123", name="Leader User 2")
        self.user_member1 = User.objects.create(email="member1@example.com", password="password123", name="Member User 1")
        self.user_member2 = User.objects.create(email="member2@example.com", password="password123", name="Member User 2")
        self.user_member3 = User.objects.create(email="member3@example.com", password="password123", name="Member User 3")

        # Set leadership relations
        self.user_leader.leader = self.user_manager
        self.user_leader2.leader = self.user_manager
        self.user_member1.leader = self.user_leader
        self.user_member2.leader = self.user_leader2
        self.user_leader.save()
        self.user_leader2.save()
        self.user_member1.save()
        self.user_member2.save()

        # Create forms
        self.form1 = Form.objects.create(name="Form 1", is_default=False, form_type="TL", cycle=self.cycle)
        self.form2 = Form.objects.create(name="Form 2", is_default=False, form_type="TL", cycle=self.cycle)
        self.form3 = Form.objects.create(name="Form 3", is_default=True, form_type="PM", cycle=self.cycle)
        self.form4 = Form.objects.create(name="Form 4", is_default=False, form_type="TL", cycle=self.cycle)

        # Assign forms where `user_leader` is the `assigned_by`
        FormAssignment.objects.create(form=self.form1, assigned_to=self.user_member1, assigned_by=self.user_leader, deadline=self.cycle.end_date)
        FormAssignment.objects.create(form=self.form2, assigned_to=self.user_member2, assigned_by=self.user_leader2, deadline=self.cycle.end_date)

        # Assign a form where `user_member1` is `assigned_by` (should NOT be returned in the test)
        FormAssignment.objects.create(form=self.form3, assigned_to=self.user_member2, assigned_by=self.user_member1, deadline=self.cycle.end_date)
        
        # For Form 4 (mixed): create two assignments, one from each leader
        FormAssignment.objects.create(form=self.form4, assigned_to=self.user_member1, assigned_by=self.user_leader, deadline=self.cycle.end_date)
        FormAssignment.objects.create(form=self.form4, assigned_to=self.user_member2, assigned_by=self.user_leader2, deadline=self.cycle.end_date)

    def test_list_forms_assigned_by_current_user(self):
        """Test that only forms assigned BY the current user are returned"""
        url = f"/api/forms/{self.form1.id}/results/?cycle_id={self.cycle.id}"

        # Authenticate as the leader
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIsInstance(response.data["my_results"], list)
        self.assertEqual(len(response.data["my_results"]), 1)
        
        result = response.data["my_results"][0]
        self.assertEqual(result["assigned_by"], self.user_leader.id)
        self.assertEqual(result["assigned_by_name"], self.user_leader.name)


    def test_no_forms_if_not_assigned_by_current_user(self):
        """Test that a user who has not assigned any forms gets an empty response"""
        url = f"/api/forms/{self.form3.id}/results/?cycle_id={self.cycle.id}"

        # Authenticate as a user who hasn't assigned any forms
        self.client.force_authenticate(user=self.user_member3)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You are not authorized to view results for this form.")
    
    def test_fetch_assigned_by_forms_accessible_by_manager(self):
        """
        Test that a manager can fetch forms where the current user is either:
        - the assessed user (assigned_by) 
        - or the leader of the assessed user (assigned_by__leader),
        filtered by cycle.
        """
        url = f"/api/forms/{self.form4.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["team_results"], list)

        # Build mapping from assigned_by to assigned_by_name from team_results.
        results_by_assigned_by = {result["assigned_by"]: result["assigned_by_name"] for result in response.data["team_results"]}
        
        self.assertIn(self.user_leader.id, results_by_assigned_by)
        self.assertEqual(results_by_assigned_by[self.user_leader.id], self.user_leader.name)
        
        self.assertIn(self.user_leader2.id, results_by_assigned_by)
        self.assertEqual(results_by_assigned_by[self.user_leader2.id], self.user_leader2.name)

    
    def test_fetch_assigned_by_forms_accessible_by_assessed_user(self):
        """
        Test that when the assessed user (user_leader) fetches the forms,
        the serializer returns their own name via 'assigned_by_name'.
        """
        url = f"/api/forms/{self.form1.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["my_results"], list)
        
        for result in response.data["my_results"]:
            self.assertIn("assigned_by_name", result)
            self.assertEqual(result["assigned_by_name"], self.user_leader.name)

    def test_fetch_assigned_by_forms_no_assignment(self):
        """
        Test that if a form has no assignments, it is not returned by the endpoint.
        (Or, if it is returned, its 'assigned_by_name' is empty.)
        """
        # Create a new form with the same cycle but no assignments.
        form_no_assignment = Form.objects.create(
            name="No Assignment Form",
            is_default=True,
            form_type="TL",
            cycle=self.cycle
        )
        url = f"/api/forms/{form_no_assignment.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert that the form is not in the "my_results" data (no assignments).
        self.assertNotIn(form_no_assignment.id, [f["assigned_by"] for f in response.data["my_results"]])
    
    def test_fetch_assigned_by_forms_multiple_assignments_consistency(self):
        """
        Test that if multiple assignments exist for a form with the same assessed user,
        the result consistently returns the same assigned_by_name.
        """
        # Create an extra assignment for form1 for the same assessed user (user_leader)
        FormAssignment.objects.create(
            form=self.form1,
            assigned_to=self.user_member1,
            assigned_by=self.user_leader,
            deadline=self.cycle.end_date
        )
        url = f"/api/forms/{self.form1.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All entries in "my_results" for form1 should have the same assigned_by_name.
        for result in response.data["my_results"]:
            self.assertEqual(result["assigned_by_name"], self.user_leader.name)
    
    def test_fetch_assigned_by_forms_mixed_scenario(self):
        """
        Test that a manager, when fetching results for a form that includes assignments from both a subordinate and another subordinate,
        sees the subordinate results in "team_results".
        For Form 4, team_results should include results for both Leader User and Leader User 2.
        """
        url = f"/api/forms/{self.form4.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["team_results"], list)
        
        results_by_assigned_by = {result["assigned_by"]: result["assigned_by_name"] for result in response.data["team_results"]}
        self.assertIn(self.user_leader.id, results_by_assigned_by)
        self.assertEqual(results_by_assigned_by[self.user_leader.id], self.user_leader.name)
        self.assertIn(self.user_leader2.id, results_by_assigned_by)
        self.assertEqual(results_by_assigned_by[self.user_leader2.id], self.user_leader2.name)

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
        self.user_leader2 = User.objects.create(email="leader2@example.com", password="password123", name="Leader User 2")
        self.user_leader3 = User.objects.create(email="leader3@example.com", password="password123", name="Leader User 3")
        self.user_member = User.objects.create(email="member_1@example.com", password="password123", name="Member User")
        self.user_member2 = User.objects.create(email="member_2@example.com", password="password123", name="Member User 2")
        self.user_member3 = User.objects.create(email="member_3@example.com", password="password123", name="Member User 3")
        self.manager_user = User.objects.create(email="manager@example.com", password="password123", name="Manager User")
        
        self.user_member.leader = self.user_leader
        self.user_member2.leader = self.user_leader2
        self.user_member3.leader = self.user_leader3
        self.user_leader.leader = self.manager_user
        self.user_leader2.leader = self.manager_user
        self.user_member.save()
        self.user_member2.save()
        self.user_member3.save()
        self.user_leader2.save()
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

        # Create a form where the assessed user is user_leader2.
        self.form_subordinate = Form.objects.create(
            name="Subordinate Form",
            is_default=True,
            form_type="TL",
            cycle=self.cycle
        )

        # Create a form where the assessed user is the manager.
        self.form_manager = Form.objects.create(
            name="Manager Form",
            is_default=True,
            form_type="MANAGER",
            cycle=self.cycle
        )

        # Create questions for the forms
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
        self.question_subordinate = Question.objects.create(
            form=self.form_subordinate,
            question_text="Test Subordinate Q1?",
            category="Cat.3",
            scale_min=1,
            scale_max=5
        )
        self.question_manager = Question.objects.create(
            form=self.form_manager,
            question_text="Test Manager Q1?",
            category="Cat.4",
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
        # Create an assignment for subordinate form with assessed user = user_leader2.
        self.assignment_subordinate = FormAssignment.objects.create(
            form=self.form_subordinate,
            assigned_to=self.user_member2,
            assigned_by=self.user_leader2,
            deadline=self.cycle.end_date     # Passed
        )
        # Create an assignment for subordinate form with assessed user = user_leader.
        self.assignment_subordinate = FormAssignment.objects.create(
            form=self.form_subordinate,
            assigned_to=self.user_member,
            assigned_by=self.user_leader,
            deadline=self.cycle.end_date     # Passed
        )
        # Create an assignment for manager form with assessed user = manager_user.
        self.assignment_manager = FormAssignment.objects.create(
            form=self.form_manager,
            assigned_to=self.user_leader,
            assigned_by=self.manager_user,
            deadline=self.cycle.end_date      # Passed
        )

        # Create responses for all forms
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
        FormResponse.objects.create(
            form=self.form_subordinate,
            user=self.user_member,
            question=self.question_subordinate,
            answer="4",
            date_created=timezone.now()
        )
        FormResponse.objects.create(
            form=self.form_subordinate,
            user=self.user_member2,
            question=self.question_subordinate,
            answer="4",
            date_created=timezone.now()
        )
        FormResponse.objects.create(
            form=self.form_manager,
            user=self.user_member,
            question=self.question_manager,
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
        # Expect the response to have "my_results" and "team_results"
        self.assertIsInstance(response.data, dict)        
        self.assertIn("my_results", response.data)
        self.assertIn("team_results", response.data)
        # Check that "my_results" contains the current user's results
        for result in response.data["my_results"]:
            self.assertIn("total_average", result)
            self.assertIn("categories", result)
            self.assertIn("questions", result)
            self.assertIn("assigned_by", result)
            self.assertIn("assigned_by_name", result)
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
        self.assertIsInstance(response.data, dict)        
        self.assertIn("my_results", response.data)
        self.assertIn("team_results", response.data)
        # Check that "my_results" contains the correct results for the current user
        for result in response.data["my_results"]:
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
    
    def test_results_accessible_by_manager_for_subordinate(self):
        """
        A manager should see subordinates' aggregated results under "team_results".
        """
        url = f"/api/forms/{self.form_default.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn("team_results", response.data)
        expected_ids = {self.user_leader.id, self.user_leader2.id}
        returned_ids = {result["assigned_by"] for result in response.data["team_results"]}
        self.assertEqual(returned_ids, expected_ids, f"Expected assessed IDs {expected_ids}, got {returned_ids}")
        for result in response.data["team_results"]:
            if result["assigned_by"] == self.user_leader.id:
                self.assertEqual(result["assigned_by_name"], self.user_leader.name)
            elif result["assigned_by"] == self.user_leader2.id:
                self.assertEqual(result["assigned_by_name"], self.user_leader2.name)
            else:
                self.fail(f"Unexpected assessed ID {result['assigned_by']}")
        
    def test_results_accessible_by_manager_for_self(self):
        """
        A manager should see their own aggregated results under "my_results".
        """
        url = f"/api/forms/{self.form_manager.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("my_results", response.data)
        for result in response.data["my_results"]:
            self.assertEqual(result["assigned_by"], self.manager_user.id)
            self.assertEqual(result["assigned_by_name"], self.manager_user.name)

    def test_no_assignments_for_user_or_subordinates(self):
        """Test that results are not available if the user has no assignments or their subordinates have no assignments"""

        url = f"/api/forms/{self.form_manager.id}/results/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader3)
        
        response = self.client.get(url)
        
        # Since there are no assignments, we should return a 403 Forbidden response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You are not authorized to view results for this form.")

class AssignedByEndpointTestCase(APITestCase):
    def setUp(self):
        # Create a cycle that has ended
        self.cycle = Cycle.objects.create(
            name="Test Cycle",
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=5)
        )
        
        # Create users
        self.user_manager = User.objects.create(email="manager@example.com", password="password123", name="Manager User")
        self.user_leader = User.objects.create(email="leader@example.com", password="password123", name="Leader User")
        self.user_leader2 = User.objects.create(email="leader2@example.com", password="password123", name="Leader User 2")
        self.user_member = User.objects.create(email="member@example.com", password="password123", name="Member User")
        self.user_other = User.objects.create(email="other@example.com", password="password123", name="Other User")
        self.user_other2 = User.objects.create(email="other2@example.com", password="password123", name="Other User2")

        
        # Set leadership relations
        self.user_leader.leader = self.user_manager
        self.user_leader2.leader = self.user_manager
        self.user_member.leader = self.user_leader
        self.user_leader.save()
        self.user_leader2.save()
        self.user_member.save()
        
        # Create forms
        self.form1 = Form.objects.create(name="Form 1", is_default=False, form_type="TL", cycle=self.cycle)
        self.form2 = Form.objects.create(name="Form 2", is_default=False, form_type="TL", cycle=self.cycle)
        self.form3 = Form.objects.create(name="Form 3", is_default=False, form_type="PM", cycle=self.cycle)
        self.form_manager = Form.objects.create(name="Manager Form", is_default=False, form_type="MANAGER", cycle=self.cycle)
        
        # Create assignments:
        # For form1, the assessed user is user_leader.
        FormAssignment.objects.create(
            form=self.form1, assigned_to=self.user_member, assigned_by=self.user_leader, deadline=self.cycle.end_date
        )
        # For form2, the assessed user is user_leader2.
        FormAssignment.objects.create(
            form=self.form2, assigned_to=self.user_member, assigned_by=self.user_leader2, deadline=self.cycle.end_date
        )
        # For form3, assigned_by is user_other (should not be returned for user_leader or user_manager)
        FormAssignment.objects.create(
            form=self.form3, assigned_to=self.user_member, assigned_by=self.user_other, deadline=self.cycle.end_date
        )
        # For form_manager: manager is directly assessed.
        FormAssignment.objects.create(form=self.form_manager, assigned_to=self.user_leader, assigned_by=self.user_manager, deadline=self.cycle.end_date
        )

    def test_fetch_assigned_forms_for_assessed_user(self):
        """
        When the current user is directly the assessed user, the form should appear under "my_forms".
        For example, user_leader should see Form 1.
        """
        url = f"/api/forms/assigned-by/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_leader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn("my_forms", response.data)
        self.assertIn("team_forms", response.data)
        my_forms_ids = [form["id"] for form in response.data["my_forms"]]
        self.assertIn(self.form1.id, my_forms_ids)
        # Verify that the serializer returns the current user's name.
        for form in response.data["my_forms"]:
            if form["id"] == self.form1.id:
                self.assertEqual(form["assigned_by_name"], self.user_leader.name)

    def test_assigned_forms_for_leader(self):
        """
        When a manager (who is the leader of assessed users) fetches the endpoint,
        they should see subordinate forms in "team_forms" and their own form in "my_forms".
        For example, user_manager should see Form 1 and Form 2. 
        """
        url = f"/api/forms/assigned-by/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn("my_forms", response.data)
        self.assertIn("team_forms", response.data)
        team_forms_ids = [form["id"] for form in response.data["team_forms"]]
        self.assertIn(self.form1.id, team_forms_ids)
        self.assertIn(self.form2.id, team_forms_ids)
        self.assertNotIn(self.form3.id, team_forms_ids)
        # Verify that assigned_by_name is the subordinate's name:
        for form in response.data["team_forms"]:
            if form["id"] == self.form1.id:
                self.assertEqual(form["assigned_by_name"], self.user_leader.name)
            if form["id"] == self.form2.id:
                self.assertEqual(form["assigned_by_name"], self.user_leader2.name)

    def test_fetch_assigned_forms_for_mixed_scenario(self):
        """
        When a manager is also directly assessed, the endpoint should return:
          - Forms where the manager is directly assessed in "my_forms".
          - And forms where the manager is the leader of the assessed user in "team_forms".
        For this test, user_manager is directly assessed in Form Manager.
        """
        url = f"/api/forms/assigned-by/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("my_forms", response.data)
        self.assertIn("team_forms", response.data)
        my_forms_ids = [form["id"] for form in response.data["my_forms"]]
        team_forms_ids = [form["id"] for form in response.data["team_forms"]]
        # Manager should see their own form in my_forms
        self.assertIn(self.form_manager.id, my_forms_ids)
        # And see subordinate forms (form1 and form2) in team_forms.
        self.assertIn(self.form1.id, team_forms_ids)
        self.assertIn(self.form2.id, team_forms_ids)
        # Check that names are correct:
        for form in response.data["my_forms"]:
            if form["id"] == self.form_manager.id:
                self.assertEqual(form["assigned_by_name"], self.user_manager.name)
        for form in response.data["team_forms"]:
            if form["id"] == self.form1.id:
                self.assertEqual(form["assigned_by_name"], self.user_leader.name)
            if form["id"] == self.form2.id:
                self.assertEqual(form["assigned_by_name"], self.user_leader2.name)

    def test_assigned_forms_empty_for_non_involved_user(self):
        """
        A user with no relevant assignments should get an empty result.
        For example, a user with no assignments should see both lists empty.
        """
        url = f"/api/forms/assigned-by/?cycle_id={self.cycle.id}"
        # Use a user who is not involved at all. Here, we use self.user_other.
        self.client.force_authenticate(user=self.user_other2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["my_forms"]), 0)
        self.assertEqual(len(response.data["team_forms"]), 0)

    def test_assigned_forms_invalid_cycle(self):
        """
        Test that if an invalid cycle_id is provided, the endpoint returns an error.
        """
        url = f"/api/forms/assigned-by/?cycle_id=9999"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_serializer_get_assigned_by_name_logic(self):
        """
        Directly test the get_assigned_by_name method of FormSerializer.
        The method should return:
          - For a form in my_forms, the current user's name (if they are the assessed user).
          - For a form in team_forms, the subordinate's name (i.e. the assessed user's name from the assignment where assigned_by__leader == request.user).
        """
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/dummy-url/")
        
        # Case: For form1, when the current user is user_leader (assessed user).
        request.user = self.user_leader
        serializer = FormSerializer(instance=self.form1, context={"request": request})
        # In our endpoint, our view would annotate form1 with _assigned_by_name.
        # For testing directly, we simulate that:
        self.form1._assigned_by_name = self.user_leader.name
        self.assertEqual(serializer.get_assigned_by_name(self.form1), self.user_leader.name)
        
        # Case: For form1, when current user is user_manager (leader of user_leader).
        request.user = self.user_manager
        serializer = FormSerializer(instance=self.form1, context={"request": request})
        # In our endpoint, form1 would be annotated with user_leader.name because user_manager is the leader.
        self.form1._assigned_by_name = self.user_leader.name
        self.assertEqual(serializer.get_assigned_by_name(self.form1), self.user_leader.name)

    def test_manager_sees_all_subordinate_assignments(self):
        """
        Verify that if a manager has multiple subordinate assignments on the same form,
        each subordinate assignment appears separately in team_forms.
        """
        # Create a new subordinate leader to simulate multiple subordinates
        user_leader3 = User.objects.create(email="leader3@example.com", password="password123", name="Leader User 3")
        user_leader3.leader = self.user_manager
        user_leader3.save()
        
        # Create a new form for this test
        form_multi = Form.objects.create(name="Multi Subordinate Form", is_default=False, form_type="TL", cycle=self.cycle)
        
        # Create assignments from three different subordinate leaders
        FormAssignment.objects.create(form=form_multi, assigned_to=self.user_member, assigned_by=self.user_leader, deadline=self.cycle.end_date)
        FormAssignment.objects.create(form=form_multi, assigned_to=self.user_member, assigned_by=self.user_leader2, deadline=self.cycle.end_date)
        FormAssignment.objects.create(form=form_multi, assigned_to=self.user_member, assigned_by=user_leader3, deadline=self.cycle.end_date)
        
        url = f"/api/forms/assigned-by/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Count how many times form_multi appears in team_forms
        count = sum(1 for form in response.data["team_forms"] if form["id"] == form_multi.id)
        # We expect it to appear 3 times, once for each subordinate assignment.
        self.assertEqual(count, 3)
        
        # Optionally, verify that each entry has the correct assigned_by_name.
        names = [form["assigned_by_name"] for form in response.data["team_forms"] if form["id"] == form_multi.id]
        self.assertIn(self.user_leader.name, names)
        self.assertIn(self.user_leader2.name, names)
        self.assertIn(user_leader3.name, names)

    def test_manager_sees_distinct_team_forms_for_multiple_subordinates(self):
        """
        Verify that if a manager has three subordinate leaders (each with 5 assignments on the same form),
        the endpoint returns one team_forms entry per subordinate (a total of 3 entries for that form),
        each with the correct assessed user (assigned_by) information.
        """
        # Create an additional subordinate leader
        user_leader3 = User.objects.create(
            email="leader3@example.com", password="password123", name="Leader User 3"
        )
        user_leader3.leader = self.user_manager
        user_leader3.save()
        
        # Create a new form for this test.
        form_test = Form.objects.create(
            name="Test Form", is_default=False, form_type="TL", cycle=self.cycle
        )
        
        # Create 5 assignments from each subordinate leader for the same form.
        for _ in range(5):
            FormAssignment.objects.create(
                form=form_test,
                assigned_to=self.user_member,   # Same assessor for simplicity.
                assigned_by=self.user_leader,     # First subordinate leader.
                deadline=self.cycle.end_date
            )
        for _ in range(5):
            FormAssignment.objects.create(
                form=form_test,
                assigned_to=self.user_member,
                assigned_by=self.user_leader2,    # Second subordinate leader.
                deadline=self.cycle.end_date
            )
        for _ in range(5):
            FormAssignment.objects.create(
                form=form_test,
                assigned_to=self.user_member,
                assigned_by=user_leader3,          # Third subordinate leader.
                deadline=self.cycle.end_date
            )
        
        # Call the assigned-by endpoint as the manager.
        url = f"/api/forms/assigned-by/?cycle_id={self.cycle.id}"
        self.client.force_authenticate(user=self.user_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # In the team_forms section, the test form should appear once per subordinate.
        team_entries = [entry for entry in response.data["team_forms"] if entry["id"] == form_test.id]
        # We expect exactly 3 entries (one for each distinct subordinate leader).
        self.assertEqual(len(team_entries), 3, f"Expected 3 entries for form_test, but found {len(team_entries)}.")
        
        # Verify that each entry's assigned_by_name is correct.
        expected_names = {self.user_leader.name, self.user_leader2.name, user_leader3.name}
        returned_names = {entry["assigned_by_name"] for entry in team_entries}
        self.assertEqual(returned_names, expected_names)


class ResultsAggregationMathTestCase(APITestCase):
    def setUp(self):
        # Create a cycle that has ended
        self.cycle = Cycle.objects.create(
            name="Aggregation Cycle",
            start_date=timezone.now() - timedelta(days=15),
            end_date=timezone.now() - timedelta(days=10)
        )
        # Create two distinct assessed leaders
        self.leader1 = User.objects.create(email="leader1@example.com", password="password123", name="Leader 1")
        self.leader2 = User.objects.create(email="leader2@example.com", password="password123", name="Leader 2")
        # Create a form and a single question for that form
        self.form = Form.objects.create(name="Aggregation Form", is_default=False, form_type="TL", cycle=self.cycle)
        self.question = Question.objects.create(
            form=self.form,
            question_text="Rate performance?",
            category="Performance",
            scale_min=1,
            scale_max=5
        )
        # Create more than 10 assessors for each group (no overlap)
        self.assessors_group1 = []
        self.assessors_group2 = []
        for i in range(10):
            user = User.objects.create(email=f"assessor1_{i}@example.com", password="password123", name=f"Assessor1_{i}")
            self.assessors_group1.append(user)
        for i in range(10):
            user = User.objects.create(email=f"assessor2_{i}@example.com", password="password123", name=f"Assessor2_{i}")
            self.assessors_group2.append(user)
        # Create assignments for group1: assessed by leader1
        for assessor in self.assessors_group1:
            FormAssignment.objects.create(
                form=self.form,
                assigned_to=assessor,
                assigned_by=self.leader1,
                deadline=self.cycle.end_date 
            )
        # Create assignments for group2: assessed by leader2
        for assessor in self.assessors_group2:
            FormAssignment.objects.create(
                form=self.form,
                assigned_to=assessor,
                assigned_by=self.leader2,
                deadline=self.cycle.end_date
            )

        response_date = self.cycle.start_date + timedelta(days=1)

        # Create responses:
        # For group1: every response is 4
        for assessor in self.assessors_group1:
            r = FormResponse.objects.create(
                form=self.form,
                user=assessor,
                question=self.question,
                answer=4,
                date_created=response_date
            )
        # For group2: every response is 3
        for assessor in self.assessors_group2:
            FormResponse.objects.create(
                form=self.form,
                user=assessor,
                question=self.question,
                answer=3,
                date_created=response_date
            )

        # This is to avoid model's auto_now_add field
        FormResponse.objects.all().update(date_created=response_date)

    def test_aggregation_math_for_group1(self):
        """
        Verify that the aggregated results for group1 (assessed by Leader 1) yield an overall average of 4.0.
        """
        adjusted_end_date = timezone.make_aware(datetime.combine(self.cycle.end_date, time.max))
        # Calculate the adjusted end date to match our query range.
        assignments_group1 = self.form.formassignment_set.filter(assigned_by=self.leader1)

        responses = FormResponse.objects.filter(
            question__form=self.form,
            user__in=assignments_group1.values_list("assigned_to", flat=True),
            date_created__range=(self.cycle.start_date, adjusted_end_date)
        )

        result = calculate_form_results(responses, self.form)
        self.assertAlmostEqual(result["total_average"], 4.0, places=2)

        for q in result["questions"]:
            self.assertAlmostEqual(q["average"], 4.0, places=2)

    def test_aggregation_math_for_group2(self):
        """
        Verify that the aggregated results for group2 (assessed by Leader 2) yield an overall average of 3.0.
        """
        adjusted_end_date = timezone.make_aware(datetime.combine(self.cycle.end_date, time.max))
        assignments_group2 = self.form.formassignment_set.filter(assigned_by=self.leader2)
        responses = FormResponse.objects.filter(
            question__form=self.form,
            user__in=assignments_group2.values_list("assigned_to", flat=True),
            date_created__range=(self.cycle.start_date, adjusted_end_date)
        )
        result = calculate_form_results(responses, self.form)
        self.assertAlmostEqual(result["total_average"], 3.0, places=2)
        for q in result["questions"]:
            self.assertAlmostEqual(q["average"], 3.0, places=2)

    def test_aggregation_with_null_response(self):
        """
        Verify that if one response in group1 is null, the aggregated results still yield an overall average of 4.0.
        (Django's Avg aggregation ignores nulls.)
        """
        # Get all assignments for group1 (assessed by leader1)
        assignments_group1 = self.form.formassignment_set.filter(assigned_by=self.leader1)
        # Get the responses for this question for group1
        responses_qs = FormResponse.objects.filter(
            question_id=self.question.id,
            user__in=assignments_group1.values_list("assigned_to", flat=True)
        )
        # Ensure at least one response exists, then update one to be null.
        first_response = responses_qs.first()
        first_response.answer = None
        first_response.save()
        
        # Re-fetch responses using the date range.
        adjusted_end_date = timezone.make_aware(datetime.combine(self.cycle.end_date, time.max))
        responses = FormResponse.objects.filter(
            question_id=self.question.id,
            user__in=assignments_group1.values_list("assigned_to", flat=True),
            date_created__range=(self.cycle.start_date, adjusted_end_date)
        )
        
        result = calculate_form_results(responses, self.form)
        
        # Expected: Even if one response is null, Django's Avg ignores it.
        self.assertAlmostEqual(result["total_average"], 4.0, places=2)
        for q in result["questions"]:
            self.assertAlmostEqual(q["average"], 4.0, places=2)
