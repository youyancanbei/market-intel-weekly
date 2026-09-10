# -*- coding: utf-8 -*-
"""市场情报周报 HTML 生成器（邮件安全：全内联样式 + table 布局 + MSO 条件注释）。

用法：
    python build_weekly_html.py report.json out.html

report.json 结构：
{
  "title": "算力行业 · 市场情报周报",
  "eyebrow": "COMPUTING / SEMICONDUCTOR · WEEKLY INTEL",
  "coverage": "2026-09-03 → 2026-09-09",
  "overview": [ {"head": "...", "body": "..."}, ... ],          # 板块01 概览
  "sections": [
    {
      "num": "02", "title": "...", "sub": "...", "accent": "#1F4E79",
      "layout": "card" | "kpi+table" | "table" | "timeline" | "callout+card",
      "callout": {"label": "...", "big": "...", "body": "..."},   # callout 用
      "kpis": [ {"value":"..","label":"..","source":"..","color":"#C00000"}, ... ],
      "headers": ["日期","...","..."],  # table 用
      "colw": ["width:80px;","","",...],
      "rows": [["2026-09-07","...","..."], ...],   # table: 每格为 HTML 或纯文本
      "cards": [ {"date":"..","title":"..","tags":["国内","规划"],"point":"..","imp":"→ ..","links":[["财联社","https://.."]]}, ... ],  # card/timeline
      "note": "可选：卡片下方提示（HTML 或纯文本）"
    }, ...
  ],
  "footer_links": [ ["证券时报","https://.."] ]   # 可选，页脚不渲染解说；仅当需要外链时用
}

约定：
- cards 用于 card/timeline 布局；rows 用于 table/kpi+table。
- timeline 不渲染 tags（避免页面出现标签 span）；card 渲染 tags 为彩色 span。
- imp 以 "→"/"⚠" 开头则原样，否则自动补 "→ "。
- 可信度/类型标签用 tags 数组，颜色见 TAG 表；可在 report.json 里自由写文本。
"""
import sys, json, base64
FONT="-apple-system,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',Arial,sans-serif"
def esc(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
TAG={'属实':('#E7F4EA','#2E7D32'),'部分属实':('#FFF3E0','#B35A00'),'未证实':('#FDECEC','#C00000'),
 '一手':('#E7F4EA','#2E7D32'),'媒体':('#E8F1FB','#2E75B6'),'待核':('#FDECEC','#C00000'),'传闻':('#FDECEC','#C00000'),
 '国内':('#E8F1FB','#1F4E79'),'海外':('#FDECEC','#C00000'),'管制':('#FFF3E0','#B35A00'),'规划':('#E7F4EA','#2E7D32'),
 '绿色':('#E7F4EA','#2E7D32'),'绿电':('#E7F4EA','#2E7D32'),'中标':('#E7F4EA','#2E7D32'),'政采':('#EAF1FF','#3B5BAA'),
 '融资':('#FFF3E0','#B35A00'),'研报':('#F3E8FB','#7030A0'),'行情':('#E8F1FB','#2E75B6'),'并购':('#FFF3E0','#B35A00'),
 '政策':('#FDECEC','#C00000'),'设计':('#E8F1FB','#2E75B6'),'存储':('#F3E8FB','#7030A0'),'整机':('#FFF3E0','#B35A00'),
 '资本':('#FDECEC','#C00000'),'财报':('#E8F1FB','#2E75B6')}
def chip(t):
    bg,fg=TAG.get(t,('#EEF1F5','#5a6675'))
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font-size:11px;font-weight:600;'
            f'padding:2px 8px;border-radius:10px;line-height:18px;vertical-align:middle;">{esc(t)}</span>')
def links_html(ls):
    if not ls: return ''
    a=' · '.join(f'<a href="{esc(u)}" style="color:#2E75B6;text-decoration:none;">{esc(n)}</a>' for n,u in ls)
    return f'<div style="font-size:12px;color:#8a94a6;margin-top:6px;">来源：{a}</div>'
def imp_norm(imp):
    return imp if imp[:1] in ('→','⚠') else '→ '+imp

def sec_head(num,title,sub,accent):
    return (f'<tr><td style="padding:26px 26px 6px 26px;"><table width="100%" cellpadding="0" cellspacing="0" '
            f'style="border-collapse:collapse;"><tr><td width="6" style="background:{accent};"></td>'
            f'<td style="padding-left:12px;">'
            f'<span style="font-size:12px;font-weight:700;color:{accent};letter-spacing:1px;">板块{esc(num)}</span>'
            f'<div style="font-size:19px;font-weight:700;color:#1b2735;line-height:1.4;">{esc(title)}</div>'
            f'<div style="font-size:12.5px;color:#8a94a6;margin-top:2px;">{esc(sub)}</div>'
            f'</td></tr></table></td></tr>')

def card(c,accent):
    tl=' '.join(chip(x) for x in c.get('tags',[]))
    pt=f'<div style="font-size:13.5px;color:#404b58;margin-top:7px;line-height:1.65;">{esc(c["point"])}</div>' if c.get('point') else ''
    impv=imp_norm(c.get('imp','')); col='#C00000' if impv.startswith('⚠') else accent
    impd=f'<div style="font-size:13px;color:{col};margin-top:8px;line-height:1.6;">{esc(impv)}</div>'
    return (f'<tr><td style="padding:5px 26px 0 26px;"><table width="100%" cellpadding="0" cellspacing="0" '
            f'style="border-collapse:collapse;background:#fff;border:1px solid #eef1f5;border-radius:8px;">'
            f'<tr><td style="padding:12px 14px;">'
            f'<div style="font-size:12px;color:#8a94a6;font-weight:600;">{esc(c["date"])} {tl}</div>'
            f'<div style="font-size:14.5px;color:#1b2735;font-weight:700;margin-top:3px;line-height:1.5;">{esc(c["title"])}</div>'
            f'{pt}{impd}{links_html(c.get("links"))}</td></tr></table></td></tr>')

def table(s):
    accent=s['accent']
    th=''.join(f'<th align="left" style="font-size:12px;color:#fff;background:{accent};padding:8px 10px;border-right:1px solid rgba(255,255,255,.2);">{esc(h)}</th>' for h in s['headers'])
    colw=s.get('colw',[''] * len(s['headers'])); colw=(colw+['']*len(s['headers']))[:len(s['headers'])]
    trs=''
    for i,r in enumerate(s['rows']):
        bg='#fbfcfe' if i%2 else '#fff'
        cells=''.join(f'<td style="font-size:13px;color:#33404e;padding:9px 10px;border-bottom:1px solid #eef1f5;vertical-align:top;{w}">{c}</td>' for c,w in zip(r,colw))
        trs+=f'<tr style="background:{bg};">{cells}</tr>'
    return (f'<tr><td style="padding:8px 26px 0 26px;"><table width="100%" cellpadding="0" cellspacing="0" '
            f'style="border-collapse:collapse;border:1px solid #e6ebf1;border-radius:8px;">'
            f'<thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></td></tr>')

def kpi(s):
    tiles=s['kpis']; n=len(tiles); w=100//n
    tds=''
    for t in tiles:
        tds+=(f'<td width="{w}%" style="padding:6px;"><div style="background:#fff;border:1px solid #eef1f5;'
              f'border-left:3px solid {t.get("color","#1F4E79")};border-radius:8px;padding:12px;">'
              f'<div style="font-size:19px;font-weight:800;color:{t.get("color","#1F4E79")};">{esc(t["value"])}</div>'
              f'<div style="font-size:12px;color:#404b58;margin-top:4px;line-height:1.4;">{esc(t["label"])}</div>'
              f'<div style="font-size:11px;color:#a6afc0;margin-top:3px;">{esc(t.get("source",""))}</div></div></td>')
    return f'<tr><td style="padding:8px 18px 0 18px;"><table width="100%" cellpadding="0" cellspacing="0"><tr>{tds}</tr></table></td></tr>'

def timeline(s):
    accent=s['accent']; out=''
    items=s['cards']
    for i,c in enumerate(items):
        last='padding-bottom:4px;' if i==len(items)-1 else ''
        pt=f'<div style="font-size:12.5px;color:#5a6673;margin-top:4px;line-height:1.6;">{esc(c["point"])}</div>' if c.get('point') else ''
        impd=f'<div style="font-size:12.5px;color:{accent};margin-top:4px;line-height:1.55;">{esc(imp_norm(c.get("imp","")))}</div>'
        out+=(f'<tr><td valign="top" width="70" style="font-size:12px;font-weight:700;color:#8a94a6;padding:8px 8px 8px 0;text-align:right;{last}">{esc(c["date"])}</td>'
              f'<td valign="top" width="16" style="padding-top:12px;{last}"><div style="width:11px;height:11px;background:{accent};border-radius:6px;margin-left:2px;"></div></td>'
              f'<td valign="top" style="border-left:2px solid #e6ebf1;padding:6px 0 8px 14px;{last}">'
              f'<div style="font-size:14px;font-weight:700;color:#1b2735;line-height:1.45;">{esc(c["title"])}</div>{pt}{impd}{links_html(c.get("links"))}</td></tr>')
    return f'<tr><td style="padding:8px 26px 0 26px;"><table width="100%" cellpadding="0" cellspacing="0">{out}</table></td></tr>'

def callout(s):
    co=s['callout']; ac=s['accent']
    return (f'<tr><td style="padding:8px 26px 2px 26px;"><table width="100%" cellpadding="0" cellspacing="0" '
            f'style="border-collapse:collapse;background:#FFF4E6;border:1px solid #FBE0BF;border-radius:10px;">'
            f'<tr><td style="padding:16px 18px;">'
            f'<div style="font-size:12px;color:{ac};font-weight:700;">{esc(co["label"])}</div>'
            f'<div style="font-size:22px;font-weight:800;color:{ac};margin-top:4px;">{esc(co["big"])}</div>'
            f'<div style="font-size:13px;color:#5a6673;margin-top:4px;line-height:1.6;">{co["body"]}</div>'
            f'</td></tr></table></td></tr>')

def render_section(s):
    out=[sec_head(s['num'],s['title'],s.get('sub',''),s['accent'])]
    lay=s.get('layout','card')
    if lay=='callout+card': out.append(callout(s))
    if lay in ('kpi+table',): out.append(kpi(s))
    if lay in ('table','kpi+table'): out.append(table(s))
    if lay=='timeline': out.append(timeline(s))
    if lay in ('card','callout+card'):
        for c in s['cards']: out.append(card(c,s['accent']))
    if s.get('note'):
        out.append(f'<tr><td style="padding:6px 26px 2px 26px;"><div style="font-size:12.5px;color:#8a6d1b;background:#FFF8E1;border:1px solid #FCE8B0;border-radius:6px;padding:8px 12px;line-height:1.6;">{s["note"]}</div></td></tr>')
    return ''.join(out)

def header(rep):
    cov=f'<div style="font-size:13px;color:#dce8f5;margin-top:12px;line-height:1.7;">{esc(rep.get("coverage_label","覆盖区间"))} <b style="color:#fff;">{esc(rep["coverage"])}</b></div>'
    b64=rep.get('logo_b64')
    if not b64 and rep.get('logo'):
        try: b64=base64.b64encode(open(rep['logo'],'rb').read()).decode()
        except Exception: b64=''
    if b64:
        img=f'<img src="data:image/png;base64,{b64}" height="58" alt="logo" style="display:block;border:0;outline:none;height:58px;width:auto;">'
        en=rep.get('brand_en') or rep.get('title','')
        zh=rep.get('brand_zh','')
        right=f'<div style="font-size:15px;line-height:20px;color:#bcd2ea;letter-spacing:2px;font-weight:700;">{esc(en)}</div>'
        if zh: right+=f'<div style="font-size:26px;line-height:34px;font-weight:800;color:#ffffff;margin-top:4px;">{esc(zh)}</div>'
        right+=cov
        return (f'<tr><td style="background:#1F4E79;padding:22px 26px;">'
                f'<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;"><tr>'
                f'<td width="86" valign="top" style="padding-right:18px;">{img}</td>'
                f'<td valign="top">{right}</td></tr></table></td></tr>')
    return (f'<tr><td style="background:#1F4E79;padding:26px 28px;">'
            f'<div style="font-size:12px;color:#bcd2ea;letter-spacing:2px;font-weight:600;">{esc(rep.get("eyebrow","WEEKLY INTEL"))}</div>'
            f'<div style="font-size:24px;font-weight:800;color:#fff;margin-top:4px;line-height:1.3;">{esc(rep["title"])}</div>'
            f'<div style="font-size:13px;color:#dce8f5;margin-top:10px;">{esc(rep.get("coverage_label","覆盖区间"))} <b style="color:#fff;">{esc(rep["coverage"])}</b></div></td></tr>')

def build(rep):
    S=[]
    S.append(header(rep))
    if rep.get('overview'):
        S.append(sec_head('01','本周主线 · 概览','4 条最值得关注的信号','#1F4E79'))
        rows=''
        for i,o in enumerate(rep['overview'],1):
            rows+=(f'<tr><td width="30" valign="top" style="font-size:20px;font-weight:800;color:#2E75B6;padding:6px 8px 6px 0;line-height:1;">{i}</td>'
                   f'<td valign="top" style="padding:6px 0;"><div style="font-size:14.5px;font-weight:700;color:#1b2735;">{esc(o["head"])}</div>'
                   f'<div style="font-size:13px;color:#404b58;margin-top:3px;line-height:1.65;">{esc(o["body"])}</div></td></tr>')
        S.append(f'<tr><td style="padding:8px 26px 4px 26px;"><table width="100%" cellpadding="0" cellspacing="0" '
                 f'style="border-collapse:collapse;background:#F2F6FB;border:1px solid #dbe6f3;border-radius:10px;">'
                 f'<tr><td style="padding:8px 18px 12px 18px;"><table width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr></table></td></tr>')
    for s in rep['sections']:
        S.append(render_section(s))
    body=''.join(S)
    return ('<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="x-apple-disable-message-reformatting">'
            '<!--[if mso]><style>*{font-family:Arial,sans-serif!important;}</style><![endif]-->'
            f'<title>{esc(rep["title"])} {esc(rep["coverage"])}</title></head>'
            f'<body style="margin:0;padding:0;background:#eef1f5;font-family:{FONT};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef1f5;">'
            f'<tr><td align="center" style="padding:18px 8px;">'
            f'<table role="presentation" width="700" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;'
            f'background:#fff;font-family:{FONT};color:#222;border-radius:12px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.08);">'
            f'{body}</table>'
            f'<div style="font-family:{FONT};font-size:11px;color:#a6afc0;margin-top:12px;">{esc(rep["title"])} · {esc(rep["coverage"])}</div>'
            f'</td></tr></table></body></html>')

if __name__=='__main__':
    rep=json.load(open(sys.argv[1],encoding='utf-8'))
    open(sys.argv[2],'w',encoding='utf-8').write(build(rep))
    print('已生成', sys.argv[2])
