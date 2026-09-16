# Redaction: what it is, and what it is not

**Short answer: the redactor is a seatbelt, not a vault. Keep it on, but do
not rely on it as your only protection.** It is best-effort pattern matching.
It cannot be proven to catch every secret, and this document is honest about
where it fails so you can decide with open eyes before making anything public.

## Why it exists (the threat model)

SpeedReader speaks text *out loud* — often through glasses, into a room — and
shows it in the follow-along window. The redactor's job is narrow: **don't
announce a credential into the air, and don't paint it on screen.** It is
defense-in-depth against an accidental read of a key that happens to be in the
text you pointed at. It is **not** a data-loss-prevention system and does not
sanitise files.

It runs on the full source text *before* anything is spoken or displayed, for
every source (selection, window, Claude transcript). It is **on by default**;
`--no-redact`, or unticking "Redact secrets" in settings, turns it off.

## What it catches

Secrets with a distinctive *shape* — the whole list is one array in
`reader.py`, auditable in a minute:

- Anthropic (`sk-ant-…`), OpenAI (`sk-…`, `sk-proj-…`), Stripe
  (`sk_live_…`), Google API (`AIza…`) and OAuth (`ya29.…`) keys
- GitHub (`ghp_…`, `github_pat_…`), GitLab (`glpat-…`), Slack (`xox…`),
  SendGrid (`SG.…`), npm (`npm_…`), PyPI (`pypi-…`), AWS (`AKIA…`),
  Telegram bot tokens
- JSON Web Tokens (`eyJ….….…`) and `Bearer …` headers
- PEM private-key blocks (`-----BEGIN … PRIVATE KEY-----`)
- URLs with an inline `user:password@host`
- `password = …`, `token: …`, `api_key=…` assignments
- Long hex blobs (40+), and a catch-all for any unbroken 20+ char token
  mixing letters and digits

Each becomes the spoken words "… redacted", so you *hear* that something was
skipped rather than losing the sentence silently.

## What it CANNOT catch (know these before going public)

- **A password that looks like a word.** `hunter2`, `correct-horse-battery`,
  a PIN, a passphrase — nothing about them says "secret". Not caught.
- **Unknown or new formats.** A vendor token shape not in the list above walks
  straight through. The list is finite; the world of secrets is not.
- **Secrets split across tokens or lines** so no single match sees the whole
  thing.
- **Base64 / random blobs that are indistinguishable from ordinary data.**
  Redacting all of them would bleep legitimate text, so we don't.
- **A secret embedded in a word-with-digits token.** To avoid deleting real
  words (`GPT-4`, `COVID-19`, `IPv6`), tokens containing letters are kept —
  a secret hidden inside one would be read.
- **Anything with `--no-redact`,** or text you deliberately highlight while
  redaction is off.

## False positives

Tuned to avoid them — `scikit-learn`, `Message-ID`, project names like
`BirdsFlyPoopSimulator-GDD-v1-1` are left alone — but a novel value could trip
a rule. If you hear "… redacted" where nothing sensitive was, that is the
harmless direction, and you can look at the source.

## Failure mode

If redaction raises on pathological input the read aborts rather than speaking
unredacted text — it fails toward silence, not toward leaking.

## Recommendation for a public release

1. Ship it **on by default** (it is).
2. Link this page from the README so no one mistakes it for a guarantee.
3. Tell users plainly: **do not point SpeedReader at a secrets file** expecting
   it to be sanitised. Redaction is there for the stray key in otherwise
   ordinary text, not as a filter you can trust with a vault.

The rules are easy to extend — add a `(regex, label)` pair to `REDACT` in
`reader.py` — but adding rules never turns best-effort into a guarantee.
