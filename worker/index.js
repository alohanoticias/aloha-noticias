/* ALOHA NOTÍCIAS: contador de visitas próprio (sem Google Analytics e sem cookies).
 *
 * Como funciona
 * - As páginas públicas mandam um aviso leve (POST /api/v) a cada página vista (assets/js/contador.js).
 * - Este Worker guarda cada visita num Durable Object com banco SQLite ("Metricas"), criado sozinho no deploy.
 * - O painel lê os números em GET /admin/api/metricas. Esse endereço fica atrás do login do Cloudflare Access
 *   (como todo o /admin) e só responde pelo domínio alohanoticias.com.
 *
 * Privacidade: não há cookies. O IP nunca é gravado: serve só para montar, junto com o navegador, um código
 * embaralhado com um "sal" que muda todo dia e é apagado no dia seguinte. Assim dá para contar visitantes
 * únicos do dia sem conseguir reconhecer ninguém, nem de um dia para o outro.
 *
 * Todo o resto (páginas, imagens, 404) continua sendo servido pelos arquivos estáticos de publico/.
 */
import { DurableObject } from "cloudflare:workers";

const DOMINIOS = new Set(["alohanoticias.com", "www.alohanoticias.com"]);
const IDIOMAS = new Set(["en", "es", "it"]);
const ROBO = /bot|crawl|spider|slurp|bingpreview|facebookexternalhit|whatsapp|telegrambot|preview|headless|lighthouse|pagespeed|gtmetrix|monitor|uptime|curl|wget|python|axios|node-fetch|go-http/i;
const FUSO_MS = -3 * 3600 * 1000; // horário de Brasília (sem horário de verão desde 2019)

const json = (dados, status = 200) =>
  new Response(JSON.stringify(dados), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

function corta(v, n) { return (v == null ? "" : String(v)).slice(0, n); }

function aparelho(ua) {
  if (/iPad|Tablet|PlayBook|Silk|Android(?!.*Mobile)/i.test(ua)) return "tablet";
  if (/Mobi|iPhone|iPod|Android|Windows Phone/i.test(ua)) return "celular";
  return "computador";
}

// Apps de celular mandam "android-app://<pacote>" como origem
const APPS = { "org.telegram.messenger": "telegram", "org.telegram.plus": "telegram", "org.thunderdog.challegram": "telegram",
  "com.whatsapp": "whatsapp", "com.whatsapp.w4b": "whatsapp", "com.instagram.android": "instagram", "com.facebook.katana": "facebook",
  "com.facebook.orca": "facebook", "com.facebook.lite": "facebook", "com.twitter.android": "x", "com.zhiliaoapp.musically": "tiktok",
  "com.ss.android.ugc.trill": "tiktok", "com.google.android.youtube": "youtube", "com.discord": "discord", "com.reddit.frontpage": "reddit",
  "com.google.android.googlequicksearchbox": "google", "com.google.android.gm": "gmail" };

function origemDe(ref) {
  if (!ref) return "direto";
  try {
    const u = new URL(ref);
    if (u.protocol === "android-app:") return APPS[u.hostname] || (/telegram/.test(u.hostname) ? "telegram" : u.hostname.slice(0, 80));
    const h = u.hostname.replace(/^www\./, "").replace(/^m\./, "").replace(/^l\./, "").replace(/^lm\./, "");
    if (h === "alohanoticias.com") return "interno";
    if (/(^|\.)google\./.test(h)) return "google";
    if (/(^|\.)bing\.com$/.test(h)) return "bing";
    if (/(^|\.)(facebook|fb)\.com$/.test(h)) return "facebook";
    if (/(^|\.)instagram\.com$/.test(h)) return "instagram";
    if (/(^|\.)(t\.co|twitter\.com|x\.com)$/.test(h)) return "x";
    if (/(^|\.)(t\.me|telegram\.org)$/.test(h)) return "telegram";
    if (/(^|\.)(youtube\.com|youtu\.be)$/.test(h)) return "youtube";
    if (/(^|\.)tiktok\.com$/.test(h)) return "tiktok";
    if (/(^|\.)whatsapp\.com$/.test(h)) return "whatsapp";
    if (/(^|\.)reddit\.com$/.test(h)) return "reddit";
    return h.slice(0, 80);
  } catch (e) { return "direto"; }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/api/v") {
      if (request.method !== "POST") return new Response(null, { status: 405 });
      const ua = request.headers.get("user-agent") || "";
      if (!ua || ROBO.test(ua) || request.headers.get("sec-purpose")) return new Response(null, { status: 204 });
      let d = {};
      try { d = JSON.parse((await request.text()).slice(0, 2000) || "{}"); } catch (e) { return new Response(null, { status: 204 }); }
      let pagina;
      try { pagina = new URL(String(d.u || ""), "https://alohanoticias.com"); } catch (e) { return new Response(null, { status: 204 }); }
      if (!DOMINIOS.has(pagina.hostname) || pagina.pathname.startsWith("/admin")) return new Response(null, { status: 204 });
      const caminho = corta(decodeURIComponent(pagina.pathname).replace(/\/index\.html$/, "/"), 200);
      const prim = caminho.split("/")[1] || "";
      const q = pagina.searchParams;
      const etiqueta = (q.get("utm_campaign") || "").toLowerCase() === "parceiro" ? (q.get("utm_medium") || "") : (q.get("utm_source") || "");
      let origem = origemDe(d.r);
      // Apps como o Telegram muitas vezes abrem o link sem informar a origem: aí vale a etiqueta (utm) do link
      if (origem === "direto" && etiqueta) origem = corta(etiqueta, 60).toLowerCase();
      const visita = {
        caminho,
        origem,
        fonte: corta(q.get("utm_source"), 60).toLowerCase(),
        midia: corta(q.get("utm_medium"), 60).toLowerCase(),
        campanha: corta(q.get("utm_campaign"), 80).toLowerCase(),
        conteudo: corta(q.get("utm_content"), 60).toLowerCase(),
        termo: corta(q.get("utm_term"), 60).toLowerCase(),
        pais: corta((request.cf && request.cf.country) || "", 2),
        aparelho: aparelho(ua),
        idioma: IDIOMAS.has(prim) ? prim : "pt",
        slug: /^[a-z0-9-]{1,140}$/.test(String(d.s || "")) ? String(d.s) : "",
        chave: (request.headers.get("cf-connecting-ip") || "") + "|" + ua,
      };
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      await obj.registrar(visita);
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/api/contato") {
      // Formulário de contato: guarda a mensagem no mesmo banco (tabela "contatos") e, se houver as variáveis
      // TELEGRAM_TOKEN e TELEGRAM_CHAT no Worker, avisa no Telegram. Limite: 5 mensagens por pessoa por dia.
      if (request.method !== "POST") return json({ ok: false }, 405);
      const origem = request.headers.get("origin") || "";
      if (origem && !DOMINIOS.has(new URL(origem).hostname)) return json({ ok: false }, 403);
      let d = {};
      try { d = JSON.parse((await request.text()).slice(0, 8000) || "{}"); } catch (e) { return json({ ok: false }, 400); }
      if (d.site) return json({ ok: true }); // campo-isca preenchido: robô
      const MOTIVOS = ["Sugestão de pauta", "Correção", "Direitos autorais e imagens", "Publicidade e parcerias", "Privacidade", "Outro assunto"];
      const msg = {
        nome: corta(d.nome, 100).trim(),
        email: corta(d.email, 160).trim(),
        motivo: MOTIVOS[parseInt(d.motivo, 10)] || "Outro assunto",
        mensagem: corta(d.mensagem, 5000).trim(),
        idioma: IDIOMAS.has(d.idioma) ? d.idioma : "pt",
        pagina: corta(d.pagina, 200),
        chave: (request.headers.get("cf-connecting-ip") || "") + "|" + (request.headers.get("user-agent") || ""),
      };
      if (!msg.nome || msg.mensagem.length < 10 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(msg.email)) return json({ ok: false, erro: "dados" }, 400);
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      const r = await obj.guardarContato(msg);
      if (!r.ok) return json({ ok: false, erro: "limite" }, 429);
      if (env.TELEGRAM_TOKEN && env.TELEGRAM_CHAT) {
        const texto = `✉️ Nova mensagem pelo site\n${msg.motivo} (${msg.idioma})\nDe: ${msg.nome} <${msg.email}>\n\n${msg.mensagem.slice(0, 3000)}`;
        ctx.waitUntil(fetch(`https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/sendMessage`, {
          method: "POST", headers: { "content-type": "application/json" },
          body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT, text: texto, disable_web_page_preview: true }) }).catch(() => {}));
      }
      return json({ ok: true });
    }

    if (url.pathname === "/admin/api/contatos") {
      if (!DOMINIOS.has(url.hostname) || !request.headers.get("cf-access-jwt-assertion")) return json({ erro: "acesso negado" }, 403);
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      return json({ mensagens: await obj.listarContatos() });
    }

    if (url.pathname === "/api/em-alta") {
      // lista pública, sem números: quais artigos estão em alta e a ordem das "Mais lidas" (cache de 5 minutos)
      const cache = caches.default, chave = new Request("https://alohanoticias.com/api/em-alta");
      let resp = await cache.match(chave);
      if (!resp) {
        const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
        resp = new Response(JSON.stringify(await obj.emAlta()), {
          headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=300" } });
        await cache.put(chave, resp.clone());
      }
      return resp;
    }

    if (url.pathname === "/admin/api/ao-vivo") {
      if (!DOMINIOS.has(url.hostname) || !request.headers.get("cf-access-jwt-assertion")) return json({ erro: "acesso negado" }, 403);
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      return json(await obj.aoVivo());
    }

    if (url.pathname === "/admin/api/metricas") {
      // só pelo domínio do site (onde o Cloudflare Access pede login) e com o login do Access presente
      if (!DOMINIOS.has(url.hostname) || !request.headers.get("cf-access-jwt-assertion")) return json({ erro: "acesso negado" }, 403);
      const dias = Math.max(1, Math.min(400, parseInt(url.searchParams.get("dias") || "30", 10) || 30));
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      return json(await obj.resumo(dias));
    }

    // Idiomas em repouso (en/es/it fora do ar até a aprovação do AdSense): /en/..., /es/..., /it/... levam (302)
    // à mesma página em português, pelo mapa que o gerador grava em repouso.json
    const prim = url.pathname.split("/")[1] || "";
    if (prim.length === 2 && request.method === "GET") {
      const r = await repouso(env, url);
      if (r.idiomas.includes(prim)) {
        const chave = decodeURIComponent(url.pathname).replace(/\/$/, "").replace(/\.html$/, "");
        const destino = r.mapa[chave] || "/";
        return Response.redirect(new URL(destino, url.origin).toString(), 302);
      }
    }

    const resp = await env.ASSETS.fetch(request);
    // Endereço antigo com nome traduzido na raiz (ex.: /politique-editoriale.html): 301 para a página em português
    if (resp.status === 404 && request.method === "GET") {
      const r = await repouso(env, url);
      const chave = decodeURIComponent(url.pathname).replace(/\/$/, "").replace(/\.html$/, "");
      const destino = (r.raiz || {})[chave];
      if (destino) return Response.redirect(new URL(destino, url.origin).toString(), 301);
    }
    return resp;
  },
};

let REPOUSO = null;
async function repouso(env, url) {
  if (REPOUSO) return REPOUSO;
  try {
    const r = await env.ASSETS.fetch(new Request(new URL("/repouso.json", url.origin)));
    REPOUSO = r.ok ? await r.json() : { idiomas: [], mapa: {} };
  } catch (e) {
    REPOUSO = { idiomas: [], mapa: {} };
  }
  return REPOUSO;
}

export class Metricas extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS visitas (
      ts INTEGER NOT NULL, dia TEXT NOT NULL, hora INTEGER NOT NULL, caminho TEXT, origem TEXT, fonte TEXT, midia TEXT,
      campanha TEXT, conteudo TEXT, termo TEXT, pais TEXT, aparelho TEXT, idioma TEXT, visitante TEXT)`);
    this.sql.exec("CREATE INDEX IF NOT EXISTS visitas_dia ON visitas(dia)");
    // coluna do artigo lido (acrescentada depois da primeira versão)
    if (!this.sql.exec("PRAGMA table_info(visitas)").toArray().some((c) => c.name === "slug")) this.sql.exec("ALTER TABLE visitas ADD COLUMN slug TEXT DEFAULT ''");
    this.sql.exec("CREATE TABLE IF NOT EXISTS sal (dia TEXT PRIMARY KEY, valor TEXT NOT NULL)");
    // visitas em /it/ que tenham ficado marcadas com outro idioma enquanto o italiano esteve fora do contador (11/11/2026)
    this.sql.exec("UPDATE visitas SET idioma = 'it' WHERE (caminho = '/it' OR caminho LIKE '/it/%') AND idioma <> 'it'");
    this.sql.exec(`CREATE TABLE IF NOT EXISTS contatos (ts INTEGER NOT NULL, dia TEXT NOT NULL, nome TEXT, email TEXT, motivo TEXT,
      mensagem TEXT, idioma TEXT, pagina TEXT, remetente TEXT)`);
  }

  // Mensagens do formulário de contato. "remetente" é um código embaralhado (como nas visitas) só para limitar o envio por dia.
  async guardarContato(m) {
    const ts = Date.now();
    const [dia] = Metricas.diaHora(ts);
    const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(this.salDoDia(dia) + "|c|" + m.chave));
    const remetente = [...new Uint8Array(bytes).slice(0, 8)].map((b) => b.toString(16).padStart(2, "0")).join("");
    const n = this.sql.exec("SELECT COUNT(*) AS n FROM contatos WHERE dia = ? AND remetente = ?", dia, remetente).toArray()[0].n;
    if (n >= 5) return { ok: false };
    this.sql.exec("INSERT INTO contatos (ts, dia, nome, email, motivo, mensagem, idioma, pagina, remetente) VALUES (?,?,?,?,?,?,?,?,?)",
      ts, dia, m.nome, m.email, m.motivo, m.mensagem, m.idioma, m.pagina, remetente);
    // guarda no máximo um ano de mensagens
    this.sql.exec("DELETE FROM contatos WHERE ts < ?", ts - 365 * 86400000);
    return { ok: true };
  }

  async listarContatos() {
    return this.sql.exec("SELECT ts, nome, email, motivo, mensagem, idioma, pagina FROM contatos ORDER BY ts DESC LIMIT 200").toArray();
  }

  static diaHora(ts) {
    const d = new Date(ts + FUSO_MS);
    return [d.toISOString().slice(0, 10), d.getUTCHours()];
  }

  salDoDia(dia) {
    const r = this.sql.exec("SELECT valor FROM sal WHERE dia = ?", dia).toArray();
    if (r.length) return r[0].valor;
    const valor = crypto.randomUUID() + crypto.randomUUID();
    this.sql.exec("DELETE FROM sal WHERE dia <> ?", dia);
    this.sql.exec("INSERT INTO sal (dia, valor) VALUES (?, ?)", dia, valor);
    return valor;
  }

  async registrar(v) {
    const ts = Date.now();
    const [dia, hora] = Metricas.diaHora(ts);
    const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(this.salDoDia(dia) + "|" + v.chave));
    const visitante = [...new Uint8Array(bytes).slice(0, 8)].map((b) => b.toString(16).padStart(2, "0")).join("");
    this.sql.exec(
      "INSERT INTO visitas (ts, dia, hora, caminho, origem, fonte, midia, campanha, conteudo, termo, pais, aparelho, idioma, visitante, slug) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      ts, dia, hora, v.caminho, v.origem, v.fonte, v.midia, v.campanha, v.conteudo, v.termo, v.pais, v.aparelho, v.idioma, visitante, v.slug || "");
  }

  // Artigos mais lidos dos últimos 7 dias (somando todos os idiomas), por visitantes únicos de cada dia.
  // "alta": até 3 artigos com pelo menos ALTA_MIN leitores na semana. "lidas": ordem para a lista "Mais lidas" (os lidos primeiro, o resto na ordem padrão).
  async emAlta() {
    const ALTA_MIN = 10;
    const [desde] = Metricas.diaHora(Date.now() - 6 * 86400000);
    const r = this.sql.exec(
      "SELECT slug, COUNT(DISTINCT dia || visitante) AS u FROM visitas WHERE dia >= ? AND slug <> '' GROUP BY slug ORDER BY u DESC, MAX(ts) DESC LIMIT 20",
      desde).toArray();
    return { alta: r.filter((x) => x.u >= ALTA_MIN).slice(0, 3).map((x) => x.slug), lidas: r.map((x) => x.slug) };
  }

  // Pessoas no site agora: quem abriu alguma página nos últimos 5 minutos (estimativa padrão de "ao vivo", sem rastrear ninguém)
  async aoVivo() {
    const desde = Date.now() - 5 * 60000;
    const q = (s, ...a) => this.sql.exec(s, ...a).toArray();
    const ORIGEM_SQL = `CASE WHEN origem LIKE '%telegram%' THEN 'telegram' WHEN origem = 'direto' AND campanha = 'parceiro' AND midia <> '' THEN midia
      WHEN origem = 'direto' AND fonte <> '' THEN fonte ELSE origem END`;
    // página atual de cada pessoa = a última que ela abriu
    const ultimas = q(`SELECT v.caminho, v.slug, v.aparelho, v.pais FROM visitas v
      JOIN (SELECT visitante, MAX(ts) AS t FROM visitas WHERE ts >= ? GROUP BY visitante) u ON u.visitante = v.visitante AND u.t = v.ts`, desde);
    const conta = (lista, chave) => Object.entries(lista.reduce((a, x) => { a[x[chave]] = (a[x[chave]] || 0) + 1; return a; }, {}))
      .map(([nome, n]) => ({ nome, n })).sort((a, b) => b.n - a.n);
    return {
      gerado: Date.now(),
      pessoas: ultimas.length,
      paginas: conta(ultimas, "caminho").slice(0, 10),
      aparelhos: conta(ultimas, "aparelho"),
      origens: q(`SELECT ${ORIGEM_SQL} AS nome, COUNT(DISTINCT visitante) AS n FROM visitas WHERE ts >= ? AND origem <> 'interno' GROUP BY 1 ORDER BY n DESC LIMIT 6`, desde),
    };
  }

  async resumo(dias) {
    const agora = Date.now();
    const [hoje] = Metricas.diaHora(agora);
    const [ontem] = Metricas.diaHora(agora - 86400000);
    const [inicio] = Metricas.diaHora(agora - (dias - 1) * 86400000);
    const [ini7] = Metricas.diaHora(agora - 6 * 86400000);
    const q = (s, ...a) => this.sql.exec(s, ...a).toArray();
    const contagem = (desde, ate) => {
      const v = q("SELECT COUNT(*) AS v FROM visitas WHERE dia BETWEEN ? AND ?", desde, ate)[0].v;
      const u = q("SELECT COALESCE(SUM(u),0) AS u FROM (SELECT COUNT(DISTINCT visitante) AS u FROM visitas WHERE dia BETWEEN ? AND ? GROUP BY dia)", desde, ate)[0].u;
      return { visualizacoes: v, visitantes: u };
    };
    const ORIGEM_SQL = `CASE WHEN origem LIKE '%telegram%' THEN 'telegram'
      WHEN origem = 'direto' AND campanha = 'parceiro' AND midia <> '' THEN midia
      WHEN origem = 'direto' AND fonte <> '' THEN fonte ELSE origem END`;
    const top = (campo, limite, extra = "") => q(
      `SELECT ${campo} AS nome, COUNT(*) AS v, COUNT(DISTINCT dia || visitante) AS u FROM visitas WHERE dia >= ? ${extra} GROUP BY ${campo} ORDER BY v DESC LIMIT ?`,
      inicio, limite);
    const primeiro = q("SELECT MIN(ts) AS t FROM visitas")[0].t;
    return {
      gerado: agora,
      dias,
      inicio_contagem: primeiro,
      agora: { visualizacoes: q("SELECT COUNT(*) AS v FROM visitas WHERE ts >= ?", agora - 30 * 60000)[0].v },
      hoje: contagem(hoje, hoje),
      ontem: contagem(ontem, ontem),
      semana: contagem(ini7, hoje),
      periodo: contagem(inicio, hoje),
      total: contagem("0000-00-00", "9999-99-99"),
      serie: q("SELECT dia, COUNT(*) AS v, COUNT(DISTINCT visitante) AS u FROM visitas WHERE dia >= ? GROUP BY dia ORDER BY dia", inicio),
      horas: q("SELECT hora, COUNT(*) AS v FROM visitas WHERE dia >= ? GROUP BY hora ORDER BY hora", inicio),
      paginas: top("caminho", 25),
      artigos: q("SELECT slug AS nome, COUNT(*) AS v, COUNT(DISTINCT dia || visitante) AS u FROM visitas WHERE dia >= ? AND slug <> '' GROUP BY slug ORDER BY u DESC LIMIT 25", inicio),
      origens: top(ORIGEM_SQL, 12, "AND origem <> 'interno'"),
      fontes: top("fonte", 12, "AND fonte <> ''"),
      parceiros: q("SELECT fonte AS parceiro, midia AS rede, termo AS jogo, COUNT(*) AS v, COUNT(DISTINCT dia || visitante) AS u FROM visitas WHERE dia >= ? AND campanha = 'parceiro' GROUP BY fonte, midia, termo ORDER BY v DESC LIMIT 40", inicio),
      paises: top("pais", 12),
      aparelhos: top("aparelho", 3),
      idiomas: top("idioma", 9),
    };
  }
}
