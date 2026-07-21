export const meta = {
  name: 'statewide-dipping-landuse-sweep',
  description: 'Replicate the Ladera Ranch land-use / dipping-era screening across California ranchos and the communities built on them. Produces a graded, verified lead list -- never a contamination claim.',
  whenToUse: 'Overnight statewide screening of former cattle ranchos in the 1907-1915 tick-quarantine counties. Review docs/statewide_program/MASTER_PLAN.md first.',
  phases: [
    { title: 'Triage', detail: 'one cheap agent per target: quarantine county? residential? worth a deep dive?' },
    { title: 'Deep dive', detail: 'full documentary pipeline per prioritised target' },
    { title: 'Verify', detail: 'a skeptic refutes each finding' },
    { title: 'Synthesize', detail: 'statewide review-gap ranking' },
  ],
}

// ---- Targets. Embedded so the script is self-contained; override by passing args.targets. ----
const TARGETS = (args && args.targets) || [
  { id: 'T01-TRABUCO',      rancho: 'Rancho Trabuco',                        county: 'Orange',         tier: 'heavy',  status: 'residential_mpc',      communities: 'Coto de Caza, Wagon Wheel, Trabuco Canyon' },
  { id: 'T02-IRVINE',       rancho: 'Irvine Ranch',                          county: 'Orange',         tier: 'heavy',  status: 'residential_mpc',      communities: 'Irvine, Tustin, Newport Coast, Lake Forest, Laguna Woods' },
  { id: 'T03-SIMI',         rancho: 'Rancho Simi',                           county: 'Ventura',        tier: 'heavy',  status: 'residential_mpc',      communities: 'Simi Valley, Moorpark edge' },
  { id: 'T04-PENASQUITOS',  rancho: 'Rancho Santa Maria de Los Penasquitos', county: 'San Diego',      tier: 'heavy',  status: 'residential_mpc',      communities: 'Rancho Penasquitos, Mira Mesa, Carmel Valley' },
  { id: 'T05-SANBERNARDO',  rancho: 'Rancho San Bernardo',                   county: 'San Diego',      tier: 'heavy',  status: 'residential_mpc',      communities: 'Rancho Bernardo, Poway edge' },
  { id: 'T06-SANDIEGUITO',  rancho: 'Rancho San Dieguito',                   county: 'San Diego',      tier: 'heavy',  status: 'residential_mpc',      communities: 'Rancho Santa Fe, Del Mar, Solana Beach' },
  { id: 'T07-SESPE',        rancho: 'Rancho Sespe',                          county: 'Ventura',        tier: 'heavy',  status: 'agricultural_partial', communities: 'Fillmore, Rancho Sespe citrus' },
  { id: 'T08-NEWHALL',      rancho: 'Rancho San Francisco / Newhall Ranch',  county: 'Los Angeles',    tier: 'lesser', status: 'residential_mpc',      communities: 'Santa Clarita, Valencia, Newhall, Saugus, Canyon Country' },
  { id: 'T09-LOSCERRITOS',  rancho: 'Rancho Los Cerritos',                   county: 'Los Angeles',    tier: 'lesser', status: 'residential_mpc',      communities: 'Long Beach, Lakewood, Cerritos, Downey, Bellflower' },
  { id: 'T10-LOSALAMITOS',  rancho: 'Rancho Los Alamitos',                   county: 'Los Angeles',    tier: 'lesser', status: 'residential_mpc',      communities: 'Long Beach, Los Alamitos, Rossmoor, Seal Beach, Cypress' },
  { id: 'T11-CUCAMONGA',    rancho: 'Rancho Cucamonga',                      county: 'San Bernardino', tier: 'lesser', status: 'residential_mpc',      communities: 'Rancho Cucamonga' },
  { id: 'T12-JURUPA',       rancho: 'Rancho Jurupa',                         county: 'Riverside',      tier: 'lesser', status: 'residential_mpc',      communities: 'Riverside, Jurupa Valley' },
  { id: 'T13-SANTAMARGARITA',rancho:'Rancho Santa Margarita y Las Flores',   county: 'San Diego',      tier: 'heavy',  status: 'federal_undeveloped',  communities: 'Camp Pendleton, San Onofre State Beach' },
  { id: 'T14-TEJON',        rancho: 'Tejon Ranch',                           county: 'Kern',           tier: 'lesser', status: 'largely_unbuilt',      communities: 'Lebec; planned Centennial/Grapevine (unbuilt)' },
  { id: 'T15-MILLERLUX',    rancho: 'Miller & Lux holdings',                 county: 'Fresno',         tier: 'heavy',  status: 'agricultural',         communities: 'Los Banos, Dos Palos, Firebaugh (farmland)' },
]

// ---- Standing rules injected into every agent prompt ----
const RULES = `
NON-NEGOTIABLE RULES (this is a hypothesis-neutral public-records screening, not an accusation):
1. NEVER state or imply that any community is contaminated. The only soil fact anywhere is "unstudied".
2. NEVER fabricate a source, date, acreage, URL, or quotation. Failed searches are dead ends -- report the exact query.
3. Every finding carries its LIMITING/CONTRADICTORY evidence, or an explicit "none identified".
4. Grade every source A1/A2/B1/B2/C/D; never silently promote a lower grade.
5. No individual, address, parcel-owner, or health data. Aggregate/land-use only.
6. Distinguish "the searchable materials do not appear to identify X" from "X did not happen". Never claim the latter.
Violating any rule invalidates the output.`

const QUARANTINE_HEAVY = 'San Luis Obispo, Santa Barbara, San Diego, Orange, Fresno, Ventura'
const QUARANTINE_LESSER = 'Tulare, Kern, Kings, Los Angeles, Riverside, San Bernardino, Madera'

const TRIAGE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['target_id', 'quarantine_county', 'land_is_residential', 'deep_dive_recommended', 'priority_score', 'notes'],
  properties: {
    target_id: { type: 'string' },
    quarantine_county: { type: 'boolean' },
    land_is_residential: { type: 'boolean' },
    earliest_imagery_year: { type: 'string' },
    review_start_year_estimate: { type: 'string' },
    deep_dive_recommended: { type: 'boolean' },
    priority_score: { type: 'number' },
    notes: { type: 'string' },
  },
}

const FINDING = {
  type: 'object', additionalProperties: false,
  required: ['claim', 'classification', 'confidence', 'supporting', 'counter_evidence', 'citation'],
  properties: {
    claim: { type: 'string' },
    classification: { type: 'string', enum: ['ESTABLISHED FACT', 'HISTORICAL CONTEXT', 'INVESTIGATIVE LEAD', 'OPEN QUESTION'] },
    confidence: { type: 'string', enum: ['High', 'Medium', 'Low', 'None'] },
    supporting: { type: 'string' },
    counter_evidence: { type: 'string' },
    citation: { type: 'string' },
  },
}

const DEEPDIVE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['target_id', 'earliest_imagery', 'review_start_year', 'review_gap_years', 'dipping_records_summary', 'sampling_frame_plausibility', 'findings', 'dead_ends'],
  properties: {
    target_id: { type: 'string' },
    earliest_imagery: { type: 'string' },
    review_start_year: { type: 'string' },
    review_gap_years: { type: 'string' },
    dipping_records_summary: { type: 'string' },
    sampling_frame_plausibility: { type: 'string' },
    findings: { type: 'array', items: FINDING },
    dead_ends: { type: 'array', items: { type: 'string' } },
    output_file_written: { type: 'string' },
  },
}

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['target_id', 'confirmed_count', 'demoted', 'integrity_flags', 'overall_confidence'],
  properties: {
    target_id: { type: 'string' },
    confirmed_count: { type: 'number' },
    demoted: { type: 'array', items: { type: 'string' } },
    integrity_flags: { type: 'array', items: { type: 'string' } },
    overall_confidence: { type: 'string', enum: ['High', 'Medium', 'Low'] },
  },
}

const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['ranking', 'summary', 'output_file_written'],
  properties: {
    ranking: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['target_id', 'community', 'review_gap_years', 'dipping_proximity', 'screening_priority'],
        properties: {
          target_id: { type: 'string' },
          community: { type: 'string' },
          review_gap_years: { type: 'string' },
          dipping_proximity: { type: 'string' },
          screening_priority: { type: 'string', enum: ['High', 'Medium', 'Low'] },
        },
      },
    },
    summary: { type: 'string' },
    output_file_written: { type: 'string' },
  },
}

const OUT = 'docs/statewide_program/results'

function triagePrompt(t) {
  return `${RULES}

TRIAGE one target for a California land-use screening. Target: ${t.rancho} (${t.county} County) -- modern communities: ${t.communities}. Registry land status: ${t.status}.

The 1907-1915 USDA cattle-tick dipping program (arsenical dipping) covered these counties. HEAVILY infested: ${QUARANTINE_HEAVY}. Lesser: ${QUARANTINE_LESSER}.

Answer quickly (this is a 10-minute triage, not the deep dive):
1. Is ${t.county} in the quarantine county list? (deterministic)
2. Is the land now RESIDENTIAL (master-planned community / city), or federal/agricultural/unbuilt? Federal/farmland/unbuilt targets should triage OUT (deep_dive_recommended=false) -- the land is not under homes.
3. Rough earliest imagery year available for this land (USGS topoView earliest topo; county aerial services). One quick check.
4. Rough guess at when a modern environmental review would have started reviewing aerials (usually 1950s).
5. priority_score 0-10 (heavy county +3, residential +4, water-rich ranching terrain +2, active large development +1).
6. deep_dive_recommended = true only if residential AND in a quarantine county.

Return the TRIAGE_SCHEMA object. Keep notes to 2-3 sentences.`
}

function deepDivePrompt(t) {
  return `${RULES}

DEEP DIVE -- run the documentary half of the Ladera Ranch methodology for this target.
Target: ${t.rancho}, ${t.county} County. Communities: ${t.communities}.

Do these, in order, using web research (USGS topoView, county GIS, UCSB FrameFinder, CEQAnet at ceqanet.lci.ca.gov, DTSC EnviroStor, State Water Board GeoTracker, California Digital Newspaper Collection cdnc.ucr.edu, Chronicling America, Google Books):

A. EARLIEST IMAGERY/MAP of this land. Give the oldest topo (year) and oldest aerial (year) that cover it, with source.
B. ENVIRONMENTAL-REVIEW WINDOW -- THE HEADLINE. Find the CEQA/EIR/Phase I environmental review for the community's development. How far back did its HISTORICAL AERIAL REVIEW reach (what is the earliest photo year it reviewed)? Search the documents for "dip", "vat", "cattle dip", "arsenic". Compute review_gap_years = (review earliest photo year) minus (~1912, dipping's end) -- i.e. how many years of the dipping era sit BELOW the review's floor.
C. DIPPING RECORDS tied to THIS ranch by name (CDNC/Chronicling America/State Vet reports). Almost certainly none by name -- report that plainly if so.
D. SAMPLING-FRAME PLAUSIBILITY -- one paragraph: does the terrain (water, drainages, ranching intensity) make an on-ranch working facility plausible? Do NOT assert a vat exists.
E. Build 4-10 FINDINGS in the schema, each graded with mandatory counter-evidence.
F. Record DEAD ENDS (exact queries that returned nothing).

Then WRITE your full record as JSON to ${OUT}/${t.id}_deepdive.json using your file tools (create the folder if needed), and set output_file_written to that path.

Return the DEEPDIVE_SCHEMA object. The review_gap_years figure is the most important single output.`
}

function verifyPrompt(dd, t) {
  return `${RULES}

ADVERSARIAL VERIFICATION. A prior agent produced this deep-dive record for ${t.rancho} (${t.county}):

${JSON.stringify(dd).slice(0, 6000)}

Your job is to REFUTE it. For each finding: is the citation real and does it support the claim? Is any contamination implied (a rule violation)? Is any "not studied" overstated into "did not happen"? Is the review_gap_years figure defensible? Default to demoting anything you cannot confirm. List integrity_flags for any rule violation. Return the VERDICT_SCHEMA object.`
}

// ---------------- run ----------------
phase('Triage')
log(`Triaging ${TARGETS.length} targets...`)
// Keep nulls so index stays aligned with TARGETS (parallel preserves order).
const triaged = await parallel(TARGETS.map(t => () =>
  agent(triagePrompt(t), { label: `triage:${t.id}`, phase: 'Triage', schema: TRIAGE_SCHEMA, effort: 'low' })
))

// Match by INDEX, not by the agent-returned target_id -- agents echo their own id strings
// ("rancho_trabuco"), which don't match the registry ids ("T01-TRABUCO"). An earlier run lost
// every deep-dive to that mismatch and synthesised on empty input.
const go = TARGETS.filter((t, i) => triaged[i] && triaged[i].deep_dive_recommended)
log(`${go.length} of ${TARGETS.length} targets passed triage for deep dive.`)

// Deep dive -> verify, pipelined per target (no barrier)
const results = await pipeline(
  go,
  (t) => agent(deepDivePrompt(t), { label: `deep:${t.id}`, phase: 'Deep dive', schema: DEEPDIVE_SCHEMA, agentType: 'general-purpose', effort: 'medium' }),
  (dd, t) => dd
    ? agent(verifyPrompt(dd, t), { label: `verify:${t.id}`, phase: 'Verify', schema: VERDICT_SCHEMA, effort: 'medium' }).then(v => ({ target: t.id, deepdive: dd, verdict: v }))
    : { target: t.id, deepdive: null, verdict: null },
)

// Synthesis
phase('Synthesize')
const clean = results.filter(Boolean)
const synthPrompt = `${RULES}

SYNTHESIZE a statewide screening ranking from these per-target results:

${JSON.stringify(clean.map(r => ({ id: r.target, gap: r.deepdive && r.deepdive.review_gap_years, dipping: r.deepdive && r.deepdive.dipping_records_summary, conf: r.verdict && r.verdict.overall_confidence }))).slice(0, 8000)}

Produce a ranking of communities by SCREENING PRIORITY = how wide the environmental-review gap is AND how plausible nearby dipping is. This is a ranking of WHERE AN UNANSWERED QUESTION IS WIDEST -- explicitly NOT a contamination ranking, and every row must be readable as such. Write a markdown table + 2-paragraph summary to docs/statewide_program/STATEWIDE_RANKING.md using your file tools, opening with the disclaimer that no community is asserted to be contaminated and the only resolver is a soil test. Return the SYNTH_SCHEMA object.`
const synthesis = await agent(synthPrompt, { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA, agentType: 'general-purpose', effort: 'high' })

log('Statewide sweep complete.')
return { triaged: triaged.filter(Boolean), deep_dived: clean.length, synthesis }
