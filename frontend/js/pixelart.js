/**
 * Pixel-art sprites drawn as SVG rects from tiny character maps.
 * Each character in a map is one pixel; "." is transparent.
 */

const SVG_NS = "http://www.w3.org/2000/svg";

const PALETTE = {
  G: "#3f9a4a", g: "#2b6e36", L: "#6fcf5e", T: "#7a4a2a", t: "#5a341c",
  H: "#c0563a", S: "#f1c39b", E: "#20232f", C: "#3d6fd1", c: "#2c50a0",
  B: "#6b4524", P: "#2a2f4a", K: "#20232f", M: "#0b0d12", m: "#7bd36f",
  W: "#f4f1e8", w: "#cfd6ea", Y: "#f2c45a", y: "#c48a26", R: "#ef6b6b",
  D: "#56607f", d: "#3e4663", s: "#e6edf7", N: "#5b8def", n: "#3a62c4", Q: "#8e97c9", U: "#151824", O: "#2f8fd8", o: "#1f6aa8",
};

export const SPRITES = {
  tree: [
    "....G....",
    "...GLG...",
    "..GGLGG..",
    "..GGGgG..",
    ".GGLGGGG.",
    ".GGGGGgG.",
    "GGLGgGGGG",
    "GgGGGGGgG",
    ".GGgGGGG.",
    "....T....",
    "....t....",
    "...TTT...",
  ],
  hero: [
    "..HHHH..",
    ".HHHHHH.",
    ".HSSSSH.",
    "..SESE..",
    "..SSSS..",
    ".CCCCCC.",
    "SCCcCCCS",
    "SCBBBBCS",
    "..CCCC..",
    "..PP.PP.",
    "..PP.PP.",
    ".BB..BB.",
  ],
  // Our own pixel penguin (Linux's traditional mascot is a penguin).
  penguin: [
    ".....QQQQ.....",
    "....QUUUUQ....",
    "...QUUUUUUQ...",
    "...QWWUUWWQ...",
    "...QWEUUEWQ...",
    "...QUUYYUUQ...",
    "..QUUYYYYUUQ..",
    "..QUWWWWWWUQ..",
    ".QUWWWWWWWWUQ.",
    "QUUWWWWWWWWUUQ",
    "QUUWWWWWWWWUUQ",
    ".QUWWWWWWWWUQ.",
    "..QUWWWWWWUQ..",
    "..YYYY..YYYY..",
  ],
  terminal: [
    "KKKKKKKKKKKK",
    "KMMMMMMMMMMK",
    "KMmmMMMMMMMK",
    "KMMMmMMMMMMK",
    "KMmmMMMMMMMK",
    "KMMMMMmmmMMK",
    "KMMMMMMMMMMK",
    "KKKKKKKKKKKK",
    "....KKKK....",
    "..KKKKKKKK..",
  ],
  cloud: [
    "....WWW.....",
    "..WWWWWWW...",
    ".WWWWWWWWWW.",
    "wwWWWWWWWWWw",
    ".wwwwwwwwww.",
  ],
  container: [
    "..........W.",
    ".OOOOOOOO.W.",
    ".OoOoOoOo.W.",
    ".OOOOOOOO.W.",
    ".OoOoOoOoW..",
    "OOOOOOOOOOOO",
    "OoooooooooOO",
    ".OOOOOOOOOO.",
    "..ooooooooo.",
  ],
  wheel: [
    ".....N.....",
    "...NNNNN...",
    "..N..N..N..",
    ".N...N...N.",
    ".N..nnn..N.",
    "NNNNnWnNNNN",
    ".N..nnn..N.",
    ".N...N...N.",
    "..N..N..N..",
    "...NNNNN...",
    ".....N.....",
  ],
  trophy: [
    "YYYYYYYYYY",
    "YyYYYYYYyY",
    "Y.YYYYYY.Y",
    ".YYYYYYYY.",
    "..YYYYYY..",
    "...YYYY...",
    "....yy....",
    "....yy....",
    "..YYYYYY..",
    "..yyyyyy..",
  ],
  star: [
    "....Y....",
    "...YYY...",
    "YYYYYYYYY",
    ".YYYYYYY.",
    "..YYYYY..",
    ".YYY.YYY.",
    "YY.....YY",
  ],
};

function el(tag, attrs = {}) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  return node;
}

/** Append a sprite's pixels to an SVG group, merging horizontal runs into one rect. */
function drawSprite(group, rows, ox = 0, oy = 0) {
  rows.forEach((row, y) => {
    let x = 0;
    while (x < row.length) {
      const ch = row[x];
      let run = 1;
      while (row[x + run] === ch) run++;
      if (ch !== "." && PALETTE[ch]) {
        group.append(el("rect", { x: ox + x, y: oy + y, width: run, height: 1, fill: PALETTE[ch] }));
      }
      x += run;
    }
  });
  return group;
}

/** A standalone sprite as an <svg> scaled by CSS (keeps hard pixel edges). */
export function sprite(name, className = "sprite") {
  const rows = SPRITES[name];
  const svg = el("svg", {
    viewBox: `0 0 ${rows[0].length} ${rows.length}`,
    class: className,
    "shape-rendering": "crispEdges",
    "aria-hidden": "true",
  });
  drawSprite(svg, rows);
  return svg;
}

function mountain(group, cx, height, base, body, snow) {
  for (let y = 0; y < height; y++) {
    const half = y;
    const fill = y < 3 ? snow : body;
    group.append(el("rect", { x: cx - half, y: base - height + y, width: half * 2 + 1, height: 1, fill }));
  }
}

/** The home-page world banner: sky, mountains, forest, our penguin and a terminal. */
export function worldScene() {
  const W = 120;
  const H = 40;
  const svg = el("svg", {
    viewBox: `0 0 ${W} ${H}`,
    class: "scene",
    "shape-rendering": "crispEdges",
    role: "img",
    "aria-label": "Pixel-art τοπίο με βουνά, δάσος, έναν πιγκουίνο και ένα τερματικό",
  });

  // Sky in dithered bands.
  [["#1b2140", 0, 10], ["#25305a", 10, 9], ["#33427a", 19, 8], ["#465a9a", 27, 6]].forEach(([fill, y, h]) =>
    svg.append(el("rect", { x: 0, y, width: W, height: h, fill })));
  for (let x = 0; x < W; x += 2) {
    svg.append(el("rect", { x: x + ((x / 2) % 2), y: 18, width: 1, height: 1, fill: "#25305a" }));
  }
  // Stars.
  [[8, 3], [22, 6], [41, 2], [57, 5], [76, 3], [93, 7], [110, 4]].forEach(([x, y]) =>
    svg.append(el("rect", { x, y, width: 1, height: 1, fill: "#e6edf7" })));

  const clouds = el("g", { class: "clouds" });
  drawSprite(clouds, SPRITES.cloud, 14, 8);
  drawSprite(clouds, SPRITES.cloud, 70, 4);
  svg.append(clouds);

  const hills = el("g");
  mountain(hills, 30, 18, 33, "#3e4663", "#e6edf7");
  mountain(hills, 52, 13, 33, "#56607f", "#e6edf7");
  mountain(hills, 88, 20, 33, "#3e4663", "#e6edf7");
  mountain(hills, 106, 12, 33, "#56607f", "#e6edf7");
  svg.append(hills);

  // Ground.
  svg.append(el("rect", { x: 0, y: 33, width: W, height: 1, fill: "#6fcf5e" }));
  svg.append(el("rect", { x: 0, y: 34, width: W, height: 6, fill: "#3f9a4a" }));
  for (let x = 1; x < W; x += 4) svg.append(el("rect", { x, y: 36 + (x % 3), width: 1, height: 1, fill: "#2b6e36" }));
  // Path to the terminal.
  svg.append(el("rect", { x: 58, y: 34, width: 30, height: 2, fill: "#b08856" }));

  const forest = el("g");
  [2, 9, 16, 98, 106, 112].forEach((x, i) => drawSprite(forest, SPRITES.tree, x, 22 + (i % 2)));
  svg.append(forest);

  drawSprite(svg, SPRITES.terminal, 86, 24);
  const hero = el("g", { class: "hero-sprite" });
  drawSprite(hero, SPRITES.penguin, 51, 20);
  svg.append(hero);
  return svg;
}
