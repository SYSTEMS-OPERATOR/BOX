# BMG electronic metadata harvest

Completed 10 September 2026; public English-US UI sampled on 9–10 September. The dataset contains **1,329 exact displayed terms**, including **852 distinct nonempty search suggestions**, and **17 detailed tracks from 16 collections and 14 labels**. These are sample counts, not catalog frequencies. Eight playlist result pages, two album pages, versions and similarity UI provide additional structural evidence.

[BMG Sync+](https://www.bmgsyncplus.com/en-us/playlists) presented a login screen with no existing authenticated catalog access. The observed track taxonomy therefore comes from **BMG Production Music**. A current comparison between the two platforms is unresolved.

## Metadata system

The [Electronic landing page](https://bmgproductionmusic.com/en-us/home/genre/electronic/f1cd685e278574e2) links 15 curated playlists. Single links include `DOWNTEMPO + TRIP HOP`, `HARDCORE + INDUSTRIAL`, `SYNTHWAVE + CHILLWAVE`, and `AMBIENT + NEW AGE`. This demonstrates navigation under Electronic, not a formal subgenre ontology. Playlist headings can use title case while navigation renders capitals.

| Observed track field | Interpretation and limitation |
|---|---|
| GENRE | Multi-valued musical styles **and** uses such as Corporate, Sports, Technology |
| KEYWORDS | Mixed moods, energy, instruments, production, scenes, eras and sync contexts |
| INSTRUMENTATION | Instruments plus vocal types, sound effects and occasional style labels |
| KEY / BPM / TEMPO | Key and Tempo are optional; numeric BPM is present on all 17 sampled tracks |
| Identity / versions | Album, code, composer, optional artist, label, release date; alternate versions and STEMS indicators |

No dedicated Subgenre, Meter, Production, Arrangement or Structure field was observed on sampled detail panels. Mood concepts are evident in Keywords; a separate mood field is not demonstrated by these panels. Existing repository evidence of advertised search axes remains distinct from this direct track-level observation.

Genre + Keywords + Instrumentation + BPM + optional Key/Tempo form a repeatable **partial coordinate system**. They do not partition concepts cleanly. [Get The Eff Outta Here](https://bmgproductionmusic.com/en-us/track/get-the-eff-outta-here/cbee04b30c626006c627468843365b34/9aa66961bbfd63f9?searchTerm=Neurofunk+OR+Breakcore+OR+Darkstep+OR+Hardstep&typed=Neurofunk+OR+Breakcore+OR+Darkstep+OR+Hardstep) places `Breakcore` in Instrumentation; its Genre includes `Electronica` and `Glitch`. This is evidence of a term, not evidence of Breakcore's position in a genre hierarchy.

## Strong vocabulary families

Repeated cross-label handles include `Drum & Bass`, `Dnb`, `Drum And Bass`, `Drum N Bass`, `House`, `Uk Garage`, `Tech House`, `Driving`, `Propulsive`, `Energetic`, `Powerful`, `Minimal`, `Synth Bass`, `Drum Machine`, `Pads`, `Sampled Vocals` and `Instrumental`. Spelling variants are retained individually. Synonym groupings are analyst interpretations.

The Dubstep sample pairs `Wobble Bass`, `Sub Bass`, `Arpeggiators`, `Dj Scratches`, `Drops` and `Glitch Effects`, but both tracks share an album and label. That makes them medium-confidence candidates, not strong independent evidence of a catalog-wide controlled vocabulary. UK Garage tracks contribute vocal, drum-machine and synth-bass language. Co-occurrence relationships in the JSON report sample support, with source URLs; no causal or population inference follows.

Repeated generic tags and consistent field names suggest standardized tagging practices. Long heterogeneous keyword lists, case variants and `Aggressive`/`Agressive`, `Synthesizer`/`Synthetizer` weaken the case for a strictly controlled vocabulary. The UI does not establish whether each label is manually selected, automatically assigned or drawn from free text.

Consumer-style labels sit beside production needs: Corporate, Advertising, Workout, Investigation and Underscore describe placement contexts rather than musical ancestry. Version labels such as Light, Drones, Percussion, Pulses, Sfx and Synths describe usable alternatives. Similar Tracks provides related items without an exposed similarity score or algorithm.

## Uncertainties

- The exact compound `UK Garage / Bassline` was **not observed**. `Uk Garage`, `Ukg` and `Bassline` appear separately. Other compounds above are atomic navigation labels, which does not prove atomic search-tag behavior.
- Murmur displays **85 BPM / SLOW**; Black Sun Divide displays **88 BPM**. Do not double those numbers or replace them with the seed maps' DnB tempo preferences. Tempo spellings also vary; no shared numerical thresholds were established.
- Liquid Drum And Bass is an album title, not a demonstrated subgenre field. Neurofunk, Darkstep, Hardstep, Acid Techno and several other requested families lack direct track evidence in this sample. Suggestion-only evidence is weaker than track-field evidence.
- This bounded harvest reached local repetition in generic tags, not global vocabulary saturation. Older editorial, distributor and SYSOP/BACKUP evidence has not been reclassified as current BMG metadata.

## Suno v6 experiments

The JSON ranks 70 high-confidence, 136 medium-confidence and 15 experimental candidate strings. Confidence concerns BMG observation quality and interpretability; **every candidate's Suno control status is untested**. No shared internal ontology or model capability is claimed.

1. Test `Drum & Bass`, `Drum And Bass`, `Drum N Bass`, and `Dnb` as separate substitutions in one fixed prompt. Keep all other inputs and available generation settings identical; generate multiple independent examples per condition.
2. Add one descriptor at a time: `Driving`, `Propulsive`, `Sampled Vocals`, `Synth Bass`. Compare against the unchanged baseline using blinded ratings of groove, timbre, vocal presence and energy.
3. Test the same genre prompt with explicit 85 versus 170 BPM. Measure resulting tempo and perceived pulse separately; BMG's displayed BPM does not establish half-time equivalence.
4. Compare `Uk Garage` alone, plus `Bassline`, and plus `Synth Bass`. Treat any combined prompt as an analyst-built condition, not an observed compound BMG label.
5. Reserve `Breakcore` as instrumentation, `Robostep`, and suggestion-only phrases for exploratory trials. Predefine outcomes and report failures as well as successes before promoting a term's control status.

The dataset preserves exact strings and source fields; analytical buckets and relationships are labeled separately. See [validation_report.md](validation_report.md) for repository repairs and validation limits.
