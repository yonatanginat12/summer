# -*- coding: utf-8 -*-
import base64
B = lambda p: base64.b64encode(open(p,'rb').read()).decode()
FONTS = f"""
@font-face{{font-family:FRL;src:url(data:font/woff2;base64,{B('fonts/frl-400.woff2')}) format('woff2');
  font-weight:300 700;font-style:normal;font-display:swap;
  unicode-range:U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F}}
@font-face{{font-family:FRL;src:url(data:font/woff2;base64,{B('fonts/frl-digits.woff2')}) format('woff2');
  font-weight:300 700;font-style:normal;font-display:swap;
  unicode-range:U+0030-0039}}
@font-face{{font-family:Hand;src:url(data:font/woff2;base64,{B('../handoff/fonts/GveretLevin.woff2')}) format('woff2');font-display:swap}}
"""
COVERCSS = """
.cv{position:relative;aspect-ratio:135/210;container-type:inline-size;overflow:hidden;
  background:#ECE8DF;color:#2B3358;font-family:FRL,"Frank Ruhl Libre",serif;line-height:1;
  box-shadow:var(--shadow,0 2px 10px rgba(0,0,0,.25))}
.cv.form{background:#EFEDE6}
.cv svg{position:absolute;inset:0;width:100%;height:100%;display:block}
.cv .tx{position:absolute;left:0;right:0;text-align:center;white-space:nowrap;line-height:1}
.cv .t-serif{font-weight:400;color:#2B3358;letter-spacing:.015em}
.cv .sub{color:#2B3358;opacity:.82;font-weight:400}
.cv .auth{color:#2B3358;font-weight:400}
.cv .hand-t{font-family:Hand;color:#232A45}
.cv .hand-a{font-family:Hand;color:#232A45}
.cv .sub-red{color:#D24329;font-weight:400}
.cv .form-h{font-weight:400;color:#2B3358}
.cv .form-lab{color:#8E8E85;font-weight:400;letter-spacing:.08em}
.cv .frame,.cv .box{position:absolute;border:1px solid #75756D}
.cv .hline{position:absolute;border-top:1px solid #75756D}
.cv .vline{position:absolute;border-left:1px solid #75756D}
.cv .cell{position:absolute}
.cv .cell span{position:absolute;top:16%;right:9%;font-size:1.75cqw;color:#8E8E85;
  letter-spacing:.08em;white-space:nowrap}
.cv .rules{position:absolute;inset:0}
.cv .rules i{position:absolute;border-top:1px solid #75756D;opacity:.4;display:block}
.cv .act{display:flex;justify-content:space-between;padding:0 14%;color:#8E8E85}
"""
