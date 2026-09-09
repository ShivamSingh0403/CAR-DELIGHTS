async function testWikimedia(query) {
  const url = `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=${encodeURIComponent(query + ' filetype:bitmap')}&gsrnamespace=6&prop=imageinfo&iiprop=url|size|mime&format=json&gsrlimit=10`;
  const res = await fetch(url, { headers: { 'User-Agent': 'CarDelightsBot/2.0 (contact@cardelights.com)' } });
  const data = await res.json();
  if (!data.query || !data.query.pages) {
    console.log(`Wikimedia for "${query}": 0 results`);
    return [];
  }
  const pages = Object.values(data.query.pages);
  const images = [];
  for (const p of pages) {
    const info = p.imageinfo?.[0];
    if (!info) continue;
    if (info.mime !== 'image/jpeg' && info.mime !== 'image/png') continue;
    if (info.width < 500 || info.height < 300) continue;
    images.push({ title: p.title, url: info.url, width: info.width, height: info.height });
  }
  console.log(`Wikimedia for "${query}": ${images.length} valid bitmap photos`);
  if (images.length > 0) console.log('  Sample:', images[0].title, images[0].url);
  return images;
}

async function testBing(query) {
  try {
    const url = `https://www.bing.com/images/search?q=${encodeURIComponent(query)}&form=HDRSC2&first=1`;
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html'
      }
    });
    const html = await res.text();
    const matches = [...html.matchAll(/murl&quot;:&quot;(https?:\/\/[^&]+)&quot;/g)].map(m => m[1]);
    console.log(`Bing for "${query}": ${matches.length} images found!`);
    if (matches.length > 0) console.log('  Sample:', matches[0]);
    return matches;
  } catch (e) {
    console.log('Bing error:', e.message);
    return [];
  }
}

async function main() {
  console.log('--- TESTING BING SCRAPE ---');
  await testBing('Deluxe Hydrophobic Foam Wash detailing');
  await testBing('Paintless Dent Repair luxury car');
  await testBing('GT Carbon Flap');
  await testBing('Hyundai Creta dark automotive');

  console.log('\n--- TESTING WIKIMEDIA ---');
  await testWikimedia('car wash foam');
  await testWikimedia('car dent repair');
  await testWikimedia('carbon spoiler');
}

main().catch(console.error);
