// MongoDB initialization script
// This script will be executed when the MongoDB container starts for the first time

// Connect to MongoDB with admin credentials
db = db.getSiblingDB('admin');

// Check if the rpger database already exists
let dbs = db.adminCommand('listDatabases').databases;
let rpgerExists = dbs.some(database => database.name === 'rpger');

if (!rpgerExists) {
    print('Creating rpger database and collections...');
    
    // Switch to rpger database
    db = db.getSiblingDB('rpger');
    
    // Create collections with validation schemas
    db.createCollection('users', {
        validator: {
            $jsonSchema: {
                bsonType: 'object',
                required: ['username', 'email', 'password', 'role'],
                properties: {
                    username: {
                        bsonType: 'string',
                        description: 'Username must be a string and is required'
                    },
                    email: {
                        bsonType: 'string',
                        description: 'Email must be a string and is required'
                    },
                    password: {
                        bsonType: 'string',
                        description: 'Password must be a string and is required'
                    },
                    role: {
                        enum: ['user', 'admin'],
                        description: 'Role must be either user or admin'
                    },
                    preferences: {
                        bsonType: 'object',
                        properties: {
                            theme: {
                                enum: ['light', 'dark', 'system'],
                                description: 'Theme preference'
                            },
                            fontSize: {
                                enum: ['small', 'medium', 'large'],
                                description: 'Font size preference'
                            },
                            dashboardLayout: {
                                bsonType: 'object',
                                description: 'Dashboard layout configuration'
                            },
                            notifications: {
                                bsonType: 'bool',
                                description: 'Notification preferences'
                            }
                        }
                    },
                    lastLogin: {
                        bsonType: 'date',
                        description: 'Last login timestamp'
                    }
                }
            }
        }
    });
    
    db.createCollection('dashboards', {
        validator: {
            $jsonSchema: {
                bsonType: 'object',
                required: ['userId', 'name', 'layouts'],
                properties: {
                    userId: {
                        bsonType: 'objectId',
                        description: 'User ID must be an ObjectId and is required'
                    },
                    name: {
                        bsonType: 'string',
                        description: 'Dashboard name must be a string and is required'
                    },
                    description: {
                        bsonType: 'string',
                        description: 'Dashboard description'
                    },
                    layouts: {
                        bsonType: 'object',
                        description: 'Dashboard layout configuration'
                    },
                    isDefault: {
                        bsonType: 'bool',
                        description: 'Whether this is the default dashboard'
                    }
                }
            }
        }
    });
    
    db.createCollection('widgets', {
        validator: {
            $jsonSchema: {
                bsonType: 'object',
                required: ['userId', 'widgetId', 'name', 'type'],
                properties: {
                    userId: {
                        bsonType: 'objectId',
                        description: 'User ID must be an ObjectId and is required'
                    },
                    widgetId: {
                        bsonType: 'string',
                        description: 'Widget ID must be a string and is required'
                    },
                    name: {
                        bsonType: 'string',
                        description: 'Widget name must be a string and is required'
                    },
                    type: {
                        bsonType: 'string',
                        description: 'Widget type must be a string and is required'
                    },
                    config: {
                        bsonType: 'object',
                        description: 'Widget configuration'
                    },
                    layout: {
                        bsonType: 'object',
                        description: 'Widget layout configuration'
                    },
                    active: {
                        bsonType: 'bool',
                        description: 'Whether the widget is active'
                    }
                }
            }
        }
    });
    
    db.createCollection('campaigns', {
        validator: {
            $jsonSchema: {
                bsonType: 'object',
                required: ['userId', 'name', 'concept', 'setting'],
                properties: {
                    userId: {
                        bsonType: 'objectId',
                        description: 'User ID must be an ObjectId and is required'
                    },
                    name: {
                        bsonType: 'string',
                        description: 'Campaign name must be a string and is required'
                    },
                    concept: {
                        bsonType: 'string',
                        description: 'Campaign concept must be a string and is required'
                    },
                    setting: {
                        bsonType: 'string',
                        description: 'Campaign setting must be a string and is required'
                    },
                    characters: {
                        bsonType: 'array',
                        description: 'Array of character ObjectIds'
                    },
                    locations: {
                        bsonType: 'array',
                        description: 'Array of location objects'
                    },
                    npcs: {
                        bsonType: 'array',
                        description: 'Array of NPC objects'
                    }
                }
            }
        }
    });
    
    db.createCollection('characters', {
        validator: {
            $jsonSchema: {
                bsonType: 'object',
                required: ['userId', 'name'],
                properties: {
                    userId: {
                        bsonType: 'objectId',
                        description: 'User ID must be an ObjectId and is required'
                    },
                    name: {
                        bsonType: 'string',
                        description: 'Character name must be a string and is required'
                    }
                    // Additional character properties would be defined here
                }
            }
        }
    });
    
    db.createCollection('notes', {
        validator: {
            $jsonSchema: {
                bsonType: 'object',
                required: ['userId', 'title', 'content'],
                properties: {
                    userId: {
                        bsonType: 'objectId',
                        description: 'User ID must be an ObjectId and is required'
                    },
                    title: {
                        bsonType: 'string',
                        description: 'Note title must be a string and is required'
                    },
                    content: {
                        bsonType: 'string',
                        description: 'Note content must be a string and is required'
                    },
                    category: {
                        bsonType: 'string',
                        description: 'Note category'
                    },
                    tags: {
                        bsonType: 'array',
                        description: 'Array of tag strings'
                    },
                    pinned: {
                        bsonType: 'bool',
                        description: 'Whether the note is pinned'
                    }
                }
            }
        }
    });
    
    // Create indexes
    db.users.createIndex({ username: 1 }, { unique: true });
    db.users.createIndex({ email: 1 }, { unique: true });
    db.dashboards.createIndex({ userId: 1, name: 1 }, { unique: true });
    db.widgets.createIndex({ userId: 1, widgetId: 1 }, { unique: true });
    db.campaigns.createIndex({ userId: 1, name: 1 }, { unique: true });
    db.characters.createIndex({ userId: 1, name: 1 });
    db.notes.createIndex({ userId: 1 });
    db.notes.createIndex({ userId: 1, tags: 1 });
    
    print('Database initialization completed successfully');
} else {
    print('RPGer database already exists, skipping initialization');
}

// Create application user if it doesn't exist
db = db.getSiblingDB('admin');
let appUser = db.getUser('rpgerapp');

if (!appUser) {
    print('Creating application user...');
    
    db.createUser({
        user: 'rpgerapp',
        pwd: 'rpgerapppassword',
        roles: [
            { role: 'readWrite', db: 'rpger' }
        ]
    });
    
    print('Application user created successfully');
} else {
    print('Application user already exists');
}

print('MongoDB initialization script completed');
