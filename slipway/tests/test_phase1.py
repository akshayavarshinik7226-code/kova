import unittest

from slipway.security import hash_password, verify_password
from slipway.users import ValidationError, create_user
from slipway.db import connect

from .base import ADMIN, STUDENT, AppTestCase


class SecurityTests(unittest.TestCase):
    def test_hash_roundtrip(self):
        h = hash_password("a-long-password-1")
        self.assertTrue(verify_password("a-long-password-1", h))
        self.assertFalse(verify_password("wrong", h))
        self.assertNotEqual(h, hash_password("a-long-password-1"))  # unique salt

    def test_tampered_or_malformed_hash_rejected(self):
        self.assertFalse(verify_password("x", "garbage"))
        self.assertFalse(verify_password("x", "md5$1$2$3$aa$bb"))


class HealthAndPages(AppTestCase):
    def test_health_ok_without_auth(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["database"])

    def test_login_page_is_branded(self):
        r = self.client.get("/login")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"KOVA", r.data)

    def test_home_redirects_when_signed_out(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/login"))

    def test_security_headers(self):
        r = self.client.get("/login")
        self.assertEqual(r.headers["X-Frame-Options"], "DENY")
        self.assertIn("script-src 'self'", r.headers["Content-Security-Policy"])
        self.assertNotIn("<script>", r.get_data(as_text=True).replace("<script src", ""))  # no inline scripts

    def test_static_assets_served(self):
        for p in ("css/tokens.css", "css/app.css", "js/api.js", "js/login.js", "js/app.js"):
            r = self.client.get("/static/" + p)
            r.close()
            self.assertEqual(r.status_code, 200, p)


class AuthTests(AppTestCase):
    def test_me_anonymous_gives_csrf_and_no_user(self):
        data = self.client.get("/api/auth/me").get_json()
        self.assertIsNone(data["user"])
        self.assertTrue(data["csrf"])

    def test_post_without_csrf_rejected(self):
        r = self.client.post("/api/auth/login", json={"email": ADMIN[0], "password": ADMIN[2]})
        self.assertEqual(r.status_code, 403)

    def test_post_with_wrong_csrf_rejected(self):
        self.csrf()
        r = self.post("/api/auth/login", {"email": ADMIN[0], "password": ADMIN[2]}, token="nope")
        self.assertEqual(r.status_code, 403)

    def test_login_success_and_session(self):
        r = self.login(ADMIN[0], ADMIN[2])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["user"]["role"], "admin")
        self.assertNotIn("password_hash", r.get_data(as_text=True))
        me = self.client.get("/api/auth/me").get_json()
        self.assertEqual(me["user"]["email"], ADMIN[0])

    def test_email_is_case_insensitive(self):
        self.assertEqual(self.login("ADMIN@Example.test", ADMIN[2]).status_code, 200)

    def test_wrong_password_and_unknown_email_look_identical(self):
        a = self.login(ADMIN[0], "wrong-password-xx")
        b = self.login("nobody@example.test", "wrong-password-xx")
        self.assertEqual(a.status_code, 401)
        self.assertEqual(b.status_code, 401)
        self.assertEqual(a.get_json(), b.get_json())

    def test_lockout_after_repeated_failures(self):
        for _ in range(5):
            self.assertEqual(self.login(STUDENT[0], "bad-password-xx").status_code, 401)
        r = self.login(STUDENT[0], STUDENT[2])  # even the right password is blocked while locked
        self.assertEqual(r.status_code, 429)

    def test_inactive_user_cannot_login(self):
        conn = connect(self.app.config["DATABASE"])
        conn.execute("UPDATE users SET is_active=0 WHERE id=?", (self.student_id,))
        conn.commit(); conn.close()
        self.assertEqual(self.login(STUDENT[0], STUDENT[2]).status_code, 401)

    def test_logout_clears_session(self):
        self.login(ADMIN[0], ADMIN[2])
        self.assertEqual(self.post("/api/auth/logout").status_code, 200)
        self.assertIsNone(self.client.get("/api/auth/me").get_json()["user"])

    def test_session_fixation_csrf_rotates_on_login(self):
        before = self.csrf()
        after = self.login(ADMIN[0], ADMIN[2]).get_json()["csrf"]
        self.assertNotEqual(before, after)

    def test_login_events_are_audited(self):
        self.login(ADMIN[0], "wrong-password-xx")
        self.login(ADMIN[0], ADMIN[2])
        conn = connect(self.app.config["DATABASE"])
        actions = [r["action"] for r in conn.execute("SELECT action FROM audit_log ORDER BY id")]
        conn.close()
        self.assertEqual(actions, ["login.failed", "login.ok"])


class StatusTests(AppTestCase):
    def test_status_requires_login(self):
        self.assertEqual(self.client.get("/api/platform/status").status_code, 401)

    def test_status_reports_coolify_not_configured(self):
        self.login(STUDENT[0], STUDENT[2])
        data = self.client.get("/api/platform/status").get_json()
        self.assertEqual(data["coolify"]["state"], "not_configured")
        self.assertIsNone(data["users"])  # students don't see user counts

    def test_status_admin_sees_user_count_and_never_the_token(self):
        self.app.config.update(COOLIFY_URL="https://coolify.example.test", COOLIFY_TOKEN="super-secret-token")
        self.login(ADMIN[0], ADMIN[2])
        r = self.client.get("/api/platform/status")
        self.assertEqual(r.get_json()["users"], 2)
        self.assertEqual(r.get_json()["coolify"]["host"], "coolify.example.test")
        self.assertNotIn("super-secret-token", r.get_data(as_text=True))

    def test_authenticated_home_renders_shell(self):
        self.login(ADMIN[0], ADMIN[2])
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Overview", r.data)


class UserCreationTests(AppTestCase):
    def test_validation(self):
        conn = connect(self.app.config["DATABASE"])
        for args in [("bad", "N", "long-enough-pass1"), ("a@b.co", "", "long-enough-pass1"),
                     ("a@b.co", "N", "short"), (STUDENT[0], "Dup", "long-enough-pass1")]:
            with self.assertRaises(ValidationError):
                create_user(conn, *args)
        conn.close()


if __name__ == "__main__":
    unittest.main()
