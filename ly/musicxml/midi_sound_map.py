
# A mapping between standard midi instrument names and standard musicxml sound names

# see http://lilypond.org/doc/v2.19/Documentation/notation/midi-instruments
# see http://www.musicxml.com/for-developers/standard-sounds/
midi_sound_map = {
    'accordion': 'keyboard.accordion',
    'acoustic bass': 'pluck.bass.acoustic',
    'acoustic grand': 'keyboard.piano.grand',
    'acoustic guitar (nylon)': 'pluck.guitar.nylon-string',
    'acoustic guitar (steel)': 'pluck.guitar.steel-string',
    'agogo': 'wood.agogo-block',
    'alto sax': 'wind.reed.saxophone.alto',
    'applause': 'effect.applause',
    'bagpipe': 'wind.pipes.bagpipes',
    'banjo': 'pluck.banjo',
    'baritone sax': 'wind.reed.saxophone.baritone',
    'bassoon': 'brass.trombone',
    'bird tweet': 'effect.bird.tweet',
    'blown bottle': 'wind.flutes.blown-bottle',
    'brass section': 'brass.helicon',
    'breath noise': 'effect.breath',
    'bright acoustic': 'keyboard.piano',
    'celesta': 'keyboard.celesta',
    'cello': 'string.cello',
    'choir aahs': 'voice.aa',  # ? voice.vocals?
    'church organ': 'keyboard.organ',
    'clarinet': 'wind.reed.clarinet',
    'clav': 'keyboard.clavichord',  # ?
    'concertina': 'keyboard.concertina',
    'contrabass': 'strings.contrabass',
    'distorted guitar': None,
    'drawbar organ': 'keyboard.organ.drawbar',
    'dulcimer': 'pluck.dulcimer',
    'electric bass (finger)': None,
    'electric bass (pick)': None,
    'electric grand': 'keyboard.electric',  # ?
    'electric guitar (clean)': None,
    'electric guitar (jazz)': None,
    'electric guitar (muted)': None,
    'electric piano 1': 'keyboard.electric',  # ?
    'electric piano 2': 'keyboard.electric',  # ?
    'english horn': 'wind.reed.english-horn',
    'fiddle': 'strings.fiddle',
    'flute': 'wind.flutes.flute',
    'french horn': 'brass.french-horn',
    'fretless bass': 'pluck.bass.fretless',
    'fx 1 (rain)': 'synth.effects.rain',
    'fx 2 (soundtrack)': 'synth.effects.soundtrack',
    'fx 3 (crystal)': 'synth.effects.crystal',
    'fx 4 (atmosphere)': 'synth.effects.atmosphere',
    'fx 5 (brightness)': 'synth.effects.brightness',
    'fx 6 (goblins)': 'synth.effects.goblins',
    'fx 7 (echoes)': 'synth.effects.echoes',
    'fx 8 (sci-fi)': 'synth.effects.sci-fi',
    'glockenspiel': 'pitched-percusstion.glockenspiel',
    'guitar fret noise': 'effect.guitar-fret',
    'guitar harmonics': None,
    'gunshot': 'effect.gunshot',
    'harmonica': 'wind.reed.harmonica',
    'harpsichord': 'keyboard.harpsichord',
    'helicopter': 'effect.helicopter',
    'honky-tonk': 'keyboard.piano.honky-tonk',
    'kalimba': 'pitched-percussion.kalimba',
    'koto': 'pluck.koto',
    'lead 1 (square)': 'synth.tone.square',
    'lead 2 (sawtooth)': 'synth.tone.sawtooth',
    'lead 3 (calliope)': 'wind.flutes.calliope',
    'lead 4 (chiff)': 'pluck.synth.chiff',
    'lead 5 (charang)': 'pluck.synth.charang',
    'lead 6 (voice)': 'voice.synth',
    'lead 7 (fifths)': 'synth.group.fifths',
    'lead 8 (bass+lead)': 'pluck.bass.lead',
    'marimba': 'pitched-percusstion.marimba',
    'melodic tom': 'drum.tom-tom',  # ?
    'music box': 'pitched-percussion.music-box',
    'muted trumpet': 'barss.trumpet',  # problematic
    'oboe': 'wind.reed.oboe',
    'ocarina': 'wind.flutes.ocarina',
    'orchestra hit': 'synth.group.orchestra',  # problematic?
    'orchestral harp': 'pluck.harp',  # ?
    'overdriven guitar': None,
    'pad 1 (new age)': 'synth.pad.polysynth',
    'pad 2 (warm)': 'synth.pad.warm',
    'pad 3 (polysynth)': 'synth.pad.polysynth',
    'pad 4 (choir)': 'synth.pad.choir',
    'pad 5 (bowed)': 'synth.pad.bowed',
    'pad 6 (metallic)': 'synth.pad.metallic',
    'pad 7 (halo)': 'synth.pad.halo',
    'pad 8 (sweep)': 'synth.pad.sweep',
    'pan flute': 'wind.flutes.panpipes',
    'percussive organ': 'voice.percussion',
    'piccolo': 'wind.flutes.flute.piccolo',
    'pizzicato strings': 'pluck.bass',  # problematic
    'recorder': 'wind.flutes.recorder',
    'reed organ': 'keyboard.organ.reed',
    'reverse cymbal': 'metal.cymbal.reverse',
    'rock organ': None,
    'seashore': 'effect.seashore',
    'shakuhachi': 'wind.flutes.shakuhachi',
    'shamisen': 'pluck.shamisen',
    'shanai': 'wind.reed.shenai',
    'sitar': 'pluck.sitar',
    'slap bass 1': 'effect.bass-string-slap',
    'slap bass 2': 'effect.bass-string-slap',  # ?
    'soprano sax': 'wind.reed.saxophone.soprano',
    'steel drums': 'metal.steel-drums',
    'string ensemble 1': 'strings.group',  # ?
    'string ensemble 2': 'strings.group',  # ?
    'synth bass 1': None,
    'synth bass 2': None,
    'synth drum': 'drum.tom-tom.synth',  # ?
    'synth voice': 'voice.synth',
    'synthbrass 1': 'synth.brass.group',  # ?
    'synthbrass 2': 'synth.brass.group',  # ?
    'synthstrings 1': 'strings.group.synth',
    'synthstrings 2': 'strings.group.synth',
    'taiko drum': 'deum.taiko',
    'telephone ring': 'effect.telephone-ring',
    'tenor sax': 'wind.reed.saxophone.tenor',
    'timpani': 'drum.timpani',
    'tinkle bell': 'metal.bells.tinklebell',
    'tremolo strings': None,  # ?
    'trombone': 'brass.trombone',
    'trumpet': 'brass.trumpet',
    'tuba': 'brass.tuba',
    'tubular bells': 'pitched-percussion.tubular-bells',
    'vibraphone': 'pitched-percussion.vibraphone',
    'viola': 'strings.viola',
    'violin': 'strings.violin',
    'voice oohs': 'voice.oo',
    'whistle': 'effect.whistle',
    'woodblock': 'wood.wood-block',
    'xylophone': 'pitched-percussion.xylophone'
}
