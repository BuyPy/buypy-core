from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from djoser.utils import encode_uid
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class TestDjoserEndpoints(APITestCase):
    """Covers registration, activation, JWT, profile, password & username flows."""

    def setUp(self):
        self.client = APIClient()
        self.password = "SuperSecret123!"
        self.user = User.objects.create_user(
            email="tester@mail.com",
            password=self.password,
            is_active=True,
        )

    # ---------- Helpers ----------
    def _jwt_pair(self, email=None, password=None):
        """Return (access, refresh) pair from /auth/jwt/create/."""
        data = {
            "email": email or self.user.email,
            "password": password or self.password,
        }
        res = self.client.post("/auth/jwt/create/", data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data["access"], res.data["refresh"]

    def _auth(self):
        """Shortcut – authenticate subsequent requests with a fresh access token."""
        access, _ = self._jwt_pair()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # ---------- Registration ----------
    def test_register_user(self):
        payload = {
            "email": "new@mail.com",
            "password": "NewPassw0rd!",
        }
        res = self.client.post("/auth/users/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())

    # ---------- Activation ----------
    def test_activate_user(self):
        usr = User.objects.create_user(
            email="inactive@mail.com",
            password="TempPass123",
            is_active=False,
        )
        uid = encode_uid(usr.pk)
        token = default_token_generator.make_token(usr)
        res = self.client.post("/auth/users/activation/", {"uid": uid, "token": token})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        usr.refresh_from_db()
        self.assertTrue(usr.is_active)

    def test_activate_in_activated_user(self):
        usr = User.objects.create_user(
            email="inactive@mail.com",
            password="TempPass123",
            is_active=True,
        )
        uid = encode_uid(usr.pk)
        token = default_token_generator.make_token(usr)
        res = self.client.post("/auth/users/activation/", {"uid": uid, "token": token})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        usr.refresh_from_db()
        self.assertTrue(usr.is_active)

    def test_resend_activation(self):
        usr = User.objects.create_user(
            email="again@mail.com",
            password="TempPass123",
            is_active=False,
        )
        res = self.client.post("/auth/users/resend_activation/", {"email": usr.email})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    # ---------- JWT ----------
    def test_jwt_refresh_and_verify(self):
        access, refresh = self._jwt_pair()
        res_refresh = self.client.post("/auth/jwt/refresh/", {"refresh": refresh})
        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)
        new_access = res_refresh.data["access"]
        res_verify = self.client.post("/auth/jwt/verify/", {"token": new_access})
        self.assertEqual(res_verify.status_code, status.HTTP_200_OK)

    # ---------- Current user ----------
    def test_get_me(self):
        self._auth()
        res_get = self.client.get("/auth/users/me/")
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data["email"], self.user.email)
        self.assertEqual(res_get.data["id"], str(self.user.id))

    def test_get_me_no_auth(self):
        res_get = self.client.get("/auth/users/me/")
        self.assertEqual(res_get.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- Password handling ----------
    def test_set_password(self):
        self._auth()
        res = self.client.post(
            "/auth/users/set_password/",
            {
                "current_password": self.password,
                "new_password": "BrandNewPass456!",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # login with new pass
        self._jwt_pair(password="BrandNewPass456!")

    def test_reset_password_flow(self):
        # request reset
        res_req = self.client.post(
            "/auth/users/reset_password/", {"email": self.user.email}
        )
        self.assertEqual(res_req.status_code, status.HTTP_204_NO_CONTENT)
        # confirm reset
        uid = encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        res_conf = self.client.post(
            "/auth/users/reset_password_confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password": "ResetPass789!",
            },
        )
        self.assertEqual(res_conf.status_code, status.HTTP_204_NO_CONTENT)
        # login with new pass
        self._jwt_pair(password="ResetPass789!")

    def test_reset_password_flow_no_auth(self):
        res_req = self.client.post(
            "/auth/users/reset_password/", {"email": self.user.email}
        )
        self.assertEqual(res_req.status_code, status.HTTP_204_NO_CONTENT)
        uid = encode_uid(self.user.pk)
        token = "ffsfsgsfwrewq"
        res_conf = self.client.post(
            "/auth/users/reset_password_confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password": "ResetPass789!",
            },
        )
        self.assertEqual(res_conf.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- Username handling ----------
    def test_set_username(self):
        self._auth()
        res = self.client.post(
            "/auth/users/set_username/",
            {
                "current_password": self.password,
                "new_username": "freshname",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, None)

    def test_reset_username_flow(self):
        res_req = self.client.post(
            "/auth/users/reset_username/", {"email": self.user.email}
        )
        self.assertEqual(res_req.status_code, status.HTTP_401_UNAUTHORIZED)
        self._auth()
        res_req = self.client.post(
            "/auth/users/reset_username/", {"email": self.user.email}
        )
        self.assertEqual(res_req.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        uid = encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        res_conf = self.client.post(
            "/auth/users/reset_username_confirm/",
            {
                "uid": uid,
                "token": token,
                "new_username": "confirmname",
            },
        )
        self.assertEqual(res_conf.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, None)
