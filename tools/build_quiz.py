"""04_예상문제/*.md 를 읽어 05_모의고사/모의고사.html 을 만든다.

문제 형식: '**번호.** 지문' 다음 줄들에 ①~④ 보기, 바로 아래 '> **정답:** ... > **해설:** ...'
문제를 고치면 이 스크립트를 다시 실행: python3 tools/build_quiz.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "04_예상문제"
OUT = ROOT / "05_모의고사" / "모의고사.html"
TEMPLATE = Path(__file__).resolve().parent / "quiz_template.html"

SUBJECTS = [
    ("01", "조림", "필수"),
    ("02", "산림보호", "필수"),
    ("03", "산림경영", "필수"),
    ("04", "산림관계법규", "필수"),
    ("05", "산림토목", "선택"),
    ("06", "임산가공", "선택"),
]
MARKS = "①②③④"


def parse(path, subject):
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^(?=\*\*\d+\.\*\* )", text, flags=re.M)
    questions = []
    for block in blocks[1:]:
        m = re.match(r"\*\*(\d+)\.\*\*\s*(.*)", block, re.S)
        if not m:
            continue
        num = int(m.group(1))
        body = m.group(2).strip()

        m_ans = re.search(r">\s*\*\*정답:\*\*\s*([①②③④])", body)
        m_expl = re.search(r">\s*\*\*해설:\*\*\s*(.*?)\s*(?:\n\s*>|$)", body)
        m_ref = re.search(r">\s*\*\*출제 근거:\*\*\s*(.*?)(?:\n|$)", body)

        if not m_ans:
            raise SystemExit(f"{path.name} {num}번: 정답 없음")

        ans = MARKS.index(m_ans.group(1))
        expl = m_expl.group(1).strip() if m_expl else ""
        ref = m_ref.group(1).strip() if m_ref else ""

        q_content = re.split(r"\n\s*>", body)[0].strip()
        parts = re.split(r"([①②③④])", q_content)
        stem = parts[0].strip()
        options = [p.strip() for p in parts[2::2]]

        if len(options) != 4:
            raise SystemExit(f"{path.name} {num}번: 보기 {len(options)}개")

        part = 1 if num <= 20 else 2 if num <= 40 else 3 if num <= 50 else 4
        questions.append({
            "id": f"{subject}-{num}",
            "subject": subject,
            "num": num,
            "part": part,
            "stem": stem,
            "options": options,
            "answer": ans,
            "explain": re.sub(r"\*\*", "", expl),
            "ref": ref,
        })
    return questions


def main():
    data = []
    for code, name, kind in SUBJECTS:
        path = next(SRC.glob(f"{code}.*.md"))
        data.append({"code": code, "name": name, "kind": kind, "questions": parse(path, name)})
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    total = sum(len(s["questions"]) for s in data)
    print(f"{OUT.relative_to(ROOT)}: {total}문항 빌드 완료")


if __name__ == "__main__":
    main()
