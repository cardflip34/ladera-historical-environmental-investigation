/**
 * Site-wide password gate (Vercel Routing Middleware, Edge runtime).
 *
 * Runs on the edge BEFORE any static file is served, so page HTML never leaves
 * the server unless the visitor is authenticated. This is real protection, not
 * a client-side overlay.
 *
 * The password is NEVER stored in this repository (the repo is public).
 *   - Preferred: set the `SITE_PASSWORD` environment variable in Vercel.
 *   - Fallback:  a SHA-256 hash of the password, below. The plaintext is not
 *                recoverable from the hash by reading this file.
 *
 * On success a signed-ish cookie is set so the visitor is not re-prompted.
 */

// SHA-256 of the site password. Used only when SITE_PASSWORD is not configured.
const FALLBACK_PW_SHA256 =
  '5256549128c9e68bfeedaa3a6bbfe1728b740bab8ee3293921a91b67e91d3b5f';

const COOKIE = 'cfp_access';
const COOKIE_SALT = ':cfp-v1';
const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

// Gate every path except Vercel's own internal routes, so the analytics beacon
// (/_vercel/insights/*) keeps working for authenticated visitors.
//
// Verified on production before widening: an unauthenticated request returns the
// login page with no static content, a wrong password is rejected, a correct one
// sets the cookie, and a cookie-bearing request receives the real file.
export const config = {
  matcher: ['/((?!_vercel).*)'],
};

const enc = new TextEncoder();

async function sha256(text) {
  const buf = await crypto.subtle.digest('SHA-256', enc.encode(text));
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/** Constant-time-ish comparison to avoid trivial timing leaks. */
function safeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) {
    return false;
  }
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/** Hash of the configured password (env var wins over the committed hash). */
async function expectedPasswordHash() {
  const fromEnv = process.env.SITE_PASSWORD;
  if (fromEnv) return sha256(fromEnv);
  return FALLBACK_PW_SHA256;
}

/** The value we expect in the access cookie. */
async function expectedCookieToken() {
  const fromEnv = process.env.SITE_PASSWORD;
  if (fromEnv) return sha256(fromEnv + COOKIE_SALT);
  // Derived from the hash so the cookie value is not the published hash itself.
  return sha256(FALLBACK_PW_SHA256 + COOKIE_SALT);
}

function readCookie(request, name) {
  const raw = request.headers.get('cookie') || '';
  for (const part of raw.split(';')) {
    const idx = part.indexOf('=');
    if (idx === -1) continue;
    if (part.slice(0, idx).trim() === name) return part.slice(idx + 1).trim();
  }
  return null;
}

/** Continue to the static file. This header is the Vercel middleware protocol. */
function proceed() {
  return new Response(null, { headers: { 'x-middleware-next': '1' } });
}

function loginPage(status, showError) {
  const err = showError
    ? '<p class="err" role="alert">That password is not correct. Please try again.</p>'
    : '';
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>California's Forgotten Past</title>
<link rel="icon" href="/favicon.ico" sizes="any">
<style>
  :root{--paper:#f7f5f0;--ink:#16233a;--ink2:#48586c;--line:#ddd7ca;
        --accent:#2f6087;--brass:#a97e1f;--card:#fffdf8;--field:#fff;--on-accent:#fff}
  @media (prefers-color-scheme:dark){:root{--paper:#141a24;--ink:#eef2f7;--ink2:#a9b6c6;
        --line:#2b3746;--accent:#7fb0d6;--brass:#d8b662;--card:#1b2330;--field:#111823;--on-accent:#0e131b}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);min-height:100vh;
    display:flex;align-items:center;justify-content:center;padding:32px;
    font:16.5px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:430px;width:100%}
  .eyebrow{font-size:11.5px;letter-spacing:.15em;text-transform:uppercase;
    color:var(--brass);font-weight:700;margin:0 0 14px}
  .mh-title{display:block;font-family:"Iowan Old Style",Georgia,serif;font-weight:600;
    font-size:clamp(27px,5.6vw,38px);line-height:1.05;letter-spacing:-.015em;margin:0 0 5px}
  .mh-tagline{display:block;font-family:"Iowan Old Style",Georgia,serif;font-style:italic;
    font-weight:500;color:var(--brass);font-size:clamp(17px,3.2vw,22px);line-height:1.2;margin:0}
  .rule{width:66px;height:3px;background:var(--brass);border-radius:2px;margin:18px 0 22px}
  p.sub{color:var(--ink2);font-size:15px;margin:0 0 22px}
  label{display:block;font-weight:600;font-size:13.5px;margin:0 0 6px}
  input{width:100%;font:inherit;color:var(--ink);background:var(--field);
    border:1px solid var(--line);border-radius:9px;padding:11px 13px}
  input:focus{outline:none;border-color:var(--accent)}
  button{margin-top:14px;width:100%;cursor:pointer;font-weight:600;font-size:15.5px;
    padding:12px 22px;border-radius:9px;border:1px solid var(--accent);
    background:var(--accent);color:var(--on-accent)}
  button:hover{filter:brightness(1.07)}
  .err{color:#b23b3b;font-weight:600;font-size:14px;margin:14px 0 0}
  .note{color:var(--ink2);font-size:12.5px;margin:22px 0 0;padding-top:14px;
    border-top:1px solid var(--line)}
</style></head><body>
<main class="wrap">
  <p class="eyebrow">Independent research &amp; data-organization project</p>
  <h1 style="margin:0">
    <span class="mh-title">California&rsquo;s Forgotten Past</span>
    <span class="mh-tagline">The Arsenic Cattle-Dipping Era</span>
  </h1>
  <div class="rule" aria-hidden="true"></div>
  <p class="sub">This research is not yet public. Please enter the password to continue.</p>
  <form method="POST" action="/__unlock">
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password"
           autofocus required>
    <button type="submit">Enter</button>
  </form>
  ${err}
  <p class="note">If you were given access and this is not working, please get in touch
    with the author.</p>
</main></body></html>`;
  return new Response(html, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store, must-revalidate',
      'x-robots-tag': 'noindex, nofollow',
    },
  });
}

export default async function middleware(request) {
  const url = new URL(request.url);

  // 1. Already authenticated?
  const cookie = readCookie(request, COOKIE);
  if (cookie && safeEqual(cookie, await expectedCookieToken())) {
    return proceed();
  }

  // 2. Handle a login submission.
  if (url.pathname === '/__unlock' && request.method === 'POST') {
    let submitted = '';
    try {
      const form = await request.formData();
      submitted = String(form.get('password') || '');
    } catch {
      submitted = '';
    }

    if (safeEqual(await sha256(submitted), await expectedPasswordHash())) {
      const token = await expectedCookieToken();
      return new Response(null, {
        status: 303,
        headers: {
          location: '/',
          'set-cookie':
            `${COOKIE}=${token}; Path=/; Max-Age=${MAX_AGE}; ` +
            'HttpOnly; Secure; SameSite=Lax',
          'cache-control': 'no-store',
        },
      });
    }
    return loginPage(401, true);
  }

  // 3. Anything else: show the gate. 401 keeps crawlers from indexing content.
  return loginPage(401, false);
}
