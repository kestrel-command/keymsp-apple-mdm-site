import base64, json, os, time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path('/Users/kestrel/.openclaw/workspace/tmp/keymsp-apple-mdm-page')
ASSETS = ROOT / 'assets'
ENV_PATH = Path('/Users/kestrel/.openclaw/workspace/.secrets/nano-banana.env')

api_key = None
for line in ENV_PATH.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    if k.strip() == 'NANO_BANANA_PRO_API_KEY':
        api_key = v.strip()
        break
if not api_key:
    raise SystemExit('Missing NANO_BANANA_PRO_API_KEY')

prompts = [
    {
        'name': 'hero',
        'prompt': 'Create a premium wide hero illustration for a managed IT services landing page about Apple Business Manager and mobile device management for SMBs. Show a clean modern business setting with one professional using a MacBook, an iPhone, and an iPad, while a subtle fleet-management dashboard appears in the environment. Style: polished editorial tech marketing, realistic but idealized, soft natural light, blue and graphite color palette, trustworthy, modern, uncluttered, no readable brand logos, no watermark, 16:9 composition.'
    },
    {
        'name': 'lifecycle',
        'prompt': 'Create a clean marketing illustration for an SMB IT services page showing the lifecycle management of Apple devices in a business. Include visual cues for onboarding a new employee, app deployment, security controls, lost device response, and offboarding. Devices should include a laptop, smartphone, and tablet in a modern minimalist business style. Use a premium enterprise-tech aesthetic, subtle blue gradient accents, highly usable composition for a website section, no logos, no watermark, 16:10 composition.'
    }
]

url = 'https://api.nanobanana.pro/v1/images/generations'
for item in prompts:
    payload = {
        'prompt': item['prompt'],
        'size': '1536x1024',
        'n': 1,
        'response_format': 'b64_json'
    }
    req = Request(url, data=json.dumps(payload).encode('utf-8'), headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }, method='POST')
    with urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    images = data.get('data') or []
    if not images:
        raise RuntimeError(f'No image data returned for {item["name"]}: {data}')
    b64 = images[0].get('b64_json')
    if not b64:
        raise RuntimeError(f'Missing b64_json for {item["name"]}: {data}')
    out = ASSETS / f'{item["name"]}.png'
    out.write_bytes(base64.b64decode(b64))
    print(f'WROTE {out}')
    time.sleep(1)
