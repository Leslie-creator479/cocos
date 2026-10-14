"""아티팩트용으로 만든 페이지(<title>·<style>로 시작하는 본문 조각)를 홈페이지에 올릴 완전한 HTML 문서로 감싼다.
아티팩트는 게시할 때 서버가 겉틀을 붙여 줬지만, 홈페이지는 파일 그대로 보여 주므로 직접 붙여야 한다.
이미 <!doctype 으로 시작하면 그대로 둔다.

사용법: python3 _tools/wrap.py 원본.html 저장할경로/index.html [--noindex]
"""
import os, sys

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '{noindex}'
        '<style>:root{{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);'
        'padding-bottom:env(safe-area-inset-bottom,0px)}}html{{scroll-padding-top:env(safe-area-inset-top,0px)}}'
        'body{{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#faf9f5;color:#141413}}'
        'img{{max-width:100%}}[hidden]:not([hidden=until-found i]){{display:none!important}}</style></head><body>\n')
TAIL = '\n</body></html>\n'


def wrap(src, noindex=False):
    if src.lstrip()[:9].lower() == '<!doctype':
        return src
    ni = '<meta name="robots" content="noindex">' if noindex else ''
    return HEAD.format(noindex=ni) + src + TAIL


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    src = open(a[0], encoding='utf8').read()
    out = wrap(src, '--noindex' in sys.argv)
    os.makedirs(os.path.dirname(os.path.abspath(a[1])), exist_ok=True)
    open(a[1], 'w', encoding='utf8').write(out)
    print(a[1], len(out.encode()) // 1024, 'KB')
