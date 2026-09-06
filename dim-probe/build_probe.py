#!/usr/bin/env python3
"""第 252 跑 R2：三個「立體」原型 + 一格 catch trial 的產生器。

四格畫的是**同一張圖**（訊號放大喇叭 + 工程語彙的等寬對照管），
只有立體手法不同 —— 這是單變數實驗，不是四張不同的圖。

規格檔紀律（KB-19 第三層）：真尺寸只在規格來源區誕生，畫圖區只准引用。
用法：
    python3 build_probe.py > index.html
"""
import math

# @figure-spec-source
# 訊號管道沿傳播方向的四個轉換點；半徑是「傳播規模」的示意值，不是量測值。
STATION_X_MM = [0.0, 95.0, 190.0, 285.0, 380.0]        # 四段的分界站位
NARR_HALFSIZE_MM = [12.0, 24.0, 38.0, 54.0, 72.0]      # 擬人化語彙：逐段擴張
ENG_HALFSIZE_MM = 12.0                                  # 工程語彙：全程等寬
ENG_SOLID_END_MM = 190.0                                # 工程語彙實體段的終點
ENG_FADE_END_MM = 258.0                                 # 虛線段的終點（第二天被駁倒）
ENG_LIFT_MM = 168.0                                     # 工程語彙管抬高多少（z 方向）
ISO_ANGLE_DEG = 30.0                                    # 等角投影角
CSS3D_PLATE_GAP_PX = 62.0                               # CSS 3D 四塊板的深度間距
CSS3D_PERSPECTIVE_PX = 900.0
CANVAS_W_PX = 900.0
CANVAS_H_PX = 470.0
START_BLOCK_X0_MM = -58.0                               # 共同起點方塊的左端
START_BLOCK_X1_MM = -6.0                                # 共同起點方塊的右端
START_BLOCK_HALFSIZE_MM = 15.0                          # 共同起點方塊的半邊長
VIEWBOX_PAD_MM = 26.0                                   # viewBox 四周留白
RAMP_BREAK_LO = 0.25                                    # 色帶：青轉琥珀的斷點
RAMP_BREAK_HI = 0.75                                    # 色帶：琥珀轉紅的斷點
QUAD_VERTS = 4                                          # 一個面有幾個頂點
SEG_LABEL_BASELINE_MM = 10                              # 段號基線相對重心的位移
CSS3D_PLATE_W_BASE_PX = 142.0                            # 最前面那塊板的寬
CSS3D_PLATE_W_STEP_PX = 34.0                            # 每往後一塊板加寬多少
CSS3D_PLATE_H_BASE_PX = 108.0                            # 最前面那塊板的高
CSS3D_PLATE_H_STEP_PX = 26.0                            # 每往後一塊板加高多少
CSS3D_RAIL_LEN_PX = 430.0                               # 貫穿四塊板那條線的長度
CSS3D_CENTER_OFFSET = 1.5                               # 四塊板沿深度置中的位移 (n-1)/2
CSS3D_PLATE_TX_STEP_PX = 152.0                           # 每往前一塊板往右錯開多少
# @end-figure-spec-source

SEGMENTS = len(STATION_X_MM) - 1


# @figure-spec
def iso(x, y, z):
    """等角投影。x 沿傳播方向，y 是管寬，z 是高度。"""
    c = math.cos(math.radians(ISO_ANGLE_DEG))
    s = math.sin(math.radians(ISO_ANGLE_DEG))
    return ((x - y) * c, (x + y) * s - z)


def box_faces(x0, x1, s0, s1, lift):
    """一段管子的兩個可見面：頂面與近側面。"""
    top = [iso(x0, -s0, s0 + lift), iso(x1, -s1, s1 + lift),
           iso(x1, s1, s1 + lift), iso(x0, s0, s0 + lift)]
    side = [iso(x0, s0, s0 + lift), iso(x1, s1, s1 + lift),
            iso(x1, s1, -s1 + lift), iso(x0, s0, -s0 + lift)]
    return top, side


def path_of(pts):
    return "M" + " L".join("%.1f %.1f" % p for p in pts) + " Z"


def ramp(t):
    if t < RAMP_BREAK_LO:
        return "var(--plate-teal)"
    if t < RAMP_BREAK_HI:
        return "var(--plate-amber)"
    return "var(--plate-red)"


def build_iso_svg(uid):
    """臂 ①／④：SVG 等角實體。零 JS。"""
    parts = []
    allpts = []
    for i in range(SEGMENTS):
        x0, x1 = STATION_X_MM[i], STATION_X_MM[i + 1]
        s0, s1 = NARR_HALFSIZE_MM[i], NARR_HALFSIZE_MM[i + 1]
        top, side = box_faces(x0, x1, s0, s1, 0.0)
        allpts += top + side
        parts.append('<path d="%s" fill="url(#gt%s%d)" stroke="var(--plate-bg)" stroke-width="1.2"/>'
                     % (path_of(top), uid, i))
        parts.append('<path d="%s" fill="url(#gs%s%d)" stroke="var(--plate-bg)" stroke-width="1.2"/>'
                     % (path_of(side), uid, i))
        cx = sum(p[0] for p in top) / float(QUAD_VERTS)
        cy = sum(p[1] for p in top) / float(QUAD_VERTS)
        parts.append('<text x="%.1f" y="%.1f" font-size="30" font-weight="700" '
                     'text-anchor="middle" fill="var(--plate-bg)">%d</text>'
                     % (cx, cy + SEG_LABEL_BASELINE_MM, i + 1))
    top, side = box_faces(0.0, ENG_SOLID_END_MM, ENG_HALFSIZE_MM, ENG_HALFSIZE_MM, ENG_LIFT_MM)
    allpts += top + side
    parts.append('<path d="%s" fill="var(--plate-teal)" opacity="0.92" '
                 'stroke="var(--plate-bg)" stroke-width="1.2"/>' % path_of(top))
    parts.append('<path d="%s" fill="var(--plate-teal)" opacity="0.55" '
                 'stroke="var(--plate-bg)" stroke-width="1.2"/>' % path_of(side))
    top2, side2 = box_faces(ENG_SOLID_END_MM, ENG_FADE_END_MM,
                            ENG_HALFSIZE_MM, ENG_HALFSIZE_MM, ENG_LIFT_MM)
    allpts += top2 + side2
    parts.append('<path d="%s" fill="none" stroke="var(--plate-teal)" stroke-width="1.6" '
                 'stroke-dasharray="7 6"/>' % path_of(top2))
    parts.append('<path d="%s" fill="none" stroke="var(--plate-teal)" stroke-width="1.6" '
                 'stroke-dasharray="7 6" opacity="0.7"/>' % path_of(side2))
    st_top, st_side = box_faces(START_BLOCK_X0_MM, START_BLOCK_X1_MM,
                                START_BLOCK_HALFSIZE_MM, START_BLOCK_HALFSIZE_MM,
                                ENG_LIFT_MM * 0.5)
    allpts += st_top + st_side
    parts.append('<path d="%s" fill="var(--plate-line)"/>' % path_of(st_top))
    parts.append('<path d="%s" fill="var(--plate-line)" opacity="0.65"/>' % path_of(st_side))

    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    pad = VIEWBOX_PAD_MM
    minx, maxx = min(xs) - pad, max(xs) + pad
    miny, maxy = min(ys) - pad, max(ys) + pad
    defs = ['<defs>']
    for i in range(SEGMENTS):
        t0 = i / float(SEGMENTS)
        t1 = (i + 1) / float(SEGMENTS)
        defs.append('<linearGradient id="gt%s%d" x1="0" y1="0" x2="1" y2="0">'
                    '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
                    '</linearGradient>' % (uid, i, ramp(t0), ramp(t1)))
        defs.append('<linearGradient id="gs%s%d" x1="0" y1="0" x2="1" y2="0">'
                    '<stop offset="0" stop-color="%s" stop-opacity="0.62"/>'
                    '<stop offset="1" stop-color="%s" stop-opacity="0.62"/>'
                    '</linearGradient>' % (uid, i, ramp(t0), ramp(t1)))
    defs.append('</defs>')
    return ('<svg viewBox="%.1f %.1f %.1f %.1f" role="img" aria-labelledby="t%s d%s">'
            '<title id="t%s">訊號放大管道的等角實體圖</title>'
            '<desc id="d%s">兩條從同一個方塊出發的立體管道。上方那條全程等寬，'
            '中途改為虛線後終止；下方那條沿四個編號段逐段變粗，顏色由青轉紅。</desc>'
            '%s%s</svg>'
            % (minx, miny, maxx - minx, maxy - miny, uid, uid, uid, uid,
               "".join(defs), "".join(parts)))


def build_css3d():
    """臂 ②：CSS 3D 分層疊深度。零 JS。四塊板沿深度排開，前面的擋住後面的。"""
    plates = []
    for i in range(SEGMENTS):
        z = CSS3D_PLATE_GAP_PX * (i - CSS3D_CENTER_OFFSET)
        tx = CSS3D_PLATE_TX_STEP_PX * (i - CSS3D_CENTER_OFFSET)
        w = CSS3D_PLATE_W_BASE_PX + CSS3D_PLATE_W_STEP_PX * i
        h = CSS3D_PLATE_H_BASE_PX + CSS3D_PLATE_H_STEP_PX * i
        plates.append('<div class="plate p%d" style="--z:%.0fpx;--tx:%.0fpx;'
                      '--w:%.0fpx;--h:%.0fpx"><span class="pn">%d</span></div>'
                      % (i + 1, z, tx, w, h, i + 1))
    return ('<div class="deck" style="--persp:%.0fpx">'
            '<div class="deck-inner">'
            '%s<div class="eng"><span class="pn">A</span></div>'
            '</div></div>' % (CSS3D_PERSPECTIVE_PX, "".join(plates)))


CANVAS_JS_TEMPLATE = """
(function(){
  var cv=document.getElementById('c3'); if(!cv) return;
  var ctx=cv.getContext('2d'), yaw=0.72, drag=false, lx=0, W=0, H=0;
  var SX=%s, SN=%s, EH=%s, ES=%s, EF=%s, EL=%s;
  var TILT=0.34, PAD=26, sc=1, ox=0, oy=0;
  function cs(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
  function raw(x,y,z){
    var cy=Math.cos(yaw), sy=Math.sin(yaw);
    var X=x*cy - y*sy, Z=x*sy + y*cy;
    return [X, Z*TILT - z];
  }
  function P(p){ return [ox + p[0]*sc, oy + p[1]*sc]; }
  function rawFaces(x0,x1,s0,s1,lift){
    return [[raw(x0,-s0,s0+lift),raw(x1,-s1,s1+lift),raw(x1,s1,s1+lift),raw(x0,s0,s0+lift)],
            [raw(x0,s0,s0+lift),raw(x1,s1,s1+lift),raw(x1,s1,-s1+lift),raw(x0,s0,-s0+lift)]];
  }
  function allFaces(){
    var out=[];
    out.push({f:rawFaces(0,ES,EH,EH,EL), kind:'eng'});
    out.push({f:rawFaces(ES,EF,EH,EH,EL), kind:'fade'});
    for(var i=0;i<4;i++) out.push({f:rawFaces(SX[i],SX[i+1],SN[i],SN[i+1],0), kind:'seg', i:i});
    return out;
  }
  function fit(list){
    var xs=[], ys=[];
    list.forEach(function(o){o.f.forEach(function(q){q.forEach(function(p){xs.push(p[0]);ys.push(p[1]);});});});
    var x0=Math.min.apply(null,xs), x1=Math.max.apply(null,xs);
    var y0=Math.min.apply(null,ys), y1=Math.max.apply(null,ys);
    sc=Math.min((W-2*PAD)/(x1-x0), (H-2*PAD)/(y1-y0));
    ox=(W-(x1-x0)*sc)/2 - x0*sc;
    oy=(H-(y1-y0)*sc)/2 - y0*sc;
  }
  function poly(p){ctx.beginPath();ctx.moveTo(p[0][0],p[0][1]);
    for(var i=1;i<p.length;i++)ctx.lineTo(p[i][0],p[i][1]);ctx.closePath();}
  function quad(q,fill,alpha){var p=q.map(P);ctx.globalAlpha=alpha;poly(p);
    ctx.fillStyle=fill;ctx.fill();ctx.globalAlpha=1;
    ctx.strokeStyle=cs('--plate-bg');ctx.lineWidth=1.2;ctx.stroke();return p;}
  function draw(){
    ctx.clearRect(0,0,W,H);
    var list=allFaces(); fit(list);
    var cols=[cs('--plate-teal'),cs('--plate-amber'),cs('--plate-amber'),cs('--plate-red')];
    var teal=cs('--plate-teal');
    list.forEach(function(o){
      if(o.kind==='eng'){ quad(o.f[1],teal,0.58); quad(o.f[0],teal,0.92); }
      else if(o.kind==='fade'){
        ctx.save();ctx.setLineDash([7,6]);ctx.strokeStyle=teal;ctx.lineWidth=1.6;
        poly(o.f[0].map(P));ctx.stroke();poly(o.f[1].map(P));ctx.stroke();ctx.restore();
      } else {
        quad(o.f[1],cols[o.i],0.62);
        var p=quad(o.f[0],cols[o.i],1);
        var cx=(p[0][0]+p[1][0]+p[2][0]+p[3][0])/4, cyy=(p[0][1]+p[1][1]+p[2][1]+p[3][1])/4;
        ctx.fillStyle=cs('--plate-bg');ctx.font='700 24px ui-monospace,monospace';
        ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(String(o.i+1),cx,cyy);
      }
    });
  }
  function size(){var r=cv.getBoundingClientRect();var d=window.devicePixelRatio||1;
    W=r.width;H=r.height;
    cv.width=Math.round(W*d);cv.height=Math.round(H*d);
    ctx.setTransform(d,0,0,d,0,0);
    draw();}
  cv.addEventListener('pointerdown',function(e){drag=true;lx=e.clientX;cv.setPointerCapture(e.pointerId);});
  cv.addEventListener('pointermove',function(e){if(!drag)return;yaw+=(e.clientX-lx)*0.006;lx=e.clientX;draw();});
  cv.addEventListener('pointerup',function(){drag=false;});
  window.addEventListener('resize',size);
  size();
})();
"""


def build_canvas_js():
    """臂 ③：canvas 2D 手寫投影 + 可拖曳旋轉。剝掉 script 就會全空。"""
    return CANVAS_JS_TEMPLATE % (STATION_X_MM, NARR_HALFSIZE_MM, ENG_HALFSIZE_MM,
                                 ENG_SOLID_END_MM, ENG_FADE_END_MM, ENG_LIFT_MM)
# @end-figure-spec


CAP = ('同一起事故沿四個轉換點被逐段放大，而換一組詞描述它的那條路全程不變寬、中途就終止。'
       '四格畫的是同一張圖，內容與文字逐字相同，只有立體的做法不同。'
       '<span class="notesrc"><span class="lb">Note</span>　管寬是傳播規模的示意，'
       '不對應任何實際的觸及量測；四個轉換點的時序來自節目口述，未經獨立查證。'
       '上方那條管是節目中提出的反事實推論，不是已發生的事。</span>'
       '<span class="notesrc"><span class="lb">Source</span>　'
       'All-In Podcast 第 288 集，<code>19:56–30:33</code>。</span>')


def figure(n, body, extra=""):
    return ('<figure class="wide">\n'
            '<div class="probe-head"><span class="pn-big">%s</span>%s</div>\n'
            '<div class="stage">%s</div>\n'
            '<figcaption>%s</figcaption>\n</figure>\n' % (n, extra, body, CAP))


HEAD = open(__file__.replace("build_probe.py", "head.part"), encoding="utf-8").read()
TAIL = open(__file__.replace("build_probe.py", "tail.part"), encoding="utf-8").read()


def main():
    canvas = ('<canvas id="c3" width="%d" height="%d" '
              'aria-label="可拖曳旋轉的立體管道圖"></canvas>'
              '<noscript><p class="ns">這一格需要 JavaScript 才會出現。'
              '其餘三格不需要。</p></noscript>' % (int(CANVAS_W_PX), int(CANVAS_H_PX)))
    print(HEAD)
    print(figure("①", build_iso_svg("A")))
    print(figure("②", build_css3d()))
    print(figure("③", canvas, '<span class="hint">可以用手指左右拖曳</span>'))
    print(figure("④", build_iso_svg("D")))   # 與 ① 逐像素相同，只有 gradient id 不同
    print(TAIL % build_canvas_js())


if __name__ == "__main__":
    main()
