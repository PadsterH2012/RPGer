/**
 * Mock API service for testing the MongoDB Viewer widget
 */

// Sample monster data
const monsters = [
  {
    _id: '1',
    name: 'Dragon, Red',
    type: 'Dragon',
    description: 'A massive fire-breathing dragon with crimson scales.',
    stats: {
      hp: 200,
      ac: 19,
      strength: 27,
      dexterity: 10,
      constitution: 25,
      intelligence: 16,
      wisdom: 13,
      charisma: 21
    },
    abilities: ['Fire Breath', 'Claw Attack', 'Tail Swipe'],
    habitat: 'Mountains, Volcanoes',
    ecology: 'Apex predator, territorial, hoards treasure'
  },
  {
    _id: '2',
    name: 'Goblin',
    type: 'Humanoid',
    description: 'A small, green-skinned creature with a mischievous grin.',
    stats: {
      hp: 7,
      ac: 15,
      strength: 8,
      dexterity: 14,
      constitution: 10,
      intelligence: 10,
      wisdom: 8,
      charisma: 8
    },
    abilities: ['Nimble Escape', 'Scimitar Attack'],
    habitat: 'Forests, Caves',
    ecology: 'Lives in tribes, scavenges and raids'
  },
  {
    _id: '3',
    name: 'Troll',
    type: 'Giant',
    description: 'A large, regenerating monster with green skin and long arms.',
    stats: {
      hp: 84,
      ac: 15,
      strength: 18,
      dexterity: 13,
      constitution: 20,
      intelligence: 7,
      wisdom: 9,
      charisma: 7
    },
    abilities: ['Regeneration', 'Multiattack', 'Keen Smell'],
    habitat: 'Swamps, Mountains',
    ecology: 'Solitary predator, territorial'
  },
  {
    _id: '4',
    name: 'Skeleton',
    type: 'Undead',
    description: 'An animated skeleton wielding rusty weapons.',
    stats: {
      hp: 13,
      ac: 13,
      strength: 10,
      dexterity: 14,
      constitution: 15,
      intelligence: 6,
      wisdom: 8,
      charisma: 5
    },
    abilities: ['Shortsword Attack', 'Shortbow Attack'],
    habitat: 'Dungeons, Crypts',
    ecology: 'Created through necromancy, mindlessly follows orders'
  },
  {
    _id: '5',
    name: 'Beholder',
    type: 'Aberration',
    description: 'A floating orb with a large central eye and many eyestalks.',
    stats: {
      hp: 180,
      ac: 18,
      strength: 10,
      dexterity: 14,
      constitution: 18,
      intelligence: 17,
      wisdom: 15,
      charisma: 17
    },
    abilities: ['Antimagic Cone', 'Eye Rays', 'Telekinetic Ray'],
    habitat: 'Underground lairs',
    ecology: 'Paranoid and territorial, creates complex lairs'
  }
];

// Sample spells data
const spells = [
  {
    _id: '1',
    name: 'Fireball',
    level: 3,
    school: 'Evocation',
    castingTime: '1 action',
    range: '150 feet',
    components: 'V, S, M (a tiny ball of bat guano and sulfur)',
    duration: 'Instantaneous',
    description: 'A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame.'
  },
  {
    _id: '2',
    name: 'Magic Missile',
    level: 1,
    school: 'Evocation',
    castingTime: '1 action',
    range: '120 feet',
    components: 'V, S',
    duration: 'Instantaneous',
    description: 'You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range.'
  }
];

// Sample items data
const itemsData = [
  {
    _id: '1',
    name: 'Sword of Sharpness',
    type: 'Weapon',
    rarity: 'Very Rare',
    attunement: true,
    description: 'A magic sword that can slice through almost anything.'
  },
  {
    _id: '2',
    name: 'Potion of Healing',
    type: 'Potion',
    rarity: 'Common',
    attunement: false,
    description: 'A red liquid that restores 2d4+2 hit points when consumed.'
  }
];

// Sample collections
const collections = ['monsters', 'spells', 'items', 'npcs', 'characters'];

// Mock API functions
export const mockApi = {
  // Get all collections
  getCollections: () => {
    return Promise.resolve({
      data: {
        collections: collections,
        count: collections.length
      }
    });
  },

  // Get items from a collection
  getCollectionItems: (collection: string, page = 1, limit = 10) => {
    let items: any[] = [];
    let total = 0;

    switch (collection) {
      case 'monsters':
        items = monsters;
        total = monsters.length;
        break;
      case 'spells':
        items = spells;
        total = spells.length;
        break;
      case 'items':
        items = itemsData;
        total = itemsData.length;
        break;
      case 'npcs':
        // Mock NPCs
        items = [
          { _id: '1', name: 'Innkeeper', type: 'NPC', description: 'A friendly innkeeper' },
          { _id: '2', name: 'Blacksmith', type: 'NPC', description: 'A skilled blacksmith' }
        ];
        total = items.length;
        break;
      case 'characters':
        // Mock characters
        items = [
          { _id: '1', name: 'Aragorn', class: 'Ranger', level: 10 },
          { _id: '2', name: 'Gandalf', class: 'Wizard', level: 20 }
        ];
        total = items.length;
        break;
      default:
        items = [];
        total = 0;
    }

    // Calculate pagination
    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedItems = items.slice(start, end);

    return Promise.resolve({
      data: {
        items: paginatedItems,
        total: total,
        page: page,
        limit: limit,
        pages: Math.ceil(total / limit)
      }
    });
  },

  // Get a single item from a collection
  getCollectionItem: (collection: string, itemId: string) => {
    let item = null;

    switch (collection) {
      case 'monsters':
        item = monsters.find(m => m._id === itemId);
        break;
      case 'spells':
        item = spells.find(s => s._id === itemId);
        break;
      case 'items':
        item = itemsData.find(i => i._id === itemId);
        break;
      case 'npcs':
        item = [
          { _id: '1', name: 'Innkeeper', type: 'NPC', description: 'A friendly innkeeper' },
          { _id: '2', name: 'Blacksmith', type: 'NPC', description: 'A skilled blacksmith' }
        ].find(n => n._id === itemId);
        break;
      case 'characters':
        item = [
          { _id: '1', name: 'Aragorn', class: 'Ranger', level: 10 },
          { _id: '2', name: 'Gandalf', class: 'Wizard', level: 20 }
        ].find(c => c._id === itemId);
        break;
    }

    if (item) {
      return Promise.resolve({ data: item });
    } else {
      return Promise.reject({
        response: {
          status: 404,
          data: { error: `Item not found in ${collection}` }
        }
      });
    }
  }
};

export default mockApi;
