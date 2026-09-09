async function debugQuery(q) {
  const searchUrl = 'https://duckduckgo.com/?q=' + encodeURIComponent(q) + '&iar=images&iax=images&ia=images';
  const tokenRes = await fetch(searchUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
  });
  const html = await tokenRes.text();
  const vqdMatch = html.match(/vqd=([\"']?)([\d-]+)\1/) || html.match(/vqd=([0-9-]+)/);
  console.log('vqd match:', vqdMatch ? vqdMatch[2] || vqdMatch[1] : null);
  if (!vqdMatch) return;
  const vqd = vqdMatch[2] || vqdMatch[1];
  const apiUrl = `https://duckduckgo.com/i.js?l=us-en&o=json&q=${encodeURIComponent(q)}&vqd=${vqd}&f=,,,&p=1`;
  const imgRes = await fetch(apiUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      'Referer': 'https://duckduckgo.com/'
    }
  });
  const data = await imgRes.json();
  console.log('Results count:', data.results?.length);
  for (let i = 0; i < Math.min(5, data.results?.length || 0); i++) {
    const item = data.results[i];
    console.log(`\nCandidate ${i}: ${item.image}`);
    try {
      const res = await fetch(item.image, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
          'Accept': 'image/*,*/*'
        },
        signal: AbortSignal.timeout(5000)
      });
      console.log('  Status:', res.status, 'Content-Type:', res.headers.get('content-type'));
    } catch (e) {
      console.log('  Fetch error:', e.message);
    }
  }
}

debugQuery('Deluxe Hydrophobic Foam Wash Car Detailing workshop detailing dark');
