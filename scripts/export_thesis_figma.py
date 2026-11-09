"""Export THESIS reference screens and source artwork without storing credentials."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

FILE_KEY = 'aFXQm7eAu32gXNeWt7WJVe'
ROOT = Path(__file__).resolve().parents[1]
FRAMES = {'navigation-hud': '2:1624', 'settings': '2:1669',
          'hazard-log': '2:1734', 'design-reference': '2:1787'}
ARTWORK = {'cpu': '2:1977', 'audio-lines': '2:1980',
           'triangle-alert': '2:1983', 'volume': '2:1986',
           'back': '2:1989', 'map-pin': '2:2004',
           'caution': '2:2010', 'safe': '2:2013', 'check': '2:1992'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token-env-file', type=Path, default=Path(
        'C:/Users/User/Documents/first_year_files/folder_for_jobs/KUWENTURO/kuwenturo/.env.local'))
    args = parser.parse_args()
    token = None
    for line in args.token_env_file.read_text(encoding='utf-8-sig').splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() == 'FIGMA_ACCESS_TOKEN':
            token = value.strip().strip('\"\'')
    if not token:
        raise SystemExit('FIGMA_ACCESS_TOKEN is missing from the private configuration.')

    def request(url, authenticated=False):
        headers = {'X-Figma-Token': token} if authenticated else {}
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            raise SystemExit(f'Figma export stopped: HTTP {error.code}. Retry later if rate limited.') from None

    def api(path):
        return json.loads(request('https://api.figma.com/v1/' + path, True))

    out = ROOT / 'qa/figma-source'
    out.mkdir(parents=True, exist_ok=True)
    source = api(f'files/{FILE_KEY}')
    comments = api(f'files/{FILE_KEY}/comments')
    for name, data in [('file.json', source), ('comments.json', comments)]:
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    nodes = {}

    def walk(node):
        nodes[node['id']] = node
        for child in node.get('children', []):
            walk(child)
    walk(source['document'])
    entries = []
    for category, mapping, scale in [('screens', FRAMES, 1), ('artwork', ARTWORK, 2)]:
        ids = urllib.parse.quote(','.join(mapping.values()))
        renders = api(f'images/{FILE_KEY}?ids={ids}&format=png&scale={scale}')
        for name, node_id in mapping.items():
            url = renders.get('images', {}).get(node_id)
            if not url:
                raise SystemExit(f'Missing render for node {node_id}.')
            path = out / category / f'{name}.png'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(request(url))
            with Image.open(path) as image:
                image.load()
                dimensions = image.size
            entries.append({'nodeId': node_id, 'name': nodes[node_id]['name'],
                            'path': path.relative_to(out).as_posix(), 'dimensions': dimensions,
                            'bounds': nodes[node_id].get('absoluteBoundingBox'),
                            'renderBounds': nodes[node_id].get('absoluteRenderBounds'),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    fills = api(f'files/{FILE_KEY}/images')['meta']['images']
    used_refs = {fill['imageRef'] for node in nodes.values() for fill in node.get('fills', [])
                 if fill.get('type') == 'IMAGE' and fill.get('imageRef')}
    for ref in sorted(used_refs):
        path = out / 'fills' / f'{ref}.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(request(fills[ref]))
        with Image.open(path) as image:
            image.load()
            dimensions = image.size
        entries.append({'imageRef': ref, 'path': path.relative_to(out).as_posix(),
                        'dimensions': dimensions, 'referenceOnly': True,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {'fileKey': FILE_KEY, 'version': source['version'],
                'lastModified': source['lastModified'], 'commentCount': len(comments['comments']),
                'assets': entries}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    cards = ''.join(f'<article><h2>{html.escape(e.get("name", "Original camera fill (reference only)"))}</h2>'
                    f'<p>{html.escape(e.get("nodeId", e.get("imageRef", "")))}</p>'
                    f'<a href="{e["path"]}"><img src="{e["path"]}" alt="{html.escape(e.get("name", "Reference image"))}"></a></article>'
                    for e in entries)
    (out / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>THESIS Figma references</title><style>body{background:#000;color:#fff;font:16px system-ui;'
        'padding:24px}main{display:flex;flex-wrap:wrap;gap:24px}article{width:360px;background:#121212;'
        'padding:16px;overflow-wrap:anywhere}img{max-width:100%;height:auto}h1{color:#ffd700}</style>'
        f'<h1>THESIS Figma references</h1><p>Version {html.escape(source["version"])} · '
        f'{len(comments["comments"])} comments. Static references; sample telemetry is not live.</p>'
        f'<main>{cards}</main></html>', encoding='utf-8')
    print(f'Exported {len(FRAMES)} frames, {len(ARTWORK)} artwork nodes, {len(used_refs)} original fills. Images decoded successfully.')


if __name__ == '__main__':
    main()
