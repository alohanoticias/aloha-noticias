// Aloha Notícias — Worker
// Serve o site estático (pasta publico/) e a API do painel de acessos (/api/ga), que lê o Google Analytics 4.
// Segredos (configurar no painel da Cloudflare, nunca no código):
//   GA_PROPERTY_ID   número da propriedade do GA4 (ex.: 123456789)
//   GA_SA_EMAIL      e-mail da conta de serviço do Google Cloud
//   GA_SA_KEY        chave privada da conta de serviço (o campo private_key do JSON)
//   ACCESS_TEAM      nome da equipe no Cloudflare Zero Trust (o "xxx" de xxx.cloudflareaccess.com)
//   ACCESS_AUD       "Application Audience (AUD) Tag" do aplicativo do Access que protege /admin e /api
// Enquanto ACCESS_TEAM/ACCESS_AUD não existirem, /admin continua abrindo como antes, mas /api/ga fica bloqueada.

const ESCOPO = "https://www.googleapis.com/auth/analytics.readonly";
let tokenCache = { token: "", exp: 0 };
let certsCache = { chaves: null, exp: 0 };

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const protegido = url.pathname.startsWith("/admin") || url.pathname.startsWith("/api/");
    const accessConfigurado = Boolean(env.ACCESS_TEAM && env.ACCESS_AUD);

    if (protegido && accessConfigurado) {
      const ok = await acessoValido(req, env).catch(() => false);
      if (!ok) return new Response("Acesso restrito aos administradores.", { status: 403, headers: { "Cache-Control": "no-store" } });
    }

    if (url.pathname === "/api/ga") {
      if (!accessConfigurado) return json({ erro: "O login dos admins (Cloudflare Access) ainda não foi configurado." }, 403);
      if (req.method !== "POST") return json({ erro: "Use POST." }, 405);
      try {
        const pedido = await req.json();
        return json(await relatorio(pedido, env));
      } catch (e) {
        return json({ erro: String(e.message || e).slice(0, 400) }, 500);
      }
    }
    return env.ASSETS.fetch(req);
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" } });
}

// ---------- Cloudflare Access: confere o token de login ----------
function b64urlBytes(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
}

async function acessoValido(req, env) {
  const jwt = req.headers.get("Cf-Access-Jwt-Assertion") || (req.headers.get("Cookie") || "").match(/CF_Authorization=([^;]+)/)?.[1];
  if (!jwt) return false;
  const [h, p, s] = jwt.split(".");
  const cab = JSON.parse(new TextDecoder().decode(b64urlBytes(h)));
  const dados = JSON.parse(new TextDecoder().decode(b64urlBytes(p)));
  const agora = Date.now() / 1000;
  const auds = Array.isArray(dados.aud) ? dados.aud : [dados.aud];
  if (!auds.includes(env.ACCESS_AUD) || dados.exp < agora) return false;
  if (dados.iss !== `https://${env.ACCESS_TEAM}.cloudflareaccess.com`) return false;
  if (!certsCache.chaves || certsCache.exp < agora) {
    const r = await fetch(`https://${env.ACCESS_TEAM}.cloudflareaccess.com/cdn-cgi/access/certs`);
    certsCache = { chaves: (await r.json()).keys, exp: agora + 3600 };
  }
  const jwk = certsCache.chaves.find((k) => k.kid === cab.kid);
  if (!jwk) return false;
  const chave = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  return crypto.subtle.verify("RSASSA-PKCS1-v1_5", chave, b64urlBytes(s), new TextEncoder().encode(`${h}.${p}`));
}

// ---------- Google: token da conta de serviço ----------
function b64url(bytes) {
  let s = "";
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function tokenGoogle(env) {
  const agora = Math.floor(Date.now() / 1000);
  if (tokenCache.token && tokenCache.exp - 60 > agora) return tokenCache.token;
  const pem = env.GA_SA_KEY.replace(/\\n/g, "\n").replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
  const der = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  const chave = await crypto.subtle.importKey("pkcs8", der, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const enc = (o) => b64url(new TextEncoder().encode(JSON.stringify(o)));
  const corpo = `${enc({ alg: "RS256", typ: "JWT" })}.${enc({ iss: env.GA_SA_EMAIL, scope: ESCOPO, aud: "https://oauth2.googleapis.com/token", iat: agora, exp: agora + 3600 })}`;
  const assinatura = b64url(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", chave, new TextEncoder().encode(corpo)));
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${corpo}.${assinatura}`,
  });
  const j = await r.json();
  if (!j.access_token) throw new Error("Não foi possível entrar no Google: " + (j.error_description || j.error || r.status));
  tokenCache = { token: j.access_token, exp: agora + (j.expires_in || 3600) };
  return j.access_token;
}

async function ga(env, metodo, corpo) {
  const r = await fetch(`https://analyticsdata.googleapis.com/v1beta/properties/${env.GA_PROPERTY_ID}:${metodo}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${await tokenGoogle(env)}`, "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  const j = await r.json();
  if (j.error) throw new Error(j.error.message);
  return j;
}

// Converte a resposta do GA em uma lista simples de linhas {dimensao: valor, metrica: numero}
function linhas(res) {
  const dims = (res.dimensionHeaders || []).map((d) => d.name);
  const mets = (res.metricHeaders || []).map((m) => m.name);
  return (res.rows || []).map((r) => {
    const o = {};
    dims.forEach((d, i) => (o[d] = r.dimensionValues[i].value));
    mets.forEach((m, i) => (o[m] = Number(r.metricValues[i].value)));
    return o;
  });
}

// ---------- Relatórios permitidos (lista fechada) ----------
const DATA = /^(\d{4}-\d{2}-\d{2}|today|yesterday|\d{1,3}daysAgo)$/;
const AGRUP = { hora: "dateHour", dia: "date", semana: "isoYearIsoWeek", mes: "yearMonth" };

async function relatorio(p, env) {
  if (!env.GA_PROPERTY_ID || !env.GA_SA_EMAIL || !env.GA_SA_KEY) throw new Error("Faltam os segredos do Google Analytics no Worker (GA_PROPERTY_ID, GA_SA_EMAIL, GA_SA_KEY).");
  const inicio = DATA.test(p.inicio || "") ? p.inicio : "7daysAgo";
  const fim = DATA.test(p.fim || "") ? p.fim : "today";
  const periodo = [{ startDate: inicio, endDate: fim }];
  const base = { dateRanges: periodo, keepEmptyRows: false };
  const lim = Math.min(Number(p.limite) || 25, 250);

  switch (p.tipo) {
    case "tempo_real": {
      const [tot, paginas, paises, origem] = await Promise.all([
        ga(env, "runRealtimeReport", { metrics: [{ name: "activeUsers" }] }),
        ga(env, "runRealtimeReport", { dimensions: [{ name: "unifiedScreenName" }], metrics: [{ name: "activeUsers" }], limit: 10 }),
        ga(env, "runRealtimeReport", { dimensions: [{ name: "country" }], metrics: [{ name: "activeUsers" }], limit: 10 }),
        ga(env, "runRealtimeReport", { dimensions: [{ name: "eventName" }], metrics: [{ name: "eventCount" }], limit: 50 }),
      ]);
      return {
        ativos: linhas(tot)[0]?.activeUsers || 0,
        paginas: linhas(paginas),
        paises: linhas(paises),
        eventos: linhas(origem).filter((l) => /^(visita_|parceiro_)/.test(l.eventName)),
      };
    }
    case "resumo": {
      const res = await ga(env, "runReport", {
        dateRanges: [{ startDate: inicio, endDate: fim, name: "atual" }, ...(p.anterior ? [{ startDate: p.anterior.inicio, endDate: p.anterior.fim, name: "anterior" }].filter((d) => DATA.test(d.startDate) && DATA.test(d.endDate)) : [])],
        metrics: ["activeUsers", "newUsers", "sessions", "screenPageViews", "averageSessionDuration", "engagementRate"].map((name) => ({ name })),
      });
      return { linhas: linhas(res) };
    }
    case "serie": {
      const dim = AGRUP[p.agrupar] || "date";
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: dim }], metrics: [{ name: "activeUsers" }, { name: "sessions" }, { name: "screenPageViews" }], orderBys: [{ dimension: { dimensionName: dim } }], limit: 10000 });
      return { dimensao: dim, linhas: linhas(res) };
    }
    case "horas": {
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: "hour" }], metrics: [{ name: "sessions" }, { name: "screenPageViews" }], orderBys: [{ dimension: { dimensionName: "hour" } }] });
      return { linhas: linhas(res) };
    }
    case "dias_semana": {
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: "dayOfWeek" }], metrics: [{ name: "sessions" }], orderBys: [{ dimension: { dimensionName: "dayOfWeek" } }] });
      return { linhas: linhas(res) };
    }
    case "origens": {
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: "sessionSource" }, { name: "sessionMedium" }], metrics: [{ name: "sessions" }, { name: "activeUsers" }], orderBys: [{ metric: { metricName: "sessions" }, desc: true }], limit: lim });
      return { linhas: linhas(res) };
    }
    case "canais": {
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: "sessionDefaultChannelGroup" }], metrics: [{ name: "sessions" }], orderBys: [{ metric: { metricName: "sessions" }, desc: true }] });
      return { linhas: linhas(res) };
    }
    case "parceiros": {
      const res = await ga(env, "runReport", {
        ...base,
        dimensions: [{ name: "sessionSource" }, { name: "sessionMedium" }, { name: "sessionManualAdContent" }],
        metrics: [{ name: "sessions" }, { name: "activeUsers" }, { name: "screenPageViews" }],
        dimensionFilter: { filter: { fieldName: "sessionCampaignName", stringFilter: { value: "parceiro", matchType: "EXACT" } } },
        orderBys: [{ metric: { metricName: "sessions" }, desc: true }],
        limit: lim,
      });
      return { linhas: linhas(res) };
    }
    case "paginas": {
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: "pageTitle" }, { name: "pagePath" }], metrics: [{ name: "screenPageViews" }, { name: "activeUsers" }], orderBys: [{ metric: { metricName: "screenPageViews" }, desc: true }], limit: lim });
      return { linhas: linhas(res) };
    }
    case "paises":
    case "cidades":
    case "aparelhos":
    case "idiomas": {
      const dim = { paises: "country", cidades: "city", aparelhos: "deviceCategory", idiomas: "language" }[p.tipo];
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: dim }], metrics: [{ name: "activeUsers" }, { name: "sessions" }], orderBys: [{ metric: { metricName: "activeUsers" }, desc: true }], limit: lim });
      return { linhas: linhas(res) };
    }
    case "versoes": {
      // idioma da versão do site lida: primeiro trecho do caminho (/en/, /es/...), sem prefixo = português
      const res = await ga(env, "runReport", { ...base, dimensions: [{ name: "pagePath" }], metrics: [{ name: "screenPageViews" }], limit: 10000 });
      const soma = {};
      for (const l of linhas(res)) {
        const m = l.pagePath.match(/^\/(en|es|fr|de|it|ja|zh|ar)(\/|$)/);
        const k = m ? m[1] : "pt";
        soma[k] = (soma[k] || 0) + l.screenPageViews;
      }
      return { linhas: Object.entries(soma).map(([versao, screenPageViews]) => ({ versao, screenPageViews })).sort((a, b) => b.screenPageViews - a.screenPageViews) };
    }
    default:
      throw new Error("Relatório desconhecido.");
  }
}
