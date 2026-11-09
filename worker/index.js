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
const IDIOMAS = new Set(["en", "es", "fr", "de", "it", "ja", "zh", "ar"]);
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

function origemDe(ref) {
  if (!ref) return "direto";
  try {
    const h = new URL(ref).hostname.replace(/^www\./, "").replace(/^m\./, "").replace(/^l\./, "").replace(/^lm\./, "");
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
  async fetch(request, env) {
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
      const visita = {
        caminho,
        origem: origemDe(d.r),
        fonte: corta(q.get("utm_source"), 60).toLowerCase(),
        midia: corta(q.get("utm_medium"), 60).toLowerCase(),
        campanha: corta(q.get("utm_campaign"), 80).toLowerCase(),
        conteudo: corta(q.get("utm_content"), 60).toLowerCase(),
        termo: corta(q.get("utm_term"), 60).toLowerCase(),
        pais: corta((request.cf && request.cf.country) || "", 2),
        aparelho: aparelho(ua),
        idioma: IDIOMAS.has(prim) ? prim : "pt",
        chave: (request.headers.get("cf-connecting-ip") || "") + "|" + ua,
      };
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      await obj.registrar(visita);
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/admin/api/metricas") {
      // só pelo domínio do site (onde o Cloudflare Access pede login) e com o login do Access presente
      if (!DOMINIOS.has(url.hostname) || !request.headers.get("cf-access-jwt-assertion")) return json({ erro: "acesso negado" }, 403);
      const dias = Math.max(1, Math.min(400, parseInt(url.searchParams.get("dias") || "30", 10) || 30));
      const obj = env.METRICAS.get(env.METRICAS.idFromName("aloha"));
      return json(await obj.resumo(dias));
    }

    return env.ASSETS.fetch(request);
  },
};

export class Metricas extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS visitas (
      ts INTEGER NOT NULL, dia TEXT NOT NULL, hora INTEGER NOT NULL, caminho TEXT, origem TEXT, fonte TEXT, midia TEXT,
      campanha TEXT, conteudo TEXT, termo TEXT, pais TEXT, aparelho TEXT, idioma TEXT, visitante TEXT)`);
    this.sql.exec("CREATE INDEX IF NOT EXISTS visitas_dia ON visitas(dia)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS sal (dia TEXT PRIMARY KEY, valor TEXT NOT NULL)");
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
      "INSERT INTO visitas (ts, dia, hora, caminho, origem, fonte, midia, campanha, conteudo, termo, pais, aparelho, idioma, visitante) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      ts, dia, hora, v.caminho, v.origem, v.fonte, v.midia, v.campanha, v.conteudo, v.termo, v.pais, v.aparelho, v.idioma, visitante);
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
      origens: top("origem", 12, "AND origem <> 'interno'"),
      fontes: top("fonte", 12, "AND fonte <> ''"),
      parceiros: q("SELECT fonte AS parceiro, midia AS rede, termo AS jogo, COUNT(*) AS v, COUNT(DISTINCT dia || visitante) AS u FROM visitas WHERE dia >= ? AND campanha = 'parceiro' GROUP BY fonte, midia, termo ORDER BY v DESC LIMIT 40", inicio),
      paises: top("pais", 12),
      aparelhos: top("aparelho", 3),
      idiomas: top("idioma", 9),
    };
  }
}
