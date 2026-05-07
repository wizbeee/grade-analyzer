"""
단일 HTML 빌드 스크립트
=======================
index.html + vendor/*.js 6종을 모두 인라인하여 'dist/성적분석_standalone.html'을 생성.
받는 사람이 더블클릭만으로 작동하는 단일 파일이 필요할 때 사용.

실행:
    python build_standalone.py
"""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ROOT, "index.html")
OUT_DIR = os.path.join(ROOT, "dist")
OUT = os.path.join(OUT_DIR, "성적분석_standalone.html")

# <script src="vendor/xxx.js"></script> 패턴
SCRIPT_RE = re.compile(r'<script\s+src="(vendor/[^"]+)"\s*></script>', re.IGNORECASE)


def inline_one(match):
    rel_path = match.group(1)
    abs_path = os.path.join(ROOT, rel_path)
    if not os.path.exists(abs_path):
        print(f"  [경고] 누락: {rel_path}")
        return match.group(0)
    with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    # </script> 시퀀스가 본문에 있으면 인라인 시 HTML 파싱이 깨지므로 escape
    content = content.replace("</script>", "<\\/script>")
    size_kb = len(content) / 1024
    print(f"  [인라인] {rel_path} ({size_kb:.0f} KB)")
    return f"<script>\n/* inlined: {rel_path} */\n{content}\n</script>"


def main():
    if not os.path.exists(INDEX):
        print(f"[오류] {INDEX} 없음")
        sys.exit(1)

    with open(INDEX, "r", encoding="utf-8") as f:
        html = f.read()

    print("[빌드 시작]")
    print(f"  원본: {INDEX} ({len(html)/1024:.0f} KB)")

    inlined = SCRIPT_RE.sub(inline_one, html)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(inlined)

    out_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"[완료] {OUT}")
    print(f"  크기: {out_mb:.1f} MB")
    print()
    print("이 파일 한 개를 USB/이메일/클라우드로 옮긴 뒤,")
    print("받는 사람이 더블클릭하면 브라우저에서 바로 작동합니다.")


if __name__ == "__main__":
    main()
