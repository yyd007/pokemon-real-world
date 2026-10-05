import creatures from "../data/creatures.json";
import "./style.css";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("missing #app");
}

const hero = document.createElement("section");
hero.className = "hero";

const copy = document.createElement("div");
copy.className = "hero-copy";

const kicker = document.createElement("p");
kicker.className = "kicker";
kicker.textContent = "短纪录片";

const title = document.createElement("h1");
title.textContent = "如果初代宝可梦生活在真实世界";

const lede = document.createElement("p");
lede.className = "lede";
lede.textContent =
  "十种最常被提起的初代宝可梦，各自放进一种可能的栖息地。画面是写实设想，每只只有一句介绍。";

copy.append(kicker, title, lede);

const player = document.createElement("div");
player.className = "player";

const video = document.createElement("video");
video.controls = true;
video.playsInline = true;
video.preload = "metadata";
video.poster = "/poster.jpg";
video.setAttribute("aria-label", "如果初代宝可梦生活在真实世界");

const source = document.createElement("source");
source.src = "/pokemon-real-world.mp4";
source.type = "video/mp4";
video.append(source);
player.append(video);
hero.append(copy, player);

const rosterWrap = document.createElement("section");
rosterWrap.className = "roster-wrap";

const heading = document.createElement("h2");
heading.textContent = "这十种";

const note = document.createElement("p");
note.className = "roster-note";
note.textContent = "按片中出场顺序。属性用的是初代图鉴，胖丁在这里仍是一般属性。";

const list = document.createElement("ol");
list.className = "roster";

creatures.forEach((creature, index) => {
  const item = document.createElement("li");
  item.className = "card";

  const img = document.createElement("img");
  img.src = `/creatures/${creature.id}.jpg`;
  img.alt = `${creature.name}的写实设想`;
  img.width = 132;
  img.height = 84;

  const body = document.createElement("div");
  const name = document.createElement("h3");
  name.textContent = `${String(index + 1).padStart(2, "0")}  ${creature.name}`;

  const meta = document.createElement("p");
  meta.className = "meta";
  meta.textContent = creature.type;
  const latin = document.createElement("span");
  latin.className = "latin";
  latin.textContent = creature.latin;
  meta.append(latin);

  const line = document.createElement("p");
  line.textContent = creature.line;

  body.append(name, meta, line);
  item.append(img, body);
  list.append(item);
});

const foot = document.createElement("p");
foot.className = "foot";
foot.textContent = "它们只是想象中的邻居。影像与旁白均为这次制作的原创内容。";

rosterWrap.append(heading, note, list, foot);
app.append(hero, rosterWrap);
