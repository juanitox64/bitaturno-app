import json
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class MockupParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.screens = set()
        self.targets = set()
        self.references = []
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        if "data-screen" in attributes:
            self.screens.add(attributes["data-screen"])
        if "data-go" in attributes:
            self.targets.add(attributes["data-go"])
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.references.append(value)


class MockupStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (DOCS / "index.html").read_text(encoding="utf-8")
        cls.css = (DOCS / "css" / "styles.css").read_text(encoding="utf-8")
        cls.javascript = (DOCS / "js" / "app.js").read_text(encoding="utf-8")
        cls.service_worker = (DOCS / "service-worker.js").read_text(encoding="utf-8")
        cls.parser = MockupParser()
        cls.parser.feed(cls.html)

    def test_required_files_exist(self):
        required = [
            "index.html",
            ".nojekyll",
            "css/styles.css",
            "js/app.js",
            "manifest.webmanifest",
            "service-worker.js",
            "assets/icons/icon-192.svg",
            "assets/icons/icon-512.svg",
            "assets/images/evidencia-ficticia.svg",
        ]
        self.assertEqual([], [path for path in required if not (DOCS / path).is_file()])

    def test_all_seven_screens_are_present(self):
        expected = {"login", "jornada", "captura", "borradores", "completar", "resumen", "historico"}
        self.assertEqual(expected, self.parser.screens)

    def test_navigation_only_targets_existing_screens(self):
        self.assertTrue(self.parser.targets)
        self.assertEqual(set(), self.parser.targets - self.parser.screens)

    def test_bottom_navigation_is_hidden_on_initial_load(self):
        nav = [attrs for tag, attrs in self.parser.elements if tag == "nav" and attrs.get("id") == "bottom-nav"]
        self.assertEqual(1, len(nav))
        self.assertIn("hidden", nav[0])
        self.assertIn(".bottom-nav[hidden]", self.css)

    def test_no_external_frontend_dependencies(self):
        external = []
        for reference in self.parser.references:
            parsed = urlparse(reference)
            if parsed.scheme or parsed.netloc or reference.startswith("//"):
                external.append(reference)
        self.assertEqual([], external)

    def test_all_local_html_references_exist(self):
        missing = []
        for reference in self.parser.references:
            clean = reference.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            if not (DOCS / clean).is_file():
                missing.append(reference)
        self.assertEqual([], missing)

    def test_manifest_and_icons_are_valid(self):
        manifest = json.loads((DOCS / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual("./", manifest["start_url"])
        self.assertEqual("./", manifest["scope"])
        self.assertEqual("standalone", manifest["display"])
        self.assertEqual({"192x192", "512x512"}, {icon["sizes"] for icon in manifest["icons"]})
        for icon in manifest["icons"]:
            ET.parse(DOCS / icon["src"])

    def test_service_worker_caches_the_complete_shell(self):
        expected = [
            "./index.html",
            "./css/styles.css",
            "./js/app.js",
            "./manifest.webmanifest",
            "./assets/icons/icon-192.svg",
            "./assets/icons/icon-512.svg",
            "./assets/images/evidencia-ficticia.svg",
        ]
        for path in expected:
            self.assertIn(f'"{path}"', self.service_worker)
        self.assertIn('CACHE_NAME = "bitaturno-mockup-v2"', self.service_worker)

    def test_scope_is_explicit_in_visible_copy(self):
        self.assertIn("Prototipo navegable", self.html)
        self.assertIn("no corresponde a la aplicación móvil final", self.html)
        self.assertNotIn("inteligencia artificial", self.html.lower())
        self.assertIn("No se enviaron credenciales", self.javascript)


if __name__ == "__main__":
    unittest.main(verbosity=2)
