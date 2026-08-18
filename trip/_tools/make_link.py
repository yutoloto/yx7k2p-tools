#!/usr/bin/env python3
"""旅のしおりアプリへの取り込みリンクを作る。

社長は手入力しない。Claudeが旅程を組んだらこれでリンクにして渡し、
社長はタップするだけ、という運用のための道具。

    python make_link.py 旅.json            # URLを表示
    python make_link.py 旅.json -o out.html # 押すだけのページも作る

入力JSON（1件でも配列でも可）:
{
  "name": "熊野旅行", "start": "2026-08-17", "days": 2,
  "people": ["自分", "相方"],
  "rule": "16:00に川を出る",
  "events": [{"day":1, "time":"08:55", "title":"品川発 のぞみ63号",
              "note":"11号車6番D・E席", "addr":"東京都港区高輪3-26-27",
              "tel":"03-0000-0000", "alt":"満席なら次の便", "key":true}],
  "checks": [{"text":"マリンシューズ"}],
  "expenses":[{"name":"宿","amount":33000,"payer":"自分","split":["自分","相方"]}],
  "contacts":[{"name":"宿SENT","tel":"090-0000-0000"}],
  "plans":  [{"w":"雨で花火が順延","t":"翌日の同時刻へ。宿に連絡"}],
  "memo": "自由記述"
}
省略した項目はアプリ側が補う。plansを省くとアプリ内蔵の定番14件は入らないので、
必要なら受け取った側で「よくあるトラブルを入れる」を押す。
"""
import sys, json, zlib, base64, urllib.parse

APP = "https://yutoloto.github.io/yx7k2p-tools/trip/"

PAGE = """<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<meta name="robots" content="noindex, nofollow">
<style>
:root{{--canvas:#fff;--ash:#efefef;--ink:#202020;--steel:#4d4d4d;--mute:#8a8a8a;--accent:#ff682c}}
@media (prefers-color-scheme:dark){{:root{{--canvas:#0d0d0d;--ash:#191919;--ink:#f0f0f0;--steel:#a8a8a8;--mute:#767676;--accent:#ff7d47}}}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--canvas);color:var(--ink);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;
font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.5}}
.box{{max-width:420px;width:100%}}
.lbl{{font-size:11px;font-weight:600;letter-spacing:.14em;color:var(--mute)}}
h1{{font-size:28px;font-weight:500;letter-spacing:-.02em;margin:10px 0 0}}
p{{font-size:14px;line-height:1.7;color:var(--steel);margin-top:12px}}
a.go{{display:block;text-align:center;background:var(--ink);color:var(--canvas);text-decoration:none;
padding:16px;font-size:16px;font-weight:500;margin-top:24px}}
.meta{{margin-top:20px;padding-top:16px;border-top:1px solid var(--ash);font-size:13px;color:var(--mute)}}
.meta b{{color:var(--accent);font-weight:600}}
</style></head>
<body><div class="box">
<div class="lbl">取り込み</div>
<h1>{title}</h1>
<p>下を押すと「旅のしおり」に追加されます。いま入っているデータは消えません。</p>
<a class="go" href="{url}">アプリに取り込む</a>
<div class="meta">{meta}</div>
</div></body></html>
"""


def make_url(data):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = co.compress(raw) + co.flush()
    b64 = base64.urlsafe_b64encode(packed).decode().rstrip("=")
    return APP + "#z=" + b64


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    trips = data if isinstance(data, list) else data.get("trips", [data])
    url = make_url(trips)

    t = trips[0]
    meta = " ・ ".join(
        f"{label}<b>{len(t.get(k, []))}</b>件"
        for k, label in (("events", "行程"), ("checks", "持ちもの"),
                         ("expenses", "立替"), ("plans", "もしも"))
        if t.get(k)
    )
    print(url)
    print(f"\n長さ {len(url)} 字", file=sys.stderr)
    if len(url) > 1900:
        print("⚠ Discordの2000字に収まりません。ページごと渡してください。", file=sys.stderr)

    if "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o") + 1]
        title = t.get("name", "旅のデータ")
        open(out, "w", encoding="utf-8").write(
            PAGE.format(title=title, url=url, meta=meta or "データ"))
        print(f"ページを書きました: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
