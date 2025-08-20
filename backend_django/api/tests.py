from rest_framework.test import APITestCase
from django.urls import reverse


class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})


class NotesAuthFlowTests(APITestCase):
    def setUp(self):
        # register user
        resp = self.client.post(reverse("auth-register"), {
            "username": "alice",
            "email": "alice@example.com",
            "password": "supersecret123",
        }, format="json")
        self.assertIn(resp.status_code, (200, 201))

        # login user (session)
        resp = self.client.post(reverse("auth-login"), {
            "username": "alice",
            "password": "supersecret123",
        }, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_crud_notes(self):
        # create note
        create_resp = self.client.post("/api/notes/", {"title": "First", "content": "Hello"}, format="json")
        self.assertIn(create_resp.status_code, (200, 201))
        note_id = create_resp.data["id"]

        # list notes
        list_resp = self.client.get("/api/notes/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(len(list_resp.data) >= 1)

        # retrieve note
        get_resp = self.client.get(f"/api/notes/{note_id}/")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.data["title"], "First")

        # update note
        put_resp = self.client.put(f"/api/notes/{note_id}/", {"title": "Updated", "content": "World"}, format="json")
        self.assertEqual(put_resp.status_code, 200)
        self.assertEqual(put_resp.data["title"], "Updated")

        # archive note
        arch_resp = self.client.post(f"/api/notes/{note_id}/archive/")
        self.assertEqual(arch_resp.status_code, 200)
        self.assertTrue(arch_resp.data["is_archived"])

        # delete note
        del_resp = self.client.delete(f"/api/notes/{note_id}/")
        self.assertIn(del_resp.status_code, (200, 204))
