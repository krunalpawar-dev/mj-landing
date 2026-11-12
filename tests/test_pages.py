"""Validate the generated MJ DYNAMIC static site artifacts."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ''
ORIGIN = 'http://mj-dynamic.test'

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()
        self.canonical = None
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if 'id' in attrs: self.ids.add(attrs['id'])
        for attr in ('href', 'src', 'action'):
            if attrs.get(attr): self.urls.append(attrs[attr])
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical = attrs['href']

class PagesTests(unittest.TestCase):
    def test_all_public_pages_and_links(self):
        sitemap = ET.parse(ROOT / 'sitemap.xml')
        urls = [el.text for el in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(len(urls), 37)
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(url.startswith(ORIGIN + BASE + '/'))
                self.assertTrue(url.endswith('/'))
                relative = urlsplit(url).path.removeprefix(BASE).strip('/')
                path = ROOT / relative / 'index.html'
                html = path.read_text(encoding='utf-8')
                self.assertNotIn('<?php', html)
                self.assertNotIn('portfolio.test', html)
                self.assertNotIn('name="csrf"', html)
                self.assertNotIn('Run locally', html)
                page = PageParser(); page.feed(html)
                self.assertEqual(page.h1, 1)
                self.assertEqual(page.canonical, url)
                json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html).group(1))
                for target in page.urls:
                    parsed = urlsplit(target)
                    if parsed.scheme or parsed.netloc: continue
                    if target.startswith('#'):
                        self.assertIn(parsed.fragment, page.ids)
                        continue
                    file = (path.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(file == ROOT or ROOT in file.parents, target)
                    if file.is_dir(): file /= 'index.html'
                    self.assertTrue(file.is_file(), target)
        self.assertTrue((ROOT / '.nojekyll').is_file())
        self.assertTrue((ROOT / '404.html').is_file())

    def test_project_case_studies_are_published(self):
        import json
        content = json.loads((ROOT / 'app/content.json').read_text(encoding='utf-8'))
        self.assertEqual(len(content['projects']), 11)
        project = content['projects'][0]
        self.assertEqual(len(project['features']), 12)
        self.assertEqual(project['short'], 'MedoraOps')
        self.assertTrue(project['concept'])
        self.assertEqual(len(project['screenshots']), 3)
        self.assertIn('original portfolio materials', project['contribution'])
        treeva = content['projects'][1]
        self.assertEqual(treeva['slug'], 'nexacare-clinic-operations-platform')
        self.assertEqual(treeva['short'], 'NexaCare')
        self.assertTrue(treeva['concept'])
        self.assertEqual(sum(f.startswith('Website: ') for f in treeva['features']), 4)
        self.assertEqual(sum(f.startswith('Admin panel: ') for f in treeva['features']), 8)
        self.assertIn('original portfolio materials', treeva['contribution'])
        self.assertTrue(all('/nexacare/' in shot['src'] for shot in treeva['screenshots']))
        page = (ROOT / 'projects' / treeva['slug'] / 'index.html').read_text(encoding='utf-8')
        self.assertIn('Public website features', page)
        self.assertIn('Admin panel features', page)
        expected = {
            'finserv-crm-business-management-platform': 3,
            'ds-shoppy-ecommerce-rewards-platform': 3,
            'electronics-ecommerce-storefront': 3,
            'kakubaa-student-support-website': 3,
            'sterile-aircare-solutions-corporate-website': 3,
        }
        for slug, screenshot_count in expected.items():
            project = next(p for p in content['projects'] if p['slug'] == slug)
            self.assertEqual(len(project['screenshots']), screenshot_count)
            self.assertTrue((ROOT / 'projects' / slug / 'index.html').is_file())
        concepts = [p for p in content['projects'] if p.get('concept')]
        self.assertEqual(len(concepts), 6)
        for project in concepts:
            self.assertGreaterEqual(len(project['screenshots']), 1)
            for screenshot in project['screenshots']:
                self.assertEqual(screenshot['width'], 1672)
                self.assertTrue((ROOT / screenshot['src'].lstrip('/')).is_file())
            page = (ROOT / 'projects' / project['slug'] / 'index.html').read_text(encoding='utf-8')
            self.assertIn('CONCEPT PROJECT', page)
            self.assertIn('not presented as commissioned client work', page)
        expected_order = [
            'nexacare-clinic-operations-platform',
            'finserv-crm-business-management-platform',
            'medoraops-pharmacy-operations-platform',
            'ds-shoppy-ecommerce-rewards-platform',
            'sterile-aircare-solutions-corporate-website',
            'kakubaa-student-support-website',
            'electronics-ecommerce-storefront',
            'smartstock-multi-warehouse-management-concept',
            'peopleflow-hrms-payroll-concept',
            'staypilot-property-management-saas-concept',
            'tradehub-b2b-dealer-portal-concept',
        ]
        listing = (ROOT / 'projects' / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(sorted(expected_order, key=listing.index), expected_order)
        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        for slug in expected_order[:6]:
            self.assertIn(f'href="projects/{slug}/"', home)
        self.assertNotIn(f'href="projects/{expected_order[6]}/"', home)
        self.assertNotRegex(home, r'href="[^"]*/index\.html')
        self.assertNotRegex(listing, r'href="[^"]*/index\.html')
        for slug in ['education-management-saas',
                     'crm-business-management-platform', 'hrms-payroll-system', 'warehouse-management-system']:
            for prefix in ['', 'portfolio/']:
                self.assertFalse((ROOT / f'{prefix}projects/{slug}/index.html').exists())

    def test_previous_project_urls_redirect_to_root(self):
        for route in ['', 'about', 'contact', 'projects/medoraops-pharmacy-operations-platform']:
            html = (ROOT / 'portfolio' / route / 'index.html').read_text(encoding='utf-8')
            target = ORIGIN + '/' + (route + '/' if route else '')
            self.assertIn('http-equiv="refresh"', html)
            self.assertIn('url=' + target, html)
            self.assertIn('rel="canonical" href="' + target + '"', html)

    def test_contact_uses_existing_working_service(self):
        html = (ROOT / 'contact/index.html').read_text(encoding='utf-8')
        self.assertIn('action="https://formspree.io/f/xdkeodjk"', html)
        self.assertIn('name="_gotcha"', html)
        self.assertNotIn('name="csrf"', html)
        self.assertIn('mailto:kmpawar0004@gmail.com', html)
        privacy = (ROOT / 'privacy/index.html').read_text(encoding='utf-8')
        self.assertIn('Formspree', privacy)
        self.assertNotIn('Enquiries are stored in a private application database.', privacy)

if __name__ == '__main__': unittest.main(verbosity=2)
