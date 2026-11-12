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
        self.assertEqual(len(urls), 38)
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
        self.assertFalse((ROOT / 'technologies').exists())
        self.assertFalse((ROOT / 'portfolio' / 'technologies').exists())

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
            'medoraops-pharmacy-operations-platform',
            'nexacare-clinic-operations-platform',
            'smartstock-multi-warehouse-management-concept',
            'tradehub-b2b-dealer-portal-concept',
            'peopleflow-hrms-payroll-concept',
            'staypilot-property-management-saas-concept',
            'finserv-crm-business-management-platform',
            'ds-shoppy-ecommerce-rewards-platform',
            'sterile-aircare-solutions-corporate-website',
            'electronics-ecommerce-storefront',
            'kakubaa-student-support-website',
        ]
        listing = (ROOT / 'projects' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero projects-page-hero"', listing)
        self.assertIn('id="projects-hero-title"', listing)
        self.assertTrue((ROOT / 'assets/img/mj-dynamic-projects-hero.webp').exists())
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

    def test_finserv_project_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/portfolio/crm/finserv-crm-project-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'projects/finserv-crm-business-management-platform/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero project-detail-hero"', html)
        self.assertIn('src="../../assets/img/portfolio/crm/finserv-crm-project-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="project-hero-title"', html)
        self.assertIn('src="../../assets/img/portfolio/crm/ERP1.png"', html)

    def test_electronics_project_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/portfolio/e-commerce/electronics-ecommerce-storefront-hero.jpg'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'projects/electronics-ecommerce-storefront/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero project-detail-hero"', html)
        self.assertIn('src="../../assets/img/portfolio/e-commerce/electronics-ecommerce-storefront-hero.jpg"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="project-hero-title"', html)
        self.assertIn('src="../../assets/img/portfolio/e-commerce/E1.png"', html)

    def test_contact_uses_existing_working_service(self):
        html = (ROOT / 'contact/index.html').read_text(encoding='utf-8')
        self.assertIn('action="https://formspree.io/f/xdkeodjk"', html)
        self.assertIn('name="_gotcha"', html)
        self.assertNotIn('name="csrf"', html)
        self.assertIn('mailto:mjdynamic.helpdesk@gmail.com', html)
        self.assertIn('mj-dynamic-contact-collaboration-hero.webp', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertTrue((ROOT / 'assets/img/mj-dynamic-contact-collaboration-hero.webp').exists())
        privacy = (ROOT / 'privacy/index.html').read_text(encoding='utf-8')
        self.assertIn('Formspree', privacy)
        self.assertNotIn('Enquiries are stored in a private application database.', privacy)

    def test_company_platform_links_are_in_the_shared_footer(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('href="https://learn.mjdynamic.in/"', html)
        self.assertIn('>MJ DYNAMIC Learn <', html)
        self.assertIn('href="https://tools.mjdynamic.in/"', html)
        self.assertIn('>ToolKitHub <', html)

    def test_custom_web_application_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/custom-web-application-development-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/custom-web-application-development/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/custom-web-application-development-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_hrms_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/hrms-development-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/hrms-development/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/hrms-development-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_api_integration_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/api-development-integration-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/api-development-integration/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/api-development-integration-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_ds_shoppy_project_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/ds-shoppy-ecommerce-rewards-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'projects/ds-shoppy-ecommerce-rewards-platform/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero project-detail-hero"', html)
        self.assertIn('src="../../assets/img/ds-shoppy-ecommerce-rewards-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="project-hero-title"', html)

    def test_saas_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/saas-development-hero.jpg'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/saas-development/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/saas-development-hero.jpg"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_healthcare_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/healthcare-management-system-development-hero.jpg'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/healthcare-management-system-development/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/healthcare-management-system-development-hero.jpg"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_inventory_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/inventory-management-system-development-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/inventory-management-system-development/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/inventory-management-system-development-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_admin_panel_service_has_an_optimized_hero(self):
        image = ROOT / 'assets/img/admin-panel-development-hero.webp'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'services/admin-panel-development/index.html').read_text(encoding='utf-8')
        self.assertIn('class="blog-page-hero service-page-hero"', html)
        self.assertIn('src="../../assets/img/admin-panel-development-hero.webp"', html)
        self.assertIn('width="1672" height="941"', html)
        self.assertIn('id="service-hero-title"', html)

    def test_homepage_has_an_optimized_hero_image(self):
        image = ROOT / 'assets/img/mj-dynamic-business-software-hero.jpg'
        self.assertTrue(image.is_file())
        self.assertLess(image.stat().st_size, 500 * 1024)
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('class="hero-visual"', html)
        self.assertIn('src="assets/img/mj-dynamic-business-software-hero.jpg"', html)
        self.assertIn('fetchpriority="high"', html)
        self.assertIn('<h1>Less manual work.<br>More control.<br><span>Software built around you.</span></h1>', html)
        css = (ROOT / 'assets/css/business.css').read_text(encoding='utf-8')
        self.assertIn('.hero { padding-block: 48px 68px; }', css)

    def test_every_blog_post_has_an_optimized_seo_image(self):
        content = json.loads((ROOT / 'app/content.json').read_text(encoding='utf-8'))
        self.assertEqual(len(content['posts']), 8)
        for post in content['posts']:
            with self.subTest(post=post['slug']):
                self.assertEqual((post['image_width'], post['image_height']), (1672, 941))
                self.assertGreaterEqual(len(post['image_alt']), 50)
                image = ROOT / post['image'].lstrip('/')
                self.assertTrue(image.is_file())
                self.assertLess(image.stat().st_size, 500 * 1024)
                html = (ROOT / 'blog' / post['slug'] / 'index.html').read_text(encoding='utf-8')
                self.assertIn(f'alt="{post["image_alt"]}"', html)
                self.assertIn('property="og:image"', html)
                self.assertIn('name="twitter:image"', html)

    def test_company_product_articles_link_to_their_platforms(self):
        expected = {
            'free-online-tools-for-everyday-work': 'https://tools.mjdynamic.in/',
            'practical-webinars-with-mj-dynamic-learn': 'https://learn.mjdynamic.in/',
        }
        for slug, target in expected.items():
            with self.subTest(slug=slug):
                html = (ROOT / 'blog' / slug / 'index.html').read_text(encoding='utf-8')
                self.assertIn(f'href="{target}"', html)

if __name__ == '__main__': unittest.main(verbosity=2)
