import puppeteer from 'puppeteer-core';
import path from 'node:path';
import fs from 'node:fs';

const ARTIFACTS_DIR = 'C:\\Users\\user\\.gemini\\antigravity-ide\\brain\\901bfd8a-b29a-4b21-aa50-e6641d37868f';
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const TEST_PAGES = [
  { name: 'home', url: 'http://127.0.0.1:8000/' },
  { name: 'vehicles', url: 'http://127.0.0.1:8000/vehicles/' },
  { name: 'vehicle_detail', url: 'http://127.0.0.1:8000/vehicles/hyundai-creta-sx-o-15l-turbo-petrol-dct-2025/' },
  { name: 'products', url: 'http://127.0.0.1:8000/products/' },
  { name: 'services', url: 'http://127.0.0.1:8000/services/' },
  { name: 'customizer', url: 'http://127.0.0.1:8000/customizer/' }
];

async function runMobileAudit() {
  console.log('====================================================');
  console.log('   HEADLESS BROWSER MOBILE VIEWPORT AUDIT (390x844)');
  console.log('====================================================');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--window-size=390,844']
  });

  const page = await browser.newPage();
  await page.setViewport({
    width: 390,
    height: 844,
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true
  });

  const report = [];

  for (const p of TEST_PAGES) {
    console.log(`\nNavigating to ${p.name}: ${p.url}`);
    try {
      const response = await page.goto(p.url, { waitUntil: 'networkidle2', timeout: 30000 });
      const status = response ? response.status() : 'unknown';
      console.log(`  HTTP Status: ${status}`);

      // 1. Check Horizontal Overflow (scrollWidth vs clientWidth)
      const overflow = await page.evaluate(() => {
        const docWidth = document.documentElement.clientWidth;
        const scrollWidth = document.documentElement.scrollWidth;
        const bodyScrollWidth = document.body.scrollWidth;
        const hasHorizontalScroll = scrollWidth > docWidth || bodyScrollWidth > docWidth;
        
        // Find elements that might be causing overflow
        const overflowElements = [];
        document.querySelectorAll('*').forEach(el => {
          const rect = el.getBoundingClientRect();
          if (rect.right > docWidth + 2) {
            overflowElements.push({
              tag: el.tagName,
              id: el.id,
              className: (el.className || '').toString().slice(0, 50),
              right: Math.round(rect.right),
              docWidth
            });
          }
        });
        
        return {
          docWidth,
          scrollWidth,
          bodyScrollWidth,
          hasHorizontalScroll,
          overflowCount: overflowElements.length,
          sampleOverflows: overflowElements.slice(0, 3)
        };
      });

      console.log(`  Viewport Width: ${overflow.docWidth}px, Scroll Width: ${overflow.scrollWidth}px`);
      console.log(`  Horizontal Overflow: ${overflow.hasHorizontalScroll ? 'FAILED' : 'PERFECT (0px overflow)'}`);

      // 2. Scan for AI Artifacts / Forbidden Badges
      const forbiddenAudit = await page.evaluate(() => {
        const text = document.body.innerText;
        const forbiddenTerms = ['REAL PHOTO', '3D STUDIO READY', 'REAL PHOTO • VALID ASSET'];
        const foundBadges = [];
        
        // Check for specific overlay elements
        document.querySelectorAll('.badge, .badge-tag, span, div').forEach(el => {
          const t = (el.innerText || '').trim().toUpperCase();
          if (t === 'REAL PHOTO' || t === '3D STUDIO READY' || t.includes('REAL PHOTO •')) {
            foundBadges.push({
              tag: el.tagName,
              class: el.className,
              text: t
            });
          }
        });

        return {
          foundBadges,
          hasForbiddenBadges: foundBadges.length > 0
        };
      });

      console.log(`  Forbidden Overlay Badges: ${forbiddenAudit.foundBadges.length === 0 ? 'CLEAN (0 found)' : 'FOUND: ' + JSON.stringify(forbiddenAudit.foundBadges)}`);

      // 3. Scan Price Formatting
      const priceAudit = await page.evaluate(() => {
        const priceMatches = [];
        // Look for elements with prices
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walker.nextNode()) {
          const val = node.nodeValue.trim();
          if (val.startsWith('₹') && val.length > 1) {
            priceMatches.push(val);
          }
        }
        return priceMatches.slice(0, 5);
      });
      console.log(`  Sample Formatted Prices: ${priceAudit.join(' | ')}`);

      // 4. Test Navbar Hamburger on Home
      if (p.name === 'home') {
        const hamburgerTest = await page.evaluate(async () => {
          const btn = document.querySelector('.cd-hamburger-btn');
          const collapse = document.querySelector('#navbarContent');
          if (!btn || !collapse) return { exists: false };
          
          btn.click();
          await new Promise(r => setTimeout(r, 400));
          const isExpanded = collapse.classList.contains('show');
          
          return {
            exists: true,
            isExpanded
          };
        });
        console.log(`  Navbar Hamburger Toggle: ${hamburgerTest.exists && hamburgerTest.isExpanded ? 'WORKING (Expanded successfully)' : 'Check hamburger'}`);
      }

      // 5. Capture Mobile Screenshot
      const screenshotPath = path.join(ARTIFACTS_DIR, `mobile_${p.name}_390x844.png`);
      await page.screenshot({ path: screenshotPath, fullPage: false });
      console.log(`  Screenshot saved: ${screenshotPath}`);

      report.push({
        page: p.name,
        status,
        overflow: overflow.hasHorizontalScroll ? 'FAIL' : 'PASS',
        forbiddenBadges: forbiddenAudit.foundBadges.length,
        prices: priceAudit,
        screenshot: screenshotPath
      });

    } catch (err) {
      console.error(`  Error auditing ${p.name}:`, err.message);
    }
  }

  await browser.close();

  console.log('\n====================================================');
  console.log('   MOBILE AUDIT SUMMARY');
  console.log('====================================================');
  console.table(report);
  console.log('\nAll tests complete.');
}

runMobileAudit().catch(err => {
  console.error('Fatal audit error:', err);
  process.exit(1);
});
