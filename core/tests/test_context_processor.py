from django.test import TestCase, override_settings


class ContextProcessorTests(TestCase):
    def test_global_ui_keys_present(self):
        resp = self.client.get('/')
        for key in [
            'SITE_NAME','APP_VERSION','ENV_LABEL','DEFAULT_THEME',
            'FEATURE_FLAGS','PENDING_INVITES_COUNT','ACTIVE_QUIZ_ATTEMPTS',
            'MAX_QUIZ_ATTEMPTS','BUILD_TIMESTAMP'
        ]:
            self.assertIn(key, resp.context)