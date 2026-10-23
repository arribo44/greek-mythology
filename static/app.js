// LinkedImmortals — front-end (vanilla JS, routage par hash)
// Les textes de l'interface viennent de i18n.js (t()) ; les données arrivent de l'API
// dans la langue courante (paramètre lang). « name » reste l'identifiant anglais d'un
// personnage, « label » son nom affiché.

const CLAN_STYLE = {
  "Olympien":   ["#f3d27a", "#b8862b", "🏛️"],
  "Titan":      ["#c9b7a0", "#6e5640", "🗿"],
  "Primordial": ["#8e7fc9", "#2f2563", "🌌"],
  "Nymphe":     ["#a9d8a2", "#3e7c48", "🌿"],
  "Aquatique":  ["#9fd3e6", "#2c6f93", "🌊"],
  "Monstre":    ["#d99b8c", "#7b2f22", "👹"],
  "Géant":      ["#c4b59b", "#5a4d38", "🏔️"],
  "Allégorie":  ["#e3c6e8", "#7d4f86", "💭"],
  "Daïmon":     ["#b9b2c9", "#4a4260", "👻"],
  "Vent":       ["#dbe8ef", "#6c8ea3", "🌬️"],
  "Demi-dieu":  ["#f6e2a6", "#a0742a", "✨"],
  "Oracle":     ["#d4c3f0", "#5a3f8f", "🔮"],
  "Chthonien":  ["#9a9a9a", "#2b2b2b", "🕳️"],
  "Divinité":   ["#efd6a8", "#9a6b35", "🏺"],
  "Mortel":     ["#e8cfae", "#8a5a2b", "🧔"],
};

const EMOJI = {
  Zeus: "⚡", Hera: "👑", Athena: "🦉", Poseidon: "🔱", Hades: "💀", Hermes: "🪽", Apollo: "☀️",
  Artemis: "🏹", Aphrodite: "🌹", Ares: "⚔️", Hephaestus: "🔨", Dionysus: "🍇", Demeter: "🌾",
  Persephone: "🌸", Hestia: "🏠", Sisyphus: "🪨", Narcissus: "🪞", Prometheus: "🔥", Atlas: "🌍",
  Medusa: "🐍", Cerberus: "🐕", Charon: "⛵", Icarus: "🪶", Heracles: "🦁", Achilles: "🛡️",
  Odysseus: "🎠", Orpheus: "🎵", Midas: "🪙", Pandora: "📦", Eros: "💘", Nike: "🏆", Cassandra: "🔮",
  Gaia: "🌍", Chaos: "🌀", Nyx: "🌙", Helios: "🌞", Echo: "🗣️", Daedalus: "🛠️",
  Minotaur: "🐂", Perseus: "🗡️", Theseus: "🧶", Arachne: "🕷️", Cronus: "⏳", Uranus: "✨", Pan: "🐐",
  Hypnos: "😴", Thanatos: "⚰️", Tantalus: "🍎", Ixion: "🎡", Nemesis: "⚖️", Eos: "🌅", Iris: "🌈",
  Penelope: "🧵", Paris: "🍏", Ariadne: "🧶", Asclepius: "⚕️", Triton: "🐚",
  Jason: "🐏", Medea: "🧪", Oedipus: "🦶", Antigone: "🕯️", Circe: "🐖", Calypso: "🏝️",
  Polyphemus: "👁️", Tyche: "🎲", Morpheus: "💤", Aeolus: "🌬️", Leto: "🌴", Maia: "⭐", Rhea: "🪨",
  // héros de la guerre de Troie
  Patroclus: "🎭",          // combat déguisé en Achille
  Aeneas: "🏃",             // fuit Troie en flammes
  Anchises: "🧓",           // porté sur le dos d'Énée hors de Troie
  "Ajax the Great": "🧽",   // homonyme d'un produit ménager
  Priam: "🏰",              // roi de Troie
  Agamemnon: "🦁",          // porte des Lions de Mycènes
  Menelaus: "💔",           // Hélène partie avec Pâris
  "Helen of Troy": "💄",    // le visage qui lança mille navires
  Nestor: "📜",             // le vieux conseiller qui raconte sa jeunesse
  Diomedes: "🗡️",          // blesse Aphrodite et Arès
  Thetis: "🐚",             // Néréide, mère d'Achille
  Peleus: "💍",             // ses noces, où éclate la pomme de discorde
  Telamon: "🛶",            // Argonaute
  Pelops: "🏇",             // la course de chars truquée contre Œnomaos
  Tydeus: "🧠",             // dévore la cervelle de Mélanippe
  Hector: "🐎",             // « dompteur de chevaux »
  Elektra: "⚱️",            // pleure sur l'urne d'Oreste
  Atreus: "🍲",             // le festin de Thyeste
  Agenor: "🔍",             // envoie ses fils chercher Europe
  Cadmus: "🐉",             // tue le dragon et sème ses dents
  Europa: "🐂",             // enlevée par Zeus en taureau
  Minos: "🧑‍⚖️",            // juge des morts
  "Augeias of Elis": "💩",  // les écuries d'Augias
  Tyndareus: "🥚",          // père adoptif des enfants nés des œufs de Léda
  Admetus: "🪦",            // Alceste meurt à sa place
  Amphiaraus: "🕳️",         // englouti par la terre avec son char
  Aeacus: "🐜",             // les Myrmidons, nés de fourmis
  Oeneus: "🍷",             // reçoit la vigne de Dionysos
  Glaucus: "🐟",            // pêcheur devenu dieu marin
  Styx: "🤞",               // les dieux jurent par le Styx
  Achelous: "🦬",           // sa corne arrachée devient la corne d'abondance
  Boreas: "🥶",             // vent du nord
  Amphitryon: "👥",         // Zeus prend son apparence
  "Argus Panoptes": "👀",   // le géant aux cent yeux
  Pelias: "🩴",             // redoute l'homme à une seule sandale
  Laertes: "🍐",            // le vieux père d'Ulysse, jardinier dans son verger
  Phrixus: "🐑",            // s'envole sur le bélier à la toison d'or
  Danaus: "🔪",             // ses filles tuent leurs maris la nuit des noces
  Creon: "🚫",              // interdit d'enterrer Polynice
  Nereus: "🧜‍♂️",            // le Vieillard de la mer
  Neoptolemus: "🔥",        // Pyrrhus, « le roux », au sac de Troie
  Teucer: "🎯",             // archer abrité derrière le bouclier d'Ajax
  Tartarus: "⛓️",           // la prison des Titans
  Phineus: "🍽️",            // les Harpies lui volent ses repas
  Chiron: "🎓",             // le précepteur des héros
  Lycaon: "🐺",             // changé en loup par Zeus
  Eurystheus: "🏺",         // se cache dans une jarre devant Héraclès
  Eurydice: "🔙",           // Orphée se retourne
  Polynices: "🤺",          // les frères ennemis s'entretuent
  Orestes: "😱",            // poursuivi par les Érinyes
  Philoctetes: "🩹",        // sa blessure qui empeste
  Typhon: "🌋",             // enseveli sous l'Etna
  Aeson: "🫕",              // rajeuni dans le chaudron de Médée
  Amphion: "🧱",            // les murs de Thèbes montent au son de sa lyre
  Alkmene: "🌃",            // Zeus prolonge la nuit avec elle
  Hyperion: "🌄",           // Titan de la lumière
  Ino: "🧣",                // devenue Leucothée, elle prête son voile à Ulysse
  Protesilaus: "🥇",        // premier débarqué à Troie, premier tué
  Capaneus: "🪜",           // foudroyé en haut de son échelle devant Thèbes
  Leda: "🦢",               // Zeus changé en cygne
  Meleager: "🪵",           // sa vie dépend d'un tison
  Atalanta: "🏃‍♀️",          // la course perdue à cause des pommes d'or
  Pirithous: "🪑",          // collé pour toujours au trône de l'oubli
  Laomedon: "💸",           // refuse de payer Apollon et Poséidon
  Machaon: "🩺",            // médecin des Grecs devant Troie
  Nilus: "🐊",              // le Nil
  Caeneus: "🔄",            // changé de femme en homme invulnérable
  Themis: "⚖️",             // la justice divine
  Calchas: "🐦",            // devin qui lit le vol des oiseaux
  Amphitrite: "🧜‍♀️",        // reine de la mer
  Deucalion: "🌧️",          // survivant du Déluge
  Hecuba: "🐕",             // changée en chienne
  Clytemnestra: "🪓",       // tue Agamemnon à son retour
  "Aeëtes": "🔑",           // gardien de la toison d'or
  Erato: "💌",              // muse de la poésie amoureuse
  Oceanus: "🌐",            // le fleuve qui entoure le monde
  Tiphys: "🧭",             // pilote de l'Argo
  Enyo: "💥",               // déesse de la destruction
  Tiresias: "🦯",           // le devin aveugle
  Autolycus: "🦹",          // le prince des voleurs
  Harmonia: "📿",           // son collier maudit
  Semele: "☄️",             // foudroyée en voyant Zeus dans sa gloire
  Erebos: "🌑",             // les ténèbres
  Eileithyia: "👶",         // déesse des accouchements
  Rhadamanthus: "⚖️",       // juge des morts
  Lynceus: "🔭",            // voit à travers les murs
  Antilochus: "🏁",         // la course de chars des funérailles de Patrocle
  Butes: "🐝",              // l'Argonaute apiculteur
  Alpheus: "💦",            // poursuit Aréthuse sous la mer
  Amycus: "🥊",             // roi boxeur, battu par Pollux
  Idas: "🤼",               // ose affronter Apollon pour Marpessa
  Ancaeus: "🐗",            // tué par le sanglier de Calydon
  Athamas: "🦌",            // dans sa folie, prend son fils pour un cerf
  Mopsus: "🐍",             // le devin meurt d'une morsure de serpent en Libye
  Iphiclus: "🌾",           // court sur les épis sans les courber
  Aethalides: "💾",         // héraut doté d'une mémoire infaillible, même chez Hadès
  Neleus: "👶",             // abandonné à la naissance avec son jumeau Pélias
  Io: "🐄",                 // changée en génisse par Zeus pour échapper à Héra
};

const DEFAULT_ME = "Athena";
let ME = localStorage.getItem("li-me") || DEFAULT_ME;
const connectedLocal = new Set(JSON.parse(localStorage.getItem("li-connected") || "[]"));
const app = document.getElementById("app");
let feedPage = 0;
let network = null;
let leafletMap = null;
const PLACE_COLORS = { birth: "#3d7f4f", death: "#c0392b", residence: "#276a9c", burial: "#8a5a2b", visit: "#8e5ba6" };
const PLACE_ORDER = Object.keys(PLACE_COLORS);
// source d'un lien vers un lieu, affichée quand elle ne vient pas seulement de Wikidata (« Apollodore III, 190 »)
const placeSource = s => s && s !== "Wikidata" ? ` <span class="muted small" title="${esc(s)}">· ${esc(s.replace(/^Wikidata ; /, ""))}</span>` : "";
let LABELS_FR = {};   // nom anglais -> nom français, pour les noms seuls (chemins, via, duos…)
let PORTRAITS = {};   // nom anglais -> vignette personnalisée (DATAS/IMAGES_JC), prioritaire sur l'emoji…
const EMOJI_FIRST = new Set([]);   // …sauf pour ces personnages (noms anglais)
const portraitOf = p => !EMOJI_FIRST.has(p.name) && PORTRAITS[p.name];

// ---------------------------------------------------------------- utilitaires

const esc = s => String(s ?? "").replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const enc = encodeURIComponent;
const api = path => fetch(`/api${path}${path.includes("?") ? "&" : "?"}lang=${LANG}`)
  .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const fmt = n => Number(n).toLocaleString(LANG === "fr" ? "fr-FR" : "en-US");

// nom affiché d'un personnage : objet de l'API (label) ou simple identifiant
const nm = p => typeof p === "string" ? (LANG === "fr" && LABELS_FR[p]) || p : p.label || nm(p.name);
const clanLabel = c => t(`clan.${c}`);

function emojiFor(p) {
  if (EMOJI[p.name]) return EMOJI[p.name];
  if (p.clan === "Mortel") return p.gender && p.gender.startsWith("female") ? "👩" : (p.gender && p.gender.startsWith("male") ? "🧔" : "🧑");
  return (CLAN_STYLE[p.clan] || CLAN_STYLE["Divinité"])[2];
}

function avatar(p, size = "") {
  const [c1, c2] = CLAN_STYLE[p.clan] || CLAN_STYLE["Divinité"];
  const title = p.clan ? `${nm(p)} · ${clanLabel(p.clan)}` : nm(p);
  const inner = portraitOf(p) ? `<img class="avatar-img" src="${esc(portraitOf(p))}" alt="">` : emojiFor(p);
  return `<span class="avatar ${size}" style="--c1:${c1};--c2:${c2}" title="${esc(title)}">${inner}</span>`;
}

// nœud vis-network : vignette personnalisée si elle existe, sinon point coloré avec emoji dans le libellé
function visNode(n, base) {
  const [c1, c2] = CLAN_STYLE[n.clan] || CLAN_STYLE["Divinité"];
  if (!portraitOf(n)) return { ...base, label: `${emojiFor(n)} ${base.label}` };
  return { ...base, shape: "circularImage", image: portraitOf(n), imagePadding: 5,
    color: { ...(base.color || {}), background: c1, border: (base.color && base.color.border) || c2 } };
}

const sourceBadge = s => s ? `<span class="src src-${esc(s.split("+")[0])}" title="${esc(t("src.title", { s: t(`src.${s}`) }))}">${s === "graphe" ? t("src.graph_short") : s.includes("+") ? "WD+desc" : s === "wikidata" ? "WD" : "desc"}</span>` : "";
const mythLink = (key, name) => `<a class="chip" href="#/myth/${enc(key)}">🏺 ${esc(name)}</a>`;
const workLink = (key, title) => `<a href="#/work/${enc(key)}"><i>${esc(title)}</i></a>`;
const genreIcon = g => g === "Epic" ? "⚔️" : g === "Dialogue" ? "🎭" : "📜";

const link = name => `#/in/${enc(name)}`;
const nameLink = p => typeof p === "string" ? `<a href="${link(p)}">${esc(nm(p))}</a>` : `<a href="${link(p.name)}">${esc(nm(p))}</a>`;
const bold = html => `<b>${html}</b>`;

function personRow(p, extra = "", size = "") {
  return `<div class="person">${avatar(p, size)}<div class="who">
    <a class="nm" href="${link(p.name)}">${esc(nm(p))}</a>
    <span class="hl">${esc(extra || p.headline)}</span></div></div>`;
}

function richText(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
    .replace(/\*(.+?)\*/g, "<i>$1</i>")
    .replace(/(^|\s)(#[\p{L}\d]+)/gu, '$1<span class="tag">$2</span>')
    .replace(/\n/g, "<br>");
}

function toast(msg) {
  const el = document.createElement("div");
  el.className = "toast"; el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2600);
}

function connectButton(p) {
  const done = connectedLocal.has(p.name);
  return `<button class="btn ${done ? "done" : ""}" data-connect="${esc(p.name)}" data-label="${esc(nm(p))}">${done ? t("btn.pending") : t("btn.connect")}</button>`;
}

function setMe(name) {
  ME = name;
  localStorage.setItem("li-me", name);
  feedPage = 0;
  refreshHeader();
}

const degreeLabel = path => path ? t("degree.n", { d: path.length - 1 }) : "";

// ---------------------------------------------------------------- événements globaux

document.addEventListener("click", e => {
  const c = e.target.closest("[data-connect]");
  if (c) {
    connectedLocal.add(c.dataset.connect);
    localStorage.setItem("li-connected", JSON.stringify([...connectedLocal]));
    c.classList.add("done"); c.textContent = t("btn.pending");
    toast(t("toast.invite", { n: c.dataset.label }));
    return;
  }
  const like = e.target.closest("[data-like]");
  if (like) {
    like.classList.toggle("liked");
    const cnt = like.closest(".post").querySelector(".likes");
    if (cnt) cnt.textContent = fmt(+cnt.dataset.n + (like.classList.contains("liked") ? 1 : 0));
    return;
  }
  const tabBtn = e.target.closest("[data-tab]");
  if (tabBtn) {
    const card = tabBtn.closest(".card");
    card.querySelectorAll("[data-tab]").forEach(b => b.classList.toggle("on", b === tabBtn));
    card.querySelectorAll("[data-panel]").forEach(el => { el.hidden = el.dataset.panel !== tabBtn.dataset.tab; });
    return;
  }
  const act = e.target.closest("[data-toast]");
  if (act) { toast(act.dataset.toast); return; }
  const become = e.target.closest("[data-become]");
  if (become) {
    setMe(become.dataset.become);
    toast(t("toast.become", { n: nm(become.dataset.become) }));
    location.hash = "#/";
  }
  if (!e.target.closest(".search")) document.querySelectorAll(".dropdown").forEach(d => d.classList.add("hidden"));
});

// La recherche affiche les noms dans la langue courante ; l'identifiant est gardé dans data-name.
function bindSearch(input, results, onPick) {
  let timer;
  input.addEventListener("input", () => {
    delete input.dataset.name;
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const v = input.value.trim();
      if (v.length < 2) { results.classList.add("hidden"); return; }
      const rows = await api(`/search?q=${enc(v)}`);
      results.innerHTML = rows.length
        ? rows.map(p => `<div class="person" data-pick="${esc(p.name)}" data-label="${esc(nm(p))}">${avatar(p, "sm")}<div class="who">
            <span class="nm">${esc(nm(p))}</span><span class="hl">${esc(p.headline)} · ${t("search.connections", { n: fmt(p.connections) })}</span></div></div>`).join("")
        : `<div class="person muted">${t("search.none")}</div>`;
      results.classList.remove("hidden");
    }, 180);
  });
  results.addEventListener("click", e => {
    const el = e.target.closest("[data-pick]");
    if (!el) return;
    results.classList.add("hidden");
    input.value = el.dataset.label;
    input.dataset.name = el.dataset.pick;
    onPick(el.dataset.pick);
  });
}

bindSearch(document.getElementById("search"), document.getElementById("search-results"),
  name => { location.hash = link(name); document.getElementById("search").value = ""; });

async function refreshHeader() {
  const me = await api(`/me/${enc(ME)}`);
  document.getElementById("me-avatar").innerHTML = avatar(me, "xs");
  const notes = await api(`/notifications/${enc(ME)}`);
  const b = document.getElementById("notif-badge");
  b.textContent = notes.length; b.classList.toggle("hidden", !notes.length);
}

// textes fixes de index.html (attribut data-i18n) et bouton de langue
function applyStaticTexts() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  document.getElementById("site-footer").innerHTML = t("footer.thanks");
  const sw = document.getElementById("lang-switch");
  sw.textContent = LANG === "fr" ? "EN" : "FR";
  sw.title = t("lang.switch");
}

document.getElementById("lang-switch").addEventListener("click", () => {
  setLang(LANG === "fr" ? "en" : "fr");
  applyStaticTexts();
  refreshHeader();
  route();
});

// ---------------------------------------------------------------- page d'accueil

function renderPost(p) {
  const a = p.author;
  const A = bold(nameLink(a));
  if (p.kind === "post") {
    const com = p.comment ? `<div class="comment">${avatar(p.comment.author, "sm")}<div class="bubble">
        <b>${nameLink(p.comment.author)}</b>${richText(p.comment.text)}</div></div>` : "";
    return `<article class="card post"><div class="head">${avatar(a)}<div class="meta">
        <div class="title">${A} ${esc(p.action)}</div>
        <div class="sub">${esc(a.position)}</div></div></div>
      <div class="body">${richText(p.text)}</div>
      <div class="counts">👍💡❤️ <span class="likes" data-n="${p.likes}">${fmt(p.likes)}</span></div>
      <div class="actions">
        <button data-like>${t("post.like")}</button>
        <button data-toast="${esc(t("toast.comment"))}">${t("post.comment")}</button>
        <button data-toast="${esc(t("toast.share"))}">${t("post.share")}</button>
      </div>${com}</article>`;
  }
  let text = "";
  if (p.kind === "connect")
    text = `${t("feed.connect", { a: A, b: bold(nameLink(p.target)) })}<div class="sub">${t("feed.connect_sub", { m: fmt(p.mentions), w: p.works })}</div>`;
  else if (p.kind === "endorse")
    text = t("feed.endorse", { a: A, b: bold(nameLink(p.target)), s: `<span class="pill">${esc(p.skill)}</span>` });
  else if (p.kind === "press")
    text = `${t("feed.press", { a: A, t: `<i>${esc(p.work.title)}</i>`, au: esc(p.work.author) })}
            <div class="sub">${t("feed.press_sub", { p: esc(p.work.period_label), m: p.work.m })}</div>`;
  else if (p.kind === "anniversary")
    text = t("feed.anniversary", { a: A, y: fmt(p.years), c: esc(p.company) });
  else if (p.kind === "family") {
    const B = bold(nameLink(p.target));
    if (p.event === "birth") text = t("feed.birth", { a: A, b: B });
    else if (p.event === "wedding") text = t("feed.wedding", { a: A, b: B, n: fmt(1000 + p.likes) });
    else text = t("feed.reunion", { a: A, b: B, half: p.target.half });
    text += `<div class="sub">${t("feed.kin_sub", { src: sourceBadge(p.source), a: `<a href="#/family/${enc(a.name)}">${esc(nm(a))}</a>` })}</div>`;
  }
  else if (p.kind === "job")
    text = t("feed.job", { a: A, p: esc(p.position) });
  return `<article class="card post simple"><div class="head">${avatar(a)}<div class="meta title">${text}</div></div></article>`;
}

async function loadFeed(container) {
  const posts = await api(`/feed/${enc(ME)}?page=${feedPage}`);
  container.insertAdjacentHTML("beforeend", posts.map(renderPost).join(""));
}

async function pageHome() {
  const [me, sugg, side] = await Promise.all([
    api(`/me/${enc(ME)}`), api(`/suggestions/${enc(ME)}`), api(`/sidebar/${enc(ME)}`)]);
  feedPage = 0;
  app.innerHTML = `<div class="layout">
    <aside class="col left">
      <div class="card flush me-card">
        <div class="banner"></div>${avatar(me, "lg")}
        <h2><a href="${link(me.name)}" style="color:inherit">${esc(nm(me))}</a></h2>
        <div class="hl">${esc(me.position)}</div>
        <div class="stats">
          <div>${t("home.connections")} <b>${fmt(me.connections)}</b></div>
          <div>${t("home.views")} <b>${fmt(me.views)}</b></div>
          <div>${t("home.offerings")} <b>${fmt(me.impressions)}</b></div>
        </div>
      </div>
      <div class="card sidenav">
        <a href="#/">${t("nav.home")}</a>
        <a href="#/mythspace">${t("nav.mythspace")}</a>
        <a href="#/library">${t("nav.library")}</a>
        <a href="#/family/${enc(me.name)}">${t("home.family")}</a>
        <a href="#/jobs">${t("home.events")} <span class="muted">${side.events.length ? fmt(side.events[0].mentions * 2) : 0}</span></a>
        <a href="#/notifications">${t("nav.notifications")}</a>
      </div>
      <div class="card">
        <h3>${t("home.events_title")}</h3>
        ${side.events.map(e => `<div class="event"><a href="#/myth/${enc(e.key)}">${esc(e.name)}</a> <span class="when">– ${esc(e.when)}</span></div>`).join("") || `<div class="muted small">${t("home.no_events")}</div>`}
      </div>
    </aside>

    <section class="col">
      <div class="card composer">${avatar(me, "sm")}<input id="composer" placeholder="${esc(t("home.composer", { n: nm(me) }))}"></div>
      <div id="feed" class="col"></div>
      <button class="view-more" id="more">${t("btn.seemore")}</button>
    </section>

    <aside class="col right">
      <div class="card">
        <h3>${t("home.add")}</h3>
        <div class="muted small" style="margin:-6px 0 6px">${t("home.add_sub")}</div>
        ${sugg.map(p => `<div class="suggest">${personRow(p)}
          <div class="small muted" style="margin:4px 0 6px 58px">${t("home.mutual", { n: fmt(p.mutual) })}</div>
          <div style="margin-left:58px">${connectButton(p)}</div></div>`).join("")}
        <div style="text-align:center;margin-top:8px"><a href="#/network">${t("btn.seeall")}</a></div>
      </div>
      <div class="card">
        <h3>${t("home.trending")}</h3>
        ${side.trending.map(x => `<div class="trend">🔍 <span><a href="#/myth/${enc(x.key)}">${esc(x.name)}</a><br><span class="muted small">${t("home.involved", { n: x.people })}</span></span></div>`).join("")}
        <div class="trend">🔍 <span>soul escape clauses</span></div>
      </div>
      <div class="footer">${t("home.footer")}</div>
    </aside>
  </div>`;

  const feed = document.getElementById("feed");
  await loadFeed(feed);
  document.getElementById("more").onclick = async () => { feedPage++; await loadFeed(feed); };
  document.getElementById("composer").addEventListener("keydown", e => {
    if (e.key !== "Enter" || !e.target.value.trim()) return;
    feed.insertAdjacentHTML("afterbegin", renderPost({
      kind: "post", author: me, action: t("post.just_published"), text: e.target.value, likes: 0, comment: null }));
    e.target.value = "";
    toast(t("toast.published"));
  });
}

// ---------------------------------------------------------------- profil

async function pageProfile(name) {
  const p = await api(`/profile/${enc(name)}?me=${enc(ME)}`);
  const isMe = p.name === ME;
  const mutualNames = p.mutual.slice(0, 2).map(m => esc(nm(m.name))).join(", ");
  const mutual = p.mutual.length ? `<div class="mutual"><span class="stack">${p.mutual.slice(0, 3).map(m => avatar(m, "xs")).join("")}</span>
      ${p.mutual_count > 2 ? t("profile.mutual_many", { names: mutualNames, n: fmt(p.mutual_count - 2) }) : t("profile.mutual_few", { names: mutualNames })}</div>` : "";

  const pathHtml = p.path ? `<div class="card"><h3>${t("profile.how")}</h3>
      <div class="path">${p.path.map((n, i) => `${i ? '<span class="arrow">→</span>' : ""}<a class="step" href="${link(n.name)}">${avatar(n, "sm")}${esc(nm(n))}</a>`).join("")}</div>
      <div class="small muted" style="margin-top:8px">${t("profile.path_note", { d: p.path.length - 1 })}</div></div>`
    : (!isMe && p.connections === 0 ? `<div class="card"><h3>${t("profile.how")}</h3><div class="muted">${t("profile.hermit")}</div></div>` : "");

  // autres noms : celui de l'autre langue, le grec, le latin
  const other = LANG === "fr" ? p.name : p.name_fr;
  const names = [other && other !== nm(p) ? other : null, p.name_el,
    p.name_la && p.name_la !== p.name && p.name_la !== nm(p) ? `${t("info.latin")} ${p.name_la}` : null].filter(Boolean);

  app.innerHTML = `<div class="layout two">
    <section class="col">
      <div class="card flush profile-top">
        <div class="banner"></div>
        <div class="inner">
          ${p.open_to_work ? '<span class="otw">#OpenToWork</span>' : ""}
          ${avatar(p, "xl")}
          <h1>${esc(nm(p))} <span class="degree">${isMe ? t("degree.me") : degreeLabel(p.path)}</span></h1>
          ${names.length ? `<div class="names">${names.map(esc).join(" · ")}</div>` : ""}
          <div class="headline">${esc(p.headline)}</div>
          <div class="headline" style="font-size:15px">💼 ${esc(p.position)}</div>
          <div class="facts">📍 ${esc(p.residence)} · <span class="pill">${esc(clanLabel(p.clan))}</span> ·
            <a href="#/mythspace/${enc(p.name)}">${t("profile.connections", { n: fmt(p.connections) })}</a> · ${t("profile.followers", { n: fmt(p.followers) })}
            ${p.theoi_url ? ` · <a href="${esc(p.theoi_url)}" target="_blank" rel="noopener">${t("profile.theoi")}</a>` : ""}</div>
          ${mutual}
          <div class="btns">
            ${isMe ? `<a class="btn primary" href="#/mythspace/${enc(p.name)}">${t("btn.mynetwork")}</a>`
                   : `${connectButton(p)}<a class="btn" href="#/messaging">${t("btn.message")}</a>
                      <button class="btn" data-become="${esc(p.name)}">${t("btn.become")}</button>`}
            <a class="btn" href="#/mythspace/${enc(p.name)}">${t("btn.mythspace")}</a>
            <a class="btn" href="#/family/${enc(p.name)}">${t("btn.tree")}</a>
          </div>
        </div>
      </div>

      ${infoCard(p)}
      ${familyCard(p)}

      <div class="card"><h3>${t("profile.experience")}</h3>
        ${p.experience.slice(0, 5).map(e => `<div class="exp"><div class="logo-sq">${genreIcon(e.genre)}</div><div>
            <div class="t">${t("profile.role_in", { t: workLink(e.key, e.title) })}</div>
            <div>${esc(e.employer)} · ${t("profile.scenes", { n: e.mentions })}</div>
            <div class="muted small">${esc(e.years)} · ${esc(e.period_label)}</div></div></div>`).join("")
          || `<div class="muted">${t("profile.no_experience")}</div>`}
      </div>

      ${p.books.length ? activityCard(p) : ""}
      ${p.books.length ? bibliographyCard(p) : ""}

      ${p.projects.length ? `<div class="card"><h3>${t("profile.projects")}</h3>
        ${p.projects.map(m => `<div class="exp"><div class="logo-sq">🏺</div><div><div class="t"><a href="#/myth/${enc(m.key)}">${esc(m.name)}</a></div>
          <div class="muted small">${esc(m.author)}, <i>${esc(m.title)}</i> · ${t("profile.interactions_myth", { n: m.mentions })}</div></div></div>`).join("")}</div>` : ""}

      <div class="card"><h3>${t("profile.skills")}</h3>
        ${p.skills.map(s => `<div class="skill"><div class="t">${esc(s.name)}</div>
          <div class="person small muted" style="margin-top:4px"><span class="stack">${s.by.map(n => avatar(n, "xs")).join("")}</span>
          ${s.by.length ? t("profile.endorsed_by", { names: s.by.map(nameLink).join(", "), n: fmt(s.count) }) : t("profile.endorsements", { n: fmt(s.count) })}</div></div>`).join("")}
      </div>

      ${recommendationsCard(p)}
    </section>

    <aside class="col">
      ${pathHtml}
      ${p.places.some(x => x.lat != null) ? `<div class="card"><h3>${t("map.focus", { n: esc(nm(p)) })}</h3>
        <div id="mini-map" class="mini-map"></div>
        <div style="text-align:center;margin-top:8px"><a href="#/map/${enc(p.name)}">${t("map.see")}</a></div></div>` : ""}
      <div class="card"><h3>${t("profile.top")}</h3>
        ${p.top_connections.map(c => `<div class="suggest">${personRow(c, t("profile.collabs", { n: c.mentions }))}</div>`).join("")
          || `<div class="muted">${t("profile.no_connections")}</div>`}
        ${p.connections ? `<div style="text-align:center;margin-top:8px"><a href="#/mythspace/${enc(p.name)}">${t("btn.seegraph")}</a></div>` : ""}
      </div>
    </aside>
  </div>`;
  drawMiniMap(p);
}

// Recommandations = citations Wikiquote : reçues (dites à son sujet / à lui) et données (dites par lui)
function quoteBlock(r, p, mode) {
  const other = mode === "received" ? r.author : r.target;
  const who = other ? avatar(other) : `<span class="avatar">${mode === "received" ? "📜" : "📣"}</span>`;
  let title, sub;
  if (mode === "received") {
    title = other ? nameLink(other) : esc(r.speaker_label || "?");
    sub = other ? esc(other.position) : t("reco.external");
  } else {
    title = other ? `${esc(nm(p))} → ${nameLink(other)}` : esc(nm(p));
    sub = other ? esc(other.position) : t("reco.everyone");
  }
  if (r.generated)
    return `<div class="exp">${who}<div><div class="t">${title}</div><div class="muted small">${sub}</div>
      <div style="margin-top:6px">« ${esc(r.text)} »</div><div class="muted small" style="margin-top:4px">${t("reco.generated")}</div></div></div>`;
  const source = [r.work && `<i>${esc(r.work)}</i>`, esc(r.section)].filter(Boolean).join(", ");
  return `<div class="exp quote">${who}<div style="flex:1;min-width:0">
      <div class="t">${title} ${r.lang !== LANG ? `<span class="pill small">${esc(r.lang)}</span>` : ""}</div>
      <div class="muted small">${sub}</div>
      <blockquote>${esc(r.text).replace(/\n/g, "<br>")}</blockquote>
      ${r.context ? `<div class="muted small">${esc(r.context)}</div>` : ""}
      <div class="muted small">${source ? `${source} · ` : ""}<a href="${esc(r.url)}" target="_blank" rel="noopener">Wikiquote</a></div>
      ${r.original ? `<details><summary>${t("reco.original", { l: r.original_lang })}</summary><blockquote class="grc" lang="${esc(r.original_lang)}">${esc(r.original).replace(/\n/g, "<br>")}</blockquote></details>` : ""}
    </div></div>`;
}

function recommendationsCard(p) {
  const { received, given } = p.recommendations;
  if (!received.length && !given.length) return "";
  const first = received.length ? "received" : "given";
  const tab = (id, items) => items.length
    ? `<button class="tab ${id === first ? "on" : ""}" data-tab="${id}">${t(`reco.${id}`)} (${items.length})</button>` : "";
  const panel = (id, items) => `<div class="tab-panel" data-panel="${id}" ${id === first ? "" : "hidden"}>
    ${items.map(r => quoteBlock(r, p, id)).join("")}</div>`;
  return `<div class="card reco"><h3>${t("profile.recommendations")}</h3>
    <div class="tabs">${tab("received", received)}${tab("given", given)}</div>
    ${panel("received", received)}${panel("given", given)}
  </div>`;
}

function pills(label, items) {
  return items && items.length ? `<div class="aliases"><span class="muted small">${label}</span>${items.map(a => `<span class="pill">${esc(a)}</span>`).join("")}</div>` : "";
}

function infoCard(p) {
  const sentence = s => s ? esc(s[0].toUpperCase() + s.slice(1)) + "." : "";
  // description principale dans la langue choisie, l'anglaise en complément quand on lit en français
  const lead = LANG === "fr" ? p.desc_fr : p.description;
  const second = LANG === "fr" && p.desc_fr ? p.description : null;
  const links = [
    p.frwiki && `<a href="https://fr.wikipedia.org/wiki/${enc(p.frwiki)}" target="_blank" rel="noopener">${t("info.wiki_fr")}</a>`,
    p.enwiki && `<a href="https://en.wikipedia.org/wiki/${enc(p.enwiki)}" target="_blank" rel="noopener">${t("info.wiki_en")}</a>`,
    p.qid && `<a href="https://www.wikidata.org/wiki/${enc(p.qid)}" target="_blank" rel="noopener">Wikidata ${esc(p.qid)}</a>`,
    p.theoi_url && `<a href="${esc(p.theoi_url)}" target="_blank" rel="noopener">Theoi</a>`,
  ].filter(Boolean);
  const scenes = p.books.reduce((a, b) => a + b.mentions, 0);
  return `<div class="card info"><h3>${t("info.title")}</h3><div class="info-grid"><div>
      <div class="lead">${sentence(lead || p.description) || t("info.discreet")}</div>
      ${second ? `<div class="muted small">${sentence(second)}</div>` : ""}
      <dl class="facts-list">
        <dt>${t("info.clan")}</dt><dd>${esc(clanLabel(p.clan))} <span class="muted small">(${esc(p.type)})</span></dd>
        <dt>${t("info.residence")}</dt><dd>${esc(p.residence)}</dd>
        ${p.same_as.length ? `<dt>${t("info.same_as")}</dt><dd>${p.same_as.map(esc).join(", ")}</dd>` : ""}
        ${p.deity_domains.length || p.domains.length ? `<dt>${t("info.domains")}</dt><dd>${[...p.deity_domains, ...p.domains].map(esc).join(", ")}</dd>` : ""}
        ${p.symbols.length ? `<dt>${t("info.symbols")}</dt><dd>${p.symbols.map(esc).join(", ")}</dd>` : ""}
        ${p.worshipped_by.length ? `<dt>${t("info.worshipped")}</dt><dd>${p.worshipped_by.map(esc).join(", ")}</dd>` : ""}
        ${p.wd_works.length ? `<dt>${t("info.present")}</dt><dd>${p.wd_works.map(esc).join(", ")}</dd>` : ""}
        ${PLACE_ORDER.map(k => {
          const ps = p.places.filter(x => x.kind === k);
          return ps.length ? `<dt>${t(`place.${k}`)}</dt><dd>${ps.map(x => esc(x.name)).join(", ")}</dd>` : "";
        }).join("")}
        <dt>${t("info.mentions")}</dt><dd>${t("info.mentions_val", { w: p.books.length, s: fmt(scenes) })}</dd>
      </dl>
      ${pills(t("info.aka"), p.aliases.slice(0, 12))}
      ${links.length ? `<div class="links">🔗 ${links.join(" · ")}</div>` : ""}
    </div>
    ${p.image ? `<figure class="portrait"><img src="${esc(p.image)}" alt="${esc(nm(p))}" loading="lazy" onerror="this.parentElement.remove()">
      <figcaption>Wikimedia Commons</figcaption></figure>` : ""}
  </div></div>`;
}

function kinRow(x, extra = "") {
  return `<div class="kin">${avatar(x, "sm")}<div class="who"><a class="nm" href="${link(x.name)}">${esc(nm(x))}</a>
    <span class="hl">${extra}${sourceBadge(x.source)}</span></div></div>`;
}

function familyCard(p) {
  const f = p.family;
  const total = f.parents.length + f.spouses.length + f.siblings.length + f.children.length;
  const ext = Object.entries(f.external);
  if (!total && !ext.length) return "";
  const group = (title, items, render, max = 12) => items.length ? `<div class="kin-group"><h4>${title} <span class="muted">${items.length}</span></h4>
      <div class="kin-list">${items.slice(0, max).map(render).join("")}</div>
      ${items.length > max ? `<details><summary>${t("family.more", { n: items.length - max })}</summary><div class="kin-list">${items.slice(max).map(render).join("")}</div></details>` : ""}</div>` : "";
  const spouses = f.spouses.filter(x => x.kind === "spouse"), lovers = f.spouses.filter(x => x.kind !== "spouse");
  const siblingInfo = x => `${x.half ? `${t("family.half")} · ` : ""}${x.via.length ? `${esc(t("family.via", { v: x.via.map(nm).join(", ") }))} ` : ""}`;
  return `<div class="card"><h3>${t("family.title")} <span class="muted small">${t("family.count", { n: total })}</span></h3>
    ${group(t("family.parents"), f.parents, x => kinRow(x, `${t(`kin.${x.role}`)} `))}
    ${group(t("family.spouses"), spouses, x => kinRow(x))}
    ${group(t("family.lovers"), lovers, x => kinRow(x))}
    ${group(t("family.siblings"), f.siblings, x => kinRow(x, siblingInfo(x)))}
    ${group(t("family.children"), f.children, x => kinRow(x))}
    ${f.grandparents.length || f.grandchildren ? `<div class="kin-group small muted">
        ${f.grandparents.length ? `${t("family.grandparents", { names: f.grandparents.map(nameLink).join(", ") })} ` : ""}
        ${f.grandchildren ? t("family.grandchildren", { n: fmt(f.grandchildren) }) : ""}</div>` : ""}
    ${ext.length ? `<div class="kin-group"><h4>${t("family.external")} <span class="muted small">${t("family.external_sub")}</span></h4>
        ${ext.map(([k, items]) => `<div class="small" style="margin:4px 0"><b>${esc(t(`kin.${k}`))}</b> : ${items.map(i => `<a class="chip" href="https://www.wikidata.org/wiki/${enc(i.qid)}" target="_blank" rel="noopener">${esc(i.label)}</a>`).join(" ")}</div>`).join("")}</div>` : ""}
    <div style="margin-top:12px"><a class="btn" href="#/family/${enc(p.name)}">${t("btn.seetree")}</a>
      <span class="muted small" style="margin-left:8px">${t("family.sources")} ${sourceBadge("wikidata")} ${t("family.src_wd")}, ${sourceBadge("description")} ${t("family.src_desc")}, ${sourceBadge("graphe")} ${t("family.src_graph")}</span></div>
  </div>`;
}

function activityCard(p) {
  const max = Math.max(...p.activity.map(a => a.mentions), 1);
  return `<div class="card"><h3>${t("activity.title")}</h3>
    <div class="muted small" style="margin:-6px 0 10px">${t("activity.sub", { n: esc(nm(p)) })}</div>
    ${p.activity.map(a => `<div class="bar-row"><span class="bar-label">${esc(a.period)}<br><span class="muted small">${esc(a.dates)}</span></span>
      <span class="bar"><span style="width:${(100 * a.mentions / max).toFixed(1)}%"></span></span><b>${fmt(a.mentions)}</b></div>`).join("")}
  </div>`;
}

function bibliographyCard(p) {
  const row = b => `<div class="book"><div class="logo-sq">${genreIcon(b.genre)}</div><div style="flex:1;min-width:0">
      <div class="t">${workLink(b.key, b.title)} <span class="muted">— ${esc(b.author)}</span></div>
      <div class="muted small">${esc(b.genre_label)} · ${esc(b.years)} · <b>${t("profile.scenes", { n: b.mentions })}</b></div>
      ${b.episodes.length ? `<div class="chips">${b.episodes.map(e => mythLink(e.key, e.name)).join("")}</div>` : ""}
    </div></div>`;
  const shown = 6;
  return `<div class="card"><h3>${t("biblio.title", { w: p.books.length, n: esc(nm(p)) })}</h3>
    ${p.books.slice(0, shown).map(row).join("")}
    ${p.books.length > shown ? `<details><summary>${t("biblio.more", { n: p.books.length - shown })}</summary>${p.books.slice(shown).map(row).join("")}</details>` : ""}
  </div>`;
}

// ---------------------------------------------------------------- arbre généalogique

async function pageFamily(name) {
  name = name || ME;
  const tree = await api(`/family-tree/${enc(name)}`);
  const label = esc(nm(name));
  app.innerHTML = `<div class="card">
    <h2 class="section-title">${t("tree.title", { n: label })}</h2>
    <div class="tool-row"><div class="search"><input id="ft" type="search" placeholder="${esc(t("tree.search"))}"><div id="ft-r" class="dropdown hidden"></div></div>
      <a class="btn" href="${link(name)}">${t("btn.profile")}</a></div>
    ${tree.nodes.length <= 1 ? `<div class="loading">${t("tree.none", { n: label })}</div>` : `<div id="network" class="tree"></div>`}
    <div class="legend"><span>${t("tree.legend_parent")}</span><span><i style="background:#c0392b"></i>${t("tree.wedding")}</span><span><i style="background:#d58fb0"></i>${t("tree.affair")}</span>
      <span>${t("tree.levels", { n: label })}</span></div>
    ${tree.truncated.length ? `<div class="small muted" style="margin-top:4px">${t("tree.truncated", {
        list: tree.truncated.map(x => t("tree.truncated_item", { shown: x.shown, what: t(`what.${x.what}`), total: x.total })).join(", "),
        link: `<a href="${link(name)}">${t("tree.profile")}</a>` })}</div>` : ""}
    <div class="small muted" style="margin-top:6px">${t("tree.help")}</div>
  </div>`;
  bindSearch(document.getElementById("ft"), document.getElementById("ft-r"), n => { location.hash = `#/family/${enc(n)}`; });
  if (tree.nodes.length <= 1 || !window.vis) return;
  const nodes = tree.nodes.map(n => {
    const [c1, c2] = CLAN_STYLE[n.clan] || CLAN_STYLE["Divinité"];
    return visNode(n, { id: n.name, level: n.level + 2, label: nm(n), title: `${nm(n)} — ${n.headline}`,
      shape: "dot", size: n.name === name ? 26 : 16,
      font: { size: n.name === name ? 20 : 14, face: "Source Sans 3", color: "#2a2620", background: "rgba(251,248,242,.85)" },
      borderWidth: n.name === name ? 4 : 2, color: { border: n.name === name ? "#b88a2e" : c2, background: c1 } });
  });
  const edges = tree.edges.map(e => e.kind === "parent"
    ? { from: e.source, to: e.target, arrows: "to", color: { color: "#a08a6a" }, title: t("tree.parent_edge", { s: t(`src.${e.src}`) }) }
    : { from: e.source, to: e.target, dashes: true, color: { color: e.kind === "spouse" ? "#c0392b" : "#d58fb0" }, width: 2,
        title: e.kind === "spouse" ? t("tree.wedding") : t("tree.affair") });
  if (network) network.destroy();
  network = new vis.Network(document.getElementById("network"), { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) }, {
    layout: { hierarchical: { direction: "UD", sortMethod: "directed", levelSeparation: 140, nodeSpacing: 120, shakeTowards: "roots" } },
    physics: false, edges: { smooth: { type: "cubicBezier", forceDirection: "vertical" } },
    interaction: { hover: true, tooltipDelay: 120 } });
  network.on("doubleClick", ev => { if (ev.nodes.length) location.hash = `#/family/${enc(ev.nodes[0])}`; });
  network.once("afterDrawing", () => network.fit({ animation: false }));
}

// ---------------------------------------------------------------- mythe / épisode

async function pageMyth(key) {
  const e = await api(`/episode?key=${enc(key)}`);
  const lead = e.cast.slice(0, 3);
  const kinText = k => k.role === "spouse" ? t("myth.married") : k.role === "partner" ? t("myth.affair")
    : t("myth.parent_of", { r: t(`kin.${k.role}`) });
  app.innerHTML = `<div class="layout two"><section class="col">
    <div class="card flush profile-top">
      <div class="banner myth-banner"><span>🏺</span></div>
      <div class="inner">
        <div class="kicker">${e.kind === "MYTH" ? t("myth.kind_myth") : t("myth.kind_chapter")} · ${t("myth.collab")}</div>
        <h1>${esc(e.name)}</h1>
        <div class="headline">${t("myth.told_in", { w: workLink(e.work_key, e.title), a: esc(e.author) })}${e.chapter ? t("myth.book", { n: esc(e.chapter) }) : ""}</div>
        <div class="facts">${esc(e.genre_label)} · ${esc(e.years)} · ${esc(e.period_label)} · ${t("myth.involved", { n: e.cast.length })}</div>
        ${lead.length ? `<div class="mutual"><span class="stack">${lead.map(c => avatar(c, "xs")).join("")}</span>
          ${t("myth.leads")} ${lead.map(nameLink).join(", ")}</div>` : ""}
      </div>
    </div>
    <div class="card"><h3>${t("myth.cast", { n: e.cast.length })}</h3>
      <div class="grid-people">${e.cast.map(c => `<div class="pcard">${avatar(c, "lg")}<a class="nm" href="${link(c.name)}"><b>${esc(nm(c))}</b></a>
        <div class="hl">${esc(c.headline)}</div><div class="small muted">${t("myth.interactions", { n: c.mentions })}</div></div>`).join("")}</div>
    </div>
  </section>
  <aside class="col">
    ${e.duos.length ? `<div class="card"><h3>${t("myth.duos")}</h3><div class="muted small" style="margin:-6px 0 6px">${t("myth.duos_sub")}</div>
      ${e.duos.map(d => `<div class="trend">🤝 <span>${nameLink(d.a)} & ${nameLink(d.b)}<br><span class="muted small">${t("myth.duo_scenes", { n: d.mentions })}</span></span></div>`).join("")}</div>` : ""}
    ${e.kin.length ? `<div class="card"><h3>${t("myth.kin")}</h3>
      ${e.kin.slice(0, 15).map(k => `<div class="trend">${k.role === "spouse" ? "💍" : k.role === "partner" ? "💘" : "👪"} <span>${nameLink(k.a)}
        ${esc(kinText(k).toLowerCase())} ${nameLink(k.b)}</span></div>`).join("")}
      ${e.kin.length > 15 ? `<div class="muted small">${t("myth.more_kin", { n: e.kin.length - 15 })}</div>` : ""}</div>` : ""}
    ${e.other_episodes.length ? `<div class="card"><h3>${t("myth.same_work")}</h3><div class="chips">${e.other_episodes.map(o => mythLink(o.key, o.name)).join("")}</div></div>` : ""}
  </aside></div>`;
}

// ---------------------------------------------------------------- œuvre (page « entreprise »)

async function pageWork(key) {
  const w = await api(`/work?key=${enc(key)}`);
  const max = Math.max(...w.clans.map(c => c[1]), 1);
  app.innerHTML = `<div class="layout two"><section class="col">
    <div class="card flush profile-top">
      <div class="banner work-banner"><span>${genreIcon(w.genre)}</span></div>
      <div class="inner">
        <div class="kicker">${t("work.kicker", { g: esc(w.genre_label) })}</div>
        <h1>${esc(w.title)}</h1>
        <div class="headline">${t("work.by")} <b>${esc(w.author)}</b></div>
        <div class="facts">📅 ${esc(w.years)} · ${esc(w.period_label)} · 🗣️ ${esc(w.language)} · ${t("work.staff", { n: fmt(w.headcount) })}</div>
        <div class="btns"><button class="btn primary" data-toast="${esc(t("toast.follow", { t: w.title }))}">${t("btn.follow")}</button></div>
      </div>
    </div>
    ${w.summary ? `<div class="card work-summary"><h3>${t("work.presentation")}
        ${w.summary.lang !== LANG ? `<span class="pill small">${esc(w.summary.lang)}</span>` : ""}</h3>
      ${w.summary.text.split("\n").filter(Boolean).map(par => `<p>${esc(par)}</p>`).join("")}
      ${w.summary.fallback ? `<div class="muted small">${t("work.fallback")}</div>` : ""}
      <div class="muted small source">${t("work.source")} <a href="${esc(w.summary.url)}" target="_blank" rel="noopener">${esc(w.summary.title)}</a>
        · <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.${LANG}" target="_blank" rel="noopener">CC BY-SA 4.0</a></div>
    </div>` : ""}
    <div class="card"><h3>${t("work.top")}</h3>
      <div class="grid-people">${w.cast.map(c => `<div class="pcard">${avatar(c, "lg")}<a class="nm" href="${link(c.name)}"><b>${esc(nm(c))}</b></a>
        <div class="hl">${esc(c.headline)}</div><div class="small muted">${t("profile.scenes", { n: c.mentions })}</div></div>`).join("")}</div>
    </div>
  </section>
  <aside class="col">
    <div class="card"><h3>${t("work.clans")}</h3>
      ${w.clans.map(([k, n]) => `<div class="bar-row compact"><span class="bar-label">${esc(clanLabel(k))}</span>
        <span class="bar"><span style="width:${(100 * n / max).toFixed(1)}%;background:${(CLAN_STYLE[k] || CLAN_STYLE["Divinité"])[1]}"></span></span><b>${n}</b></div>`).join("")}
    </div>
    ${w.episodes.length ? `<div class="card"><h3>${t("work.episodes", { n: w.episodes.length })}</h3>
      <div class="chips">${w.episodes.map(e => mythLink(e.key, e.name)).join("")}</div></div>` : ""}
  </aside></div>`;
}

async function pageLibrary() {
  const works = await api("/works");
  const groups = {};
  works.forEach(w => (groups[w.period_label] = groups[w.period_label] || []).push(w));
  app.innerHTML = `<div class="card"><h2 class="section-title">${t("library.title")}</h2>
    <div class="muted" style="margin:-8px 0 14px">${t("library.sub", { n: works.length })}</div>
    ${Object.entries(groups).map(([period, ws]) => `<h3 class="period">${esc(period)} <span class="muted small">${esc(ws[0].years)}</span></h3>
      <div class="works">${ws.map(w => `<a class="work-card" href="#/work/${enc(w.key)}">
        <span class="wicon">${genreIcon(w.genre)}</span>
        <b>${esc(w.title)}</b><span>${esc(w.author)}</span>
        ${w.excerpt ? `<span class="excerpt">${esc(w.excerpt)}</span>` : ""}
        <span class="muted small">${t("library.stats", { g: esc(w.genre_label), p: fmt(w.people), s: fmt(w.mentions) })}</span></a>`).join("")}</div>`).join("")}
  </div>`;
}

// ---------------------------------------------------------------- Mythspace (graphe)

async function pageMythspace(center) {
  center = center || ME;
  app.innerHTML = `<div class="col">
    <div class="card">
      <h2 class="section-title">${t("ms.title", { n: esc(nm(center)) })}</h2>
      <div class="tool-row">
        <div class="search"><input id="ms-center" type="search" placeholder="${esc(t("ms.center"))}"><div id="ms-center-r" class="dropdown hidden"></div></div>
        <label class="small muted">${t("ms.size")}
          <input id="ms-size" type="range" min="10" max="80" value="30"></label>
      </div>
      <div id="network" style="margin-top:12px"></div>
      <div class="legend">${Object.entries(CLAN_STYLE).map(([k, [, c2]]) => `<span><i style="background:${c2}"></i>${esc(clanLabel(k))}</span>`).join("")}</div>
      <div class="small muted" style="margin-top:6px">${t("ms.help")}</div>
    </div>
    <div class="card">
      <h3>${t("ms.degrees")}</h3>
      <div class="tool-row">
        <div class="search"><input id="pa" type="search" value="${esc(nm(ME))}" data-name="${esc(ME)}"><div id="pa-r" class="dropdown hidden"></div></div>
        <span>→</span>
        <div class="search"><input id="pb" type="search" value="${esc(nm("Sisyphus"))}" data-name="Sisyphus"><div id="pb-r" class="dropdown hidden"></div></div>
        <button class="btn primary" id="go">${t("btn.findpath")}</button>
      </div>
      <div id="path-out" style="margin-top:14px"></div>
    </div>
  </div>`;

  const draw = async () => {
    const size = document.getElementById("ms-size").value;
    const g = await api(`/network/${enc(center)}?size=${size}`);
    const maxM = Math.max(...g.edges.map(e => e.mentions), 1);
    const nodes = g.nodes.map(n => {
      const [c1, c2] = CLAN_STYLE[n.clan] || CLAN_STYLE["Divinité"];
      return visNode(n, { id: n.name, label: nm(n), title: `${nm(n)} — ${n.headline}`,
        value: n.name === center ? 40 : 8 + (n.mentions || 0),
        color: { background: c1, border: c2, highlight: { background: c1, border: "#000" } },
        font: { size: n.name === center ? 22 : 15, face: "Source Sans 3", color: "#2a2620" } });
    });
    const edges = g.edges.map(e => ({ from: e.source, to: e.target, value: e.mentions,
      title: t("ms.edge", { n: e.mentions }),
      color: { color: e.source === center || e.target === center ? "#b88a2e" : "#c9bfae", opacity: .3 + .7 * e.mentions / maxM } }));
    if (!window.vis) { document.getElementById("network").innerHTML = `<div class="loading">${t("ms.offline")}</div>`; return; }
    if (network) network.destroy();
    network = new vis.Network(document.getElementById("network"),
      { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) },
      { nodes: { shape: "dot", scaling: { min: 8, max: 40 } },
        edges: { scaling: { min: 1, max: 9 }, smooth: false },
        physics: { barnesHut: { gravitationalConstant: -9000, springLength: 160 }, stabilization: { iterations: 200 } },
        interaction: { hover: true, tooltipDelay: 120 } });
    network.on("doubleClick", ev => { if (ev.nodes.length) location.hash = link(ev.nodes[0]); });
  };
  document.getElementById("ms-size").onchange = draw;
  bindSearch(document.getElementById("ms-center"), document.getElementById("ms-center-r"),
    n => { location.hash = `#/mythspace/${enc(n)}`; });
  bindSearch(document.getElementById("pa"), document.getElementById("pa-r"), () => {});
  bindSearch(document.getElementById("pb"), document.getElementById("pb-r"), () => {});

  const findPath = async () => {
    const ia = document.getElementById("pa"), ib = document.getElementById("pb");
    const a = ia.dataset.name || ia.value.trim(), b = ib.dataset.name || ib.value.trim();
    const out = document.getElementById("path-out");
    try {
      const r = await api(`/path?a=${enc(a)}&b=${enc(b)}`);
      if (!r.found) { out.innerHTML = `<div class="muted">${t("ms.nopath")}</div>`; return; }
      const first = r.people[0], last = r.people[r.people.length - 1];
      out.innerHTML = `<div class="path">${r.people.map((p, i) => `${i ? `<span class="arrow">→<br>${r.mentions[i - 1]} ${t("ms.sc")}</span>` : ""}
          <a class="step" href="${link(p.name)}">${avatar(p, "sm")}${esc(nm(p))}</a>`).join("")}</div>
        <div style="margin-top:8px">${t("ms.result", { d: r.degrees, a: esc(nm(first)), b: esc(nm(last)) })}</div>`;
    } catch { out.innerHTML = `<div class="muted">${t("ms.notfound")}</div>`; }
  };
  document.getElementById("go").onclick = findPath;
  await Promise.all([draw(), findPath()]);
}

// ---------------------------------------------------------------- autres pages

async function pageNetwork() {
  const sugg = await api(`/suggestions/${enc(ME)}?limit=24`);
  app.innerHTML = `<div class="card"><h2 class="section-title">${t("network.title")}</h2>
    <div class="muted" style="margin:-8px 0 14px">${t("network.sub")}</div>
    <div class="grid-people">${sugg.map(p => `<div class="pcard">${avatar(p, "lg")}<a class="nm" href="${link(p.name)}"><b>${esc(nm(p))}</b></a>
      <div class="hl">${esc(p.headline)}</div><div class="small muted" style="margin-bottom:8px">${t("home.mutual", { n: fmt(p.mutual) })}</div>${connectButton(p)}</div>`).join("")}</div></div>`;
}

async function pageJobs() {
  const jobs = await api(`/jobs/${enc(ME)}`);
  app.innerHTML = `<div class="layout two"><section class="card">
    <h2 class="section-title">${t("jobs.title")}</h2>
    ${jobs.map(j => `<div class="job">${avatar(j.boss, "lg")}<div style="flex:1">
      <div class="t">${esc(j.title)}</div>
      <div>${esc(j.company)} · ${esc(j.location)}</div>
      <div class="muted small">${t("jobs.recruiter")} ${nameLink(j.boss)} ${j.degrees ? t("degree.job", { d: j.degrees }) : ""} · ${t("jobs.applicants", { n: fmt(j.applicants) })}</div>
      <div style="margin-top:6px">${esc(j.desc)}</div>
      ${j.candidates.length ? `<div class="cands"><span class="stack">${j.candidates.map(c => avatar(c, "xs")).join("")}</span>
        ${t("jobs.candidates")} ${j.candidates.map(nameLink).join(", ")}</div>` : ""}
      <div style="margin-top:10px"><button class="btn primary" data-toast="${esc(t("toast.apply"))}">${t("btn.apply")}</button></div>
    </div></div>`).join("")}
  </section>
  <aside class="col"><div class="card"><h3>${t("jobs.tip")}</h3>
    <div>${t("jobs.tip_body")}</div>
    <div class="muted small" style="margin-top:8px">${t("jobs.tip_note")}</div></div></aside></div>`;
}

async function pageMessaging() {
  const convs = await api(`/messages/${enc(ME)}`);
  app.innerHTML = `<div class="card"><h2 class="section-title">${t("msg.title")}</h2>
    ${convs.map(c => `<div class="list-item">${avatar(c.who)}<div><a class="nm" href="${link(c.who.name)}"><b>${esc(nm(c.who))}</b></a>
      <div class="muted">${esc(c.last)}</div></div><span class="when">${esc(c.when)}</span></div>`).join("")}
    <div class="muted small" style="margin-top:12px">${t("msg.note")}</div></div>`;
}

async function pageNotifications() {
  const notes = await api(`/notifications/${enc(ME)}`);
  app.innerHTML = `<div class="card"><h2 class="section-title">${t("notif.title")}</h2>
    ${notes.map(n => `<div class="list-item">${n.who ? avatar(n.who) : '<span class="avatar">📈</span>'}
      <div>${n.who ? `<b>${nameLink(n.who)}</b> ` : ""}${esc(n.text)}</div><span class="when">${esc(n.when)}</span></div>`).join("")}</div>`;
}

function pageSwitch() {
  const famous = ["Athena", "Zeus", "Hera", "Hermes", "Sisyphus", "Narcissus", "Prometheus", "Odysseus",
    "Medusa", "Hades", "Persephone", "Heracles", "Cassandra", "Icarus", "Pandora", "Charon"];
  app.innerHTML = `<div class="card"><h2 class="section-title">${t("switch.title")}</h2>
    <div class="muted" style="margin:-8px 0 14px">${t("switch.sub", { n: esc(nm(ME)) })}</div>
    <div class="tool-row" style="margin-bottom:16px"><div class="search"><input id="sw" type="search" placeholder="${esc(t("switch.search"))}"><div id="sw-r" class="dropdown hidden"></div></div></div>
    <div class="grid-people">${famous.map(n => `<div class="pcard" data-become="${esc(n)}" style="cursor:pointer">
      ${avatar({ name: n, clan: "Divinité" }, "lg")}<b>${esc(nm(n))}</b></div>`).join("")}</div></div>`;
  bindSearch(document.getElementById("sw"), document.getElementById("sw-r"), n => {
    setMe(n); toast(t("toast.become", { n: nm(n) })); location.hash = "#/";
  });
}

// ---------------------------------------------------------------- carte (Leaflet)

function newMap(el) {
  if (leafletMap) { leafletMap.remove(); leafletMap = null; }
  if (!window.L) { el.innerHTML = `<div class="loading">${t("map.offline")}</div>`; return null; }
  leafletMap = L.map(el, { scrollWheelZoom: false }).setView([38.5, 23.5], 6);   // centrée sur la Grèce
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · Wikidata',
  }).addTo(leafletMap);
  return leafletMap;
}

// Un marqueur pour un groupe de lieux voisins (voir groupByProximity), dont la bulle les liste tous.
// Couleur = type de lien le plus fréquent, taille = nombre de personnages.
function placeMarker(group) {
  const all = group.flatMap(g => g.people);
  const counts = {};
  all.forEach(x => { counts[x.kind] = (counts[x.kind] || 0) + 1; });
  const main = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
  const approx = group.every(g => g.place.approx);
  const section = ({ place, people }) => `<div class="map-place"><b>${esc(place.name)}</b>${place.approx ? ` <span class="muted small">≈</span>` : ""}
    ${PLACE_ORDER.filter(k => people.some(x => x.kind === k)).map(k =>
      `<div class="map-kind" style="--c:${PLACE_COLORS[k]}">${t(`place.${k}`)}</div>
      ${people.filter(x => x.kind === k).map(x => `<a class="map-person" href="${link(x.name)}">${emojiFor(x)} ${esc(nm(x))}${placeSource(x.source)}</a>`).join("")}`).join("")}</div>`;
  const popup = `<div class="map-popup">${group.map(section).join("")}
    ${group.some(g => g.place.approx) ? `<div class="muted small">≈ ${t("map.approx")}</div>` : ""}</div>`;
  const { lat, lon } = group[0].place;
  return L.circleMarker([lat, lon], {
    radius: Math.min(5 + 4 * Math.sqrt(all.length), 22), color: "#fff", weight: 1.5,
    fillColor: PLACE_COLORS[main], fillOpacity: approx ? .55 : .9, dashArray: approx ? "3" : null,
  }).bindPopup(popup, { maxWidth: 300, maxHeight: 320 });
}

function coreBounds(points) {
  const q = (arr, f) => arr[Math.min(arr.length - 1, Math.max(0, Math.round(f * (arr.length - 1))))];
  const lats = points.map(p => p[0]).sort((a, b) => a - b), lons = points.map(p => p[1]).sort((a, b) => a - b);
  return [[q(lats, .05), q(lons, .05)], [q(lats, .95), q(lons, .95)]];
}

// Lieux qui se chevaucheraient à l'écran au zoom courant : même position (une ville et ses tombeaux
// « approchés ») ou quelques centaines de mètres (l'Achilléion et le tumulus d'Achille) -> un seul marqueur.
const OVERLAP_PX = 10;

function groupByProximity(items, map) {
  const groups = [];
  [...items].sort((a, b) => b.people.length - a.people.length).forEach(it => {
    const pt = map.latLngToLayerPoint([it.place.lat, it.place.lon]);
    const near = groups.find(g => g.pt.distanceTo(pt) < OVERLAP_PX);
    if (near) near.items.push(it);
    else groups.push({ pt, items: [it] });
  });
  return groups.map(g => g.items);
}

// Dessine les lieux et refait les regroupements à chaque zoom (en zoomant, les voisins se séparent).
function plotPlaces(map, layer, items) {
  const render = () => {
    layer.clearLayers();
    groupByProximity(items, map).forEach(g => placeMarker(g).addTo(layer));
  };
  if (map.replot) map.off("zoomend", map.replot);
  map.replot = render;
  map.on("zoomend", render);
  render();
}

function mapLegend() {
  return `<div class="legend map-legend">${PLACE_ORDER.map(k =>
    `<label><input type="checkbox" data-kind="${k}" checked><i style="background:${PLACE_COLORS[k]}"></i>${t(`place.${k}`)}</label>`).join("")}
    <span><i class="approx-dot"></i>${t("map.approx")}</span></div>`;
}

// recherche sans accents ni majuscules (« heracles » trouve « Héraclès »)
const fold = s => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

async function pageMap(focus) {
  const places = await api("/map");
  const located = places.filter(p => p.lat != null);
  const off = places.filter(p => p.lat == null);
  // personnages présents sur la carte, avec leur nombre de lieux, pour le filtre
  const cast = new Map();
  places.forEach(pl => pl.people.forEach(x => {
    const c = cast.get(x.name) || { ...x, places: new Set() };
    c.places.add(pl.qid);
    cast.set(x.name, c);
  }));
  const castList = [...cast.values()].sort((a, b) => nm(a).localeCompare(nm(b), LANG));
  app.innerHTML = `<div class="card">
    <h2 class="section-title" id="map-title"></h2>
    <div class="muted" id="map-sub" style="margin:-8px 0 12px"></div>
    <div class="map-filters">
      <div class="search map-search">
        <input id="map-who" type="search" autocomplete="off" placeholder="${esc(t("map.filter"))}">
        <div id="map-who-r" class="dropdown hidden"></div>
      </div>
      ${mapLegend()}
    </div>
    <div id="world-map" class="world-map"></div>
    <div id="map-off" class="small muted" style="margin-top:10px"></div>
    <div id="map-route" class="map-route"></div>
  </div>`;
  const input = document.getElementById("map-who"), results = document.getElementById("map-who-r");
  const header = () => {
    document.getElementById("map-title").innerHTML = focus ? t("map.focus", { n: esc(nm(focus)) }) : t("map.title");
    document.getElementById("map-sub").innerHTML = focus ? `<a href="#/map">${t("map.all")}</a>`
      : t("map.sub", { n: located.length, p: cast.size });
    document.getElementById("map-off").innerHTML = off.length && !focus ? `<b>${t("map.offmap")}</b> — ${t("map.offmap_sub")}
      ${off.map(p => `${esc(p.name)} (${p.people.map(x => nameLink(x)).join(", ")})`).join(" · ")}` : "";
  };
  header();
  if (focus) input.value = nm(focus);

  const map = newMap(document.getElementById("world-map"));
  if (!map) return;
  const layer = L.layerGroup().addTo(map);
  const routeLayer = L.layerGroup().addTo(map);
  const routes = {};   // itinéraires déjà chargés, par personnage
  // Itinéraire du personnage filtré (DATAS/itineraires.csv) : segments en pointillé, flèches, étapes numérotées
  const showRoute = () => {
    routeLayer.clearLayers();
    const box = document.getElementById("map-route");
    const who = focus, steps = who && routes[who];
    if (who && steps === undefined) {
      api(`/itinerary/${enc(who)}`).then(s => { routes[who] = s; if (focus === who) showRoute(); });
      return;
    }
    if (!steps || !steps.length) { box.innerHTML = ""; return; }
    const pts = steps.filter(s => s.lat != null);
    for (let i = 1; i < pts.length; i++) {
      const a = [pts[i - 1].lat, pts[i - 1].lon], b = [pts[i].lat, pts[i].lon];
      if (a[0] === b[0] && a[1] === b[1]) continue;
      L.polyline([a, b], { color: PLACE_COLORS.visit, weight: 2.5, opacity: .85, dashArray: "6 6", interactive: false })
        .addTo(routeLayer);
      const pa = map.latLngToLayerPoint(a), pb = map.latLngToLayerPoint(b);
      const deg = Math.atan2(pb.y - pa.y, pb.x - pa.x) * 180 / Math.PI;   // projection conforme : angle valable à tout zoom
      L.marker([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], { interactive: false, keyboard: false,
        icon: L.divIcon({ className: "route-arrow", iconSize: [16, 16], html: `<span style="transform:rotate(${deg}deg)">➤</span>` }) })
        .addTo(routeLayer);
    }
    const byPlace = {};
    pts.forEach(s => { (byPlace[s.qid] = byPlace[s.qid] || { ...s, orders: [] }).orders.push(s.order); });
    Object.values(byPlace).forEach(s => L.marker([s.lat, s.lon], { interactive: false, keyboard: false,
      icon: L.divIcon({ className: "route-num", iconSize: null, iconAnchor: [-6, 22], html: s.orders.join(" · ") }) })
      .addTo(routeLayer));
    box.innerHTML = `<h3>${t("route.title", { n: esc(nm(who)) })}</h3><ol>${steps.map(s => `<li value="${s.order}">
      <b>${esc(s.label)}</b> <span class="muted small">— ${esc(s.place || "")}${s.lat == null ? ` (${t("route.offmap")})` : ""}
      · ${esc(s.ref)}</span></li>`).join("")}</ol>`;
  };
  const choose = name => {
    focus = name;
    input.value = name ? nm(name) : "";
    results.classList.add("hidden");
    history.replaceState(null, "", name ? `#/map/${enc(name)}` : "#/map");   // sans relancer route()
    header();
    draw();
  };
  const suggest = () => {
    const v = fold(input.value.trim());
    const rows = castList.filter(x => !v || fold(nm(x)).includes(v) || fold(x.name).includes(v)).slice(0, 40);
    results.innerHTML = rows.length
      ? rows.map(x => `<div class="person" data-pick="${esc(x.name)}">${avatar(x, "sm")}<div class="who">
          <span class="nm">${esc(nm(x))}</span><span class="hl">${t("map.places", { n: x.places.size })}</span></div></div>`).join("")
      : `<div class="person muted">${t("search.none")}</div>`;
    results.classList.remove("hidden");
  };
  input.addEventListener("focus", suggest);
  input.addEventListener("input", () => {
    if (!input.value.trim() && focus) choose(null);   // champ vidé (ou croix du champ) : tous les personnages
    else suggest();
  });
  input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      const first = results.querySelector("[data-pick]");
      if (first) choose(first.dataset.pick);
    } else if (e.key === "Escape") results.classList.add("hidden");
  });
  results.addEventListener("click", e => {
    const el = e.target.closest("[data-pick]");
    if (el) choose(el.dataset.pick);
  });
  const draw = () => {
    const kinds = new Set([...document.querySelectorAll("[data-kind]:checked")].map(c => c.dataset.kind));
    const items = located.map(pl => ({ place: pl, people: pl.people.filter(x => kinds.has(x.kind) && (!focus || x.name === focus)) }))
      .filter(it => it.people.length);
    const shown = items.map(it => [it.place.lat, it.place.lon]);
    // vue cadrée sur l'essentiel des lieux (Grèce, ou bassin méditerranéen si besoin) : on ignore
    // les 5 % les plus excentrés (île de Cerné, Assur…), qui restent visibles en dézoomant
    if (shown.length) map.fitBounds(focus ? shown : coreBounds(shown), { padding: [30, 30], maxZoom: focus ? 8 : 7 });
    plotPlaces(map, layer, items);
    showRoute();
  };
  document.querySelectorAll("[data-kind]").forEach(c => c.addEventListener("change", draw));
  draw();
}

function drawMiniMap(p) {
  const el = document.getElementById("mini-map");
  if (!el) return;
  const map = newMap(el);
  if (!map) return;
  const pts = p.places.filter(x => x.lat != null);
  const byPlace = {};
  pts.forEach(x => { (byPlace[x.qid] = byPlace[x.qid] || { place: x, people: [] }).people.push({ ...p, kind: x.kind }); });
  map.fitBounds(pts.map(x => [x.lat, x.lon]), { padding: [25, 25], maxZoom: 8 });
  plotPlaces(map, L.layerGroup().addTo(map), Object.values(byPlace));
}

// ---------------------------------------------------------------- page d'erreur : le labyrinthe

// Labyrinthe circulaire : chaque mur est un cercle ouvert d'un côté (alternativement en bas et en haut),
// le fil d'Ariane entre par le bas et passe d'une ouverture à l'autre jusqu'au Minotaure.
function labyrinthSVG() {
  const c = 120, rings = [105, 80, 55, 30];
  const pt = (r, a) => `${(c + r * Math.cos(a)).toFixed(1)} ${(c + r * Math.sin(a)).toFixed(1)}`;
  const walls = rings.map((r, i) => {
    const gapAt = i % 2 === 0 ? Math.PI / 2 : -Math.PI / 2, g = 13 / r;
    return `<path d="M ${pt(r, gapAt + g)} A ${r} ${r} 0 1 1 ${pt(r, gapAt - g)}" />`;
  }).join("");
  // couloirs entre deux murs : rayon moyen, parcourus d'un demi-tour à chaque fois
  const lanes = [92.5, 67.5, 42.5];
  let d = `M ${c} 236 L ${c} ${c + lanes[0]}`;
  lanes.forEach((r, i) => {
    const down = i % 2 === 0;               // on part du bas, on arrive en haut, et ainsi de suite
    d += ` A ${r} ${r} 0 0 1 ${c} ${down ? c - r : c + r}`;
    const next = lanes[i + 1];
    d += next ? ` L ${c} ${down ? c - next : c + next}` : ` L ${c} ${c - 8}`;
  });
  return `<svg class="labyrinth" viewBox="0 0 240 250" role="img" aria-label="${esc(t("error.img"))}">
    <g class="walls">${walls}</g>
    <path class="thread" d="${d}" />
    <g class="ball" transform="translate(${c} 238)"><circle r="9" />
      <path d="M -7 -4 Q 0 2 7 -4 M -8 2 Q 0 8 8 2 M -3 -8 Q 2 0 -2 8" /></g>
    <text x="${c}" y="${c + 9}" text-anchor="middle" font-size="24">🐂</text>
  </svg>`;
}

// ---------------------------------------------------------------- crédits

function pageAbout() {
  app.innerHTML = `<div class="card about">
    <h2 class="section-title">${t("about.title")}</h2>
    <p class="muted">${t("about.intro")}</p>
    <div class="about-kaggle"><span class="about-icon">📊</span><div>
      <h3>${t("about.kaggle_title")}</h3><p>${t("about.kaggle")}</p></div></div>
    <h3>${t("about.other_title")}</h3>
    <ul>${["wikidata", "wikipedia", "wikiquote", "commons", "theoi", "osm"].map(k => `<li>${t(`about.${k}`)}</li>`).join("")}</ul>
    <h3>${t("about.tools_title")}</h3>
    <p>${t("about.tools")}</p>
  </div>`;
}

// ---------------------------------------------------------------- routeur

async function route() {
  const [, page = "", ...rest] = location.hash.split("/");
  const param = rest.length ? decodeURIComponent(rest.join("/")) : null;
  document.querySelectorAll(".mainnav a").forEach(a =>
    a.classList.toggle("active", a.dataset.nav === (page || "home")));
  app.innerHTML = `<div class="loading">${t("loading")}</div>`;
  window.scrollTo(0, 0);
  try {
    if (page === "in" && param) await pageProfile(param);
    else if (page === "mythspace") await pageMythspace(param);
    else if (page === "network") await pageNetwork();
    else if (page === "family") await pageFamily(param);
    else if (page === "myth" && param) await pageMyth(param);
    else if (page === "work" && param) await pageWork(param);
    else if (page === "library") await pageLibrary();
    else if (page === "map") await pageMap(param);
    else if (page === "about") pageAbout();
    else if (page === "jobs") await pageJobs();
    else if (page === "messaging") await pageMessaging();
    else if (page === "notifications") await pageNotifications();
    else if (page === "switch") pageSwitch();
    else await pageHome();
  } catch (err) {
    app.innerHTML = `<div class="card error-page">${labyrinthSVG()}<div>
      <h2 class="section-title">${t("error.title")}</h2>
      <div class="muted">${/^\d+$/.test(err.message) ? "" : `${esc(err.message)}. `}${t("error.body")}</div></div></div>`;
  }
}

window.addEventListener("hashchange", route);
applyStaticTexts();
Promise.all([
  fetch("/api/labels").then(r => r.json()).then(m => { LABELS_FR = m; }),
  fetch("/api/portraits").then(r => r.json()).then(m => { PORTRAITS = m; }),
]).catch(() => {}).finally(() => {
  refreshHeader().catch(() => { setMe(DEFAULT_ME); });
  route();
});
