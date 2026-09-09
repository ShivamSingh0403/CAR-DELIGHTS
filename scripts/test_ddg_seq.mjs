async function getDdgImages(query) {
  try {
    const url = 'https://duckduckgo.com/?q=' + encodeURIComponent(query + ' automotive luxury dark') + '&iar=images&iax=images&ia=images';
    const res1 = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      },
      signal: AbortSignal.timeout(8000)
    });
    const html = await res1.text();
    const vqdMatch = html.match(/vqd=([\"']?)([\d-]+)\1/) || html.match(/vqd=([0-9-]+)/);
    if (!vqdMatch) return [];
    const vqd = vqdMatch[2] || vqdMatch[1];
    const apiUrl = `https://duckduckgo.com/i.js?l=us-en&o=json&q=${encodeURIComponent(query + ' automotive luxury dark')}&vqd=${vqd}&f=,,,&p=1`;
    const res2 = await fetch(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://duckduckgo.com/'
      },
      signal: AbortSignal.timeout(8000)
    });
    const data = await res2.json();
    return (data.results || []).map(r => r.image).filter(u => u && u.startsWith('http') && !u.endsWith('.svg') && !u.endsWith('.gif'));
  } catch (e) {
    return [];
  }
}

async function main() {
  const queries = [
    'Express Foam Wash & Vacuum',
    'Paintless Dent Repair',
    'Stage 3 Concours Mirror Finish Detailing',
    'Borbet Wheels 17" Matte Black Sport Monoblock Rims',
    'GT Carbon Flap'
  ];

  for (const q of queries) {
    const start = Date.now();
    const urls = await getDdgImages(q);
    console.log(`Query "${q}" returned ${urls.length} images in ${Date.now() - start}ms. First: ${urls[0]}`);
  }
}

main().catch(console.error);
