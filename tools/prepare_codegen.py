"""Apply the Magic 2012 host-only worker backoff to locally generated C++.

No game function bodies are stored in this tool. A changed generator pattern
stops the build instead of silently omitting the worker fix.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def main():
    generated = ROOT / 'app/generated/default'
    for path in generated.glob('mtg12_recomp.*.cpp'):
        text = path.read_text(encoding='utf-8')
        match = re.search(r'(?:REX_FUNC|REX_FUNC_IMPL)\(sub_82A61E90\)', text)
        if not match:
            continue
        end = text.find('\n}', match.end())
        if end < 0:
            raise RuntimeError('Cannot locate the generated worker end')
        body = text[match.start():end]
        if 'mtg12_worker_idle();' in body:
            print('Worker backoff already prepared')
            return
        needle = 'if (cr6.eq) goto loc_82A61EE4;'
        # The first of these branches is the empty-ready poll. Later branches
        # belong to job processing and must stay unchanged.
        if body.count(needle) != 2:
            raise RuntimeError('Worker layout changed: expected two ready-loop branches')
        body = body.replace(needle, 'if (cr6.eq) { mtg12_worker_idle(); goto loc_82A61EE4; }', 1)
        text = text[:match.start()] + body + text[end:]
        text = 'extern "C" void mtg12_worker_idle();\n' + text
        path.write_text(text, encoding='utf-8')
        print('Worker backoff prepared:', path.name)
        return
    raise RuntimeError('Generated Magic 2012 worker was not found')


if __name__ == '__main__':
    main()
