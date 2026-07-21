export const meta = {
  name: 'statewide-ranch-image-hunt',
  description: 'Deep archival image/photo/map/artifact hunt for every California target ranch, using the metadata tactics that worked for the O\'Neill ranch. Rights-flagged, provenance-graded; downloads only rights-clean items.',
  whenToUse: 'The image-acquisition layer of the statewide program: exhaustive photo/map/artifact search per ranch across Calisphere, OAC, USC, UCLA, Huntington, Bancroft, county libraries, historical societies, David Rumsey.',
  phases: [
    { title: 'Image hunt', detail: 'one deep archival agent per ranch' },
    { title: 'Index', detail: 'merge into a master image index' },
  ],
}

// Each target carries its grantee/owner FAMILY NAMES -- the single most powerful metadata lever
// for archival search (collections are catalogued by owner, not by modern community).
const RANCHES = (args && args.ranches) || [
  { id: 'T01-TRABUCO',       rancho: 'Rancho Trabuco',                        county: 'Orange',         families: 'Arguello, Forster, O\'Neill, Flood',        region: 'Trabuco Canyon / Coto de Caza / south Orange County' },
  { id: 'T02-IRVINE',        rancho: 'Irvine Ranch',                          county: 'Orange',         families: 'Irvine, Flint, Bixby, Sepulveda, Yorba, Grijalva', region: 'Irvine / Tustin / Newport, Orange County' },
  { id: 'T03-SIMI',          rancho: 'Rancho Simi',                           county: 'Ventura',        families: 'Pico, de la Guerra, Simi, Strathearn',      region: 'Simi Valley, Ventura County' },
  { id: 'T04-PENASQUITOS',   rancho: 'Rancho Santa Maria de Los Penasquitos', county: 'San Diego',      families: 'Ruiz, Alvarado, Johnson',                   region: 'Rancho Penasquitos / Mira Mesa, San Diego' },
  { id: 'T05-SANBERNARDO',   rancho: 'Rancho San Bernardo',                   county: 'San Diego',      families: 'Snook, Osuna, Sikes',                       region: 'Rancho Bernardo / Escondido, San Diego' },
  { id: 'T06-SANDIEGUITO',   rancho: 'Rancho San Dieguito',                   county: 'San Diego',      families: 'Osuna, Ruiz',                               region: 'Rancho Santa Fe / Del Mar, San Diego' },
  { id: 'T07-SESPE',         rancho: 'Rancho Sespe',                          county: 'Ventura',        families: 'Carrillo, More',                            region: 'Fillmore / Sespe, Ventura County' },
  { id: 'T08-NEWHALL',       rancho: 'Rancho San Francisco / Newhall Ranch',  county: 'Los Angeles',    families: 'del Valle, Newhall',                        region: 'Santa Clarita / Newhall, Los Angeles County' },
  { id: 'T09-LOSCERRITOS',   rancho: 'Rancho Los Cerritos',                   county: 'Los Angeles',    families: 'Nieto, Temple, Flint, Bixby',               region: 'Long Beach / Lakewood, Los Angeles County' },
  { id: 'T10-LOSALAMITOS',   rancho: 'Rancho Los Alamitos',                   county: 'Los Angeles',    families: 'Nieto, Stearns, Bixby',                     region: 'Long Beach / Los Alamitos, Los Angeles County' },
  { id: 'T11-CUCAMONGA',     rancho: 'Rancho Cucamonga',                      county: 'San Bernardino', families: 'Tapia, Rains, Chaffey',                     region: 'Rancho Cucamonga, San Bernardino County' },
  { id: 'T12-JURUPA',        rancho: 'Rancho Jurupa',                         county: 'Riverside',      families: 'Bandini, Rubidoux, Stearns',                region: 'Riverside / Jurupa Valley' },
  { id: 'T13-SANTAMARGARITA',rancho: 'Rancho Santa Margarita y Las Flores',   county: 'San Diego',      families: 'Pico, Forster, O\'Neill, Flood',            region: 'Camp Pendleton / San Onofre, San Diego (NOT the OC city of the same name)' },
  { id: 'T14-TEJON',         rancho: 'Tejon Ranch',                           county: 'Kern',           families: 'Beale, Fort Tejon',                         region: 'Tejon / Lebec, Kern County' },
  { id: 'T15-MILLERLUX',     rancho: 'Miller & Lux',                          county: 'Fresno',         families: 'Henry Miller, Charles Lux',                 region: 'Los Banos / San Joaquin Valley' },
]

const RULES = `
STANDING RULES:
1. NEVER fabricate an image, title, call number, identifier, URL, date, or rights statement. Verify a URL resolves before calling it usable. "Not found" is a valid, useful result.
2. Record rights status VERBATIM as the repository states it. Only DOWNLOAD items that are clearly public domain or openly licensed. For restricted/unclear items, catalogue them but do NOT download.
3. For EVERY item, state WHICH LAND/COUNTY it depicts. Many ranchos share names or families across counties -- e.g. the San Diego "Santa Margarita y Las Flores" (Camp Pendleton) is DIFFERENT land from the Orange County city "Rancho Santa Margarita". Do not conflate. Flag any ambiguity.
4. No individual private data; historical land-use and ranch-operation imagery only.
5. This is image acquisition for a hypothesis-neutral land-use archive. Make NO claim about contamination.`

const ITEM = {
  type: 'object', additionalProperties: false,
  required: ['title', 'repository', 'date', 'rights', 'depicts', 'downloadable'],
  properties: {
    title: { type: 'string' },
    repository: { type: 'string' },
    identifier: { type: 'string' },
    date: { type: 'string' },
    url: { type: 'string' },
    rights: { type: 'string' },
    depicts: { type: 'string' },
    category: { type: 'string', enum: ['photo', 'map', 'artifact', 'document', 'other'] },
    downloadable: { type: 'boolean' },
    downloaded_path: { type: 'string' },
  },
}

const HUNT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['target_id', 'items_found', 'items_downloaded', 'items', 'physical_only_collections', 'dead_ends'],
  properties: {
    target_id: { type: 'string' },
    items_found: { type: 'number' },
    items_downloaded: { type: 'number' },
    items: { type: 'array', items: ITEM },
    physical_only_collections: { type: 'array', items: { type: 'string' } },
    dead_ends: { type: 'array', items: { type: 'string' } },
    output_file_written: { type: 'string' },
  },
}

const INDEX_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['total_items', 'total_downloaded', 'summary', 'output_file_written'],
  properties: {
    total_items: { type: 'number' },
    total_downloaded: { type: 'number' },
    by_target: { type: 'array', items: { type: 'object', additionalProperties: true } },
    summary: { type: 'string' },
    output_file_written: { type: 'string' },
  },
}

function huntPrompt(r) {
  return `${RULES}

DEEP ARCHIVAL IMAGE / PHOTO / MAP / ARTIFACT HUNT for one California ranch.
Ranch: ${r.rancho} (${r.county} County). Grantee/owner families: ${r.families}. Region: ${r.region}.

Find EVERYTHING visual related to this ranch and its cattle operation, using the metadata tactics that work for archival collections (collections are catalogued by OWNER FAMILY and PHOTOGRAPHER, not by modern place name):

SEARCH THESE, systematically:
- Calisphere (calisphere.org) and the Online Archive of California (oac.cdlib.org) finding aids -- search the rancho name AND each family name.
- USC Digital Library (digitallibrary.usc.edu), UCLA Library Special Collections, Bancroft Library (UC Berkeley), Huntington Library (photos AND the "Maps" collection).
- The county's public library digital collection and local historical society (each region has one -- find it).
- Library of Congress (photos + Sanborn maps + HABS/HAER), David Rumsey Map Collection (davidrumsey.com), BLM GLO Records and USGS topoView for maps/plats.
- Try metadata levers: family surnames, photographer/collection IDs, negative numbers, "rancho" + region, adjacent-item browsing within a hit collection.

FOR EACH ITEM found, record: title (verbatim), repository, identifier/call number, date (and whether stated or estimated), permanent URL, rights status (VERBATIM), what land/county it depicts, category (photo/map/artifact/document), downloadable y/n.

DOWNLOAD only clearly public-domain / openly-licensed items, to evidence/images/${r.id}/ (create the folder). Verify each download is a real image/PDF with the file command, not an HTML error page. Set downloaded_path.

Catalogue physical-only collections (historical societies, title-company archives) with contact info in physical_only_collections. Record dead_ends (exact queries that returned nothing).

Then WRITE your full inventory as JSON to research/statewide/images/${r.id}_images.json (create the folder) and set output_file_written.

Return the HUNT_SCHEMA object. Be exhaustive -- run many searches, not three.`
}

phase('Image hunt')
log(`Hunting images across ${RANCHES.length} ranches...`)
const hunts = await parallel(RANCHES.map(r => () =>
  agent(huntPrompt(r), { label: `img:${r.id}`, phase: 'Image hunt', schema: HUNT_SCHEMA, agentType: 'general-purpose', effort: 'medium' })
))
const ok = hunts.filter(Boolean)
const found = ok.reduce((s, h) => s + (h.items_found || 0), 0)
const dl = ok.reduce((s, h) => s + (h.items_downloaded || 0), 0)
log(`Found ${found} items across ${ok.length} ranches; downloaded ${dl}.`)

phase('Index')
const indexPrompt = `${RULES}

Build a MASTER IMAGE INDEX from these per-ranch inventories:

${JSON.stringify(ok.map(h => ({ id: h.target_id, found: h.items_found, downloaded: h.items_downloaded, physical: h.physical_only_collections }))).slice(0, 8000)}

Write a markdown index to research/statewide/IMAGE_INDEX.md using your file tools: one section per ranch with a table (title, repository, date, rights, depicts, downloadable), a list of the physical-only collections worth an in-person visit or records request (with contacts), and a 2-paragraph summary of where the richest untapped visual archives are. Reiterate that rights-restricted items were catalogued but not downloaded, and that images depicting different land/counties are flagged as such. Return the INDEX_SCHEMA object.`
const index = await agent(indexPrompt, { label: 'index', phase: 'Index', schema: INDEX_SCHEMA, agentType: 'general-purpose', effort: 'high' })

log('Statewide image hunt complete.')
return { ranches: ok.length, items_found: found, items_downloaded: dl, index }
