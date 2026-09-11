// Configuration for Pirate Scrollytelling Engine

const CONFIG = {
  apiEndpoint: '/api/frames-info',
  framesDir: '/static/frames/',
  defaultFrames: 240,
  framePrefix: 'frame_',
  frameExt: '.jpg',
  zeroPadding: 4,
  
  // Smooth scroll physics
  scrollTrackHeight: 450, // in vh units (450vh allows luxurious pacing)
  lerpFactor: 0.12,        // Frame interpolation damping (0.08 to 0.15 is ideal)
  lenisDuration: 1.2,      // Smooth scroll inertia duration in seconds
  
  // Acts and milestones (progress 0.0 to 1.0)
  chapters: [
    {
      id: 'prologue',
      range: [0.0, 0.16],
      title: 'Dead Men Tell Tales',
      subtitle: 'The Cursed Voyage of the Crimson Galleon'
    },
    {
      id: 'act1',
      range: [0.20, 0.40],
      badge: 'Act I • Uncharted Meridian',
      title: 'The Cursed Needle',
      text: 'The brass needle spins true only when the soul desires that which cannot be owned. As our galleon cuts through the black brine, ancient glyphs carved into the helm flare with eldritch fire.'
    },
    {
      id: 'act2',
      range: [0.45, 0.65],
      badge: 'Act II • Siren\'s Maelstrom',
      title: 'Wrath of the Tempest',
      text: 'Lightning tears open the canvas sky! Giant tentacles coil around the ship\'s keel as ghost galleons emerge through the emerald fog. Hold fast to the rigging!'
    },
    {
      id: 'act3',
      range: [0.70, 0.88],
      badge: 'Act III • Isla de la Muerte',
      title: 'The Sunken Vault',
      text: 'Eight hundred and eighty-two identical pieces of Aztec gold, placed in a stone chest, paid as blood money to Cortês himself. He who takes but a single coin shall be cursed for eternity!'
    },
    {
      id: 'epilogue',
      range: [0.91, 1.0],
      title: 'The Legend Lives On',
      text: 'The voyage is complete, but the sea calls forever. Replay the voyage anytime or chart your own course.'
    }
  ]
};

window.PIRATE_CONFIG = CONFIG;
