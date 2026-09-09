async function testDDG(query) {
  try {
    const url = 'https://duckduckgo.com/?q=' + encodeURIComponent(query) + '&iar=images&iax=images&ia=images';
    const res1 = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    });
    const html = await res1.text();
    const vqdMatch = html.match(/vqd=([\"']?)([\d-]+)\1/) || html.match(/vqd=([0-9-]+)/);
    if (!vqdMatch) {
      console.log('No VQD for', query);
      return;
    }
    const vqd = vqdMatch[2] || vqdMatch[1];
    const apiUrl = `https://duckduckgo.com/i.js?l=us-en&o=json&q=${encodeURIComponent(query)}&vqd=${vqd}&f=,,,&p=1`;
    const res2 = await fetch(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://duckduckgo.com/'
      }
    });
    const data = await res2.json();
    console.log(`DDG results for "${query}": ${data.results?.length} results`);
    if (data.results?.length > 0) {
      console.log('First result image URL:', data.results[0].image);
      console.log('First result title:', data.results[0].title);
    }
  } catch (e) {
    console.error('DDG error:', e.message);
  }
}

async function main() {
  await testDDG('Paintless Dent Repair automotive luxury');
  await testDDG('GT Carbon Flap car');
  await testDDG('Hyundai Creta dark automotive 85mm');
  await testDDG('Express Foam Wash & Vacuum luxury car');
}

main().catch(console.error);
