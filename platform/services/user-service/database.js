const knex = require('knex');

const db = knex({
  client: 'pg',
  connection: {
    connectionString: process.env.DATABASE_URL || 'postgresql://iris_user:iris_password@postgres:5432/iris_platform',
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
  },
  pool: {
    min: 2,
    max: 10
  },
  migrations: {
    directory: './migrations',
    tableName: 'knex_migrations'
  },
  seeds: {
    directory: './seeds'
  }
});

// Create tables if they don't exist
const initializeTables = async () => {
  try {
    // Organizations table
    const orgExists = await db.schema.hasTable('organizations');
    if (!orgExists) {
      await db.schema.createTable('organizations', (table) => {
        table.uuid('id').primary();
        table.string('name', 255).notNullable();
        table.text('description').nullable();
        table.jsonb('settings').defaultTo('{}');
        table.boolean('is_active').defaultTo(true);
        table.timestamp('created_at').defaultTo(db.fn.now());
        table.timestamp('updated_at').defaultTo(db.fn.now());

        table.index(['name']);
        table.index(['is_active']);
      });
    }

    // Users table
    const usersExists = await db.schema.hasTable('users');
    if (!usersExists) {
      await db.schema.createTable('users', (table) => {
        table.uuid('id').primary();
        table.string('email', 255).notNullable().unique();
        table.string('password_hash', 255).notNullable();
        table.string('name', 255).notNullable();
        table.string('totp_secret', 255).nullable();
        table.jsonb('preferences').defaultTo('{}');
        table.boolean('is_active').defaultTo(true);
        table.boolean('email_verified').defaultTo(false);
        table.timestamp('last_login_at').nullable();
        table.timestamp('created_at').defaultTo(db.fn.now());
        table.timestamp('updated_at').defaultTo(db.fn.now());

        table.index(['email']);
        table.index(['is_active']);
      });
    }

    // Organization members table
    const membersExists = await db.schema.hasTable('organization_members');
    if (!membersExists) {
      await db.schema.createTable('organization_members', (table) => {
        table.uuid('id').primary();
        table.uuid('user_id').notNullable().references('id').inTable('users').onDelete('CASCADE');
        table.uuid('organization_id').notNullable().references('id').inTable('organizations').onDelete('CASCADE');
        table.enum('role', ['admin', 'member', 'viewer']).defaultTo('member');
        table.timestamp('joined_at').defaultTo(db.fn.now());
        table.timestamp('updated_at').defaultTo(db.fn.now());

        table.unique(['user_id', 'organization_id']);
        table.index(['organization_id']);
        table.index(['role']);
      });
    }

    // API keys table
    const apiKeysExists = await db.schema.hasTable('api_keys');
    if (!apiKeysExists) {
      await db.schema.createTable('api_keys', (table) => {
        table.uuid('id').primary();
        table.uuid('user_id').notNullable().references('id').inTable('users').onDelete('CASCADE');
        table.uuid('organization_id').notNullable().references('id').inTable('organizations').onDelete('CASCADE');
        table.string('name', 255).notNullable();
        table.string('key_hash', 255).notNullable();
        table.string('key_prefix', 20).notNullable();
        table.jsonb('scopes').defaultTo('[]');
        table.boolean('is_active').defaultTo(true);
        table.timestamp('last_used_at').nullable();
        table.timestamp('expires_at').nullable();
        table.timestamp('created_at').defaultTo(db.fn.now());

        table.index(['key_hash']);
        table.index(['user_id']);
        table.index(['organization_id']);
        table.index(['is_active']);
      });
    }

    // Session logs table
    const logsExists = await db.schema.hasTable('session_logs');
    if (!logsExists) {
      await db.schema.createTable('session_logs', (table) => {
        table.uuid('id').primary();
        table.uuid('user_id').nullable().references('id').inTable('users').onDelete('SET NULL');
        table.uuid('organization_id').nullable().references('id').inTable('organizations').onDelete('SET NULL');
        table.enum('action', ['login', 'logout', 'token_refresh', 'api_access']).notNullable();
        table.string('ip_address', 45).nullable();
        table.string('user_agent', 512).nullable();
        table.jsonb('metadata').defaultTo('{}');
        table.timestamp('created_at').defaultTo(db.fn.now());

        table.index(['user_id']);
        table.index(['action']);
        table.index(['created_at']);
      });
    }

    console.log('Database tables initialized successfully');

  } catch (error) {
    console.error('Database initialization error:', error);
    throw error;
  }
};

// Initialize on startup
initializeTables().catch(console.error);

module.exports = db;