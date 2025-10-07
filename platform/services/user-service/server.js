const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const cors = require('cors');
const redis = require('redis');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const { v4: uuidv4 } = require('uuid');
const winston = require('winston');
require('dotenv').config();

const db = require('./database');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Logger setup
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'user-service.log' })
  ]
});

// Redis client
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://redis:6379'
});

redisClient.on('error', (err) => {
  logger.error('Redis error:', err);
});

redisClient.connect();

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));

// Rate limiting
const authRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: { error: 'Too many authentication attempts' },
  standardHeaders: true,
  legacyHeaders: false,
});

const generalRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests' },
});

app.use('/auth', authRateLimit);
app.use(generalRateLimit);

// JWT middleware
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  try {
    // Check if token is blacklisted
    const isBlacklisted = await redisClient.get(`blacklist:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await db('users').where({ id: decoded.userId }).first();

    if (!user || !user.is_active) {
      return res.status(401).json({ error: 'User not found or inactive' });
    }

    req.user = user;
    next();
  } catch (error) {
    logger.error('Token verification error:', error);
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// Check organization access
const checkOrgAccess = (requiredRole = null) => {
  return async (req, res, next) => {
    try {
      const membership = await db('organization_members')
        .where({
          user_id: req.user.id,
          organization_id: req.params.orgId || req.body.organization_id
        })
        .first();

      if (!membership) {
        return res.status(403).json({ error: 'Access denied to organization' });
      }

      if (requiredRole && membership.role !== requiredRole && membership.role !== 'admin') {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }

      req.orgMembership = membership;
      next();
    } catch (error) {
      logger.error('Organization access check error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
};

// Utility functions
const hashPassword = async (password) => {
  return await bcrypt.hash(password, 12);
};

const validatePassword = async (password, hashedPassword) => {
  return await bcrypt.compare(password, hashedPassword);
};

const generateTokens = (userId) => {
  const accessToken = jwt.sign(
    { userId },
    process.env.JWT_SECRET,
    { expiresIn: '1h' }
  );

  const refreshToken = jwt.sign(
    { userId, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
  );

  return { accessToken, refreshToken };
};

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'iris-user-service' });
});

// User registration
app.post('/auth/register', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/),
  body('name').trim().isLength({ min: 1, max: 255 }),
  body('organization_name').optional().trim().isLength({ min: 1, max: 255 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password, name, organization_name } = req.body;

    // Check if user exists
    const existingUser = await db('users').where({ email }).first();
    if (existingUser) {
      return res.status(409).json({ error: 'User already exists' });
    }

    const hashedPassword = await hashPassword(password);
    const userId = uuidv4();

    await db.transaction(async (trx) => {
      // Create user
      await trx('users').insert({
        id: userId,
        email,
        password_hash: hashedPassword,
        name,
        created_at: new Date(),
        is_active: true
      });

      // Create or join organization
      let orgId;
      if (organization_name) {
        // Create new organization
        orgId = uuidv4();
        await trx('organizations').insert({
          id: orgId,
          name: organization_name,
          created_at: new Date(),
          is_active: true
        });
      } else {
        // Join default organization
        const defaultOrg = await trx('organizations')
          .where({ name: 'Default Organization' })
          .first();

        if (!defaultOrg) {
          orgId = uuidv4();
          await trx('organizations').insert({
            id: orgId,
            name: 'Default Organization',
            created_at: new Date(),
            is_active: true
          });
        } else {
          orgId = defaultOrg.id;
        }
      }

      // Add user to organization
      await trx('organization_members').insert({
        id: uuidv4(),
        user_id: userId,
        organization_id: orgId,
        role: organization_name ? 'admin' : 'member',
        joined_at: new Date()
      });
    });

    logger.info(`User registered: ${email}`);
    res.status(201).json({ message: 'User created successfully' });

  } catch (error) {
    logger.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// User login
app.post('/auth/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').notEmpty()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password, totp_code } = req.body;

    const user = await db('users').where({ email }).first();
    if (!user || !user.is_active) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isValidPassword = await validatePassword(password, user.password_hash);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Check 2FA if enabled
    if (user.totp_secret) {
      if (!totp_code) {
        return res.status(200).json({
          requires_2fa: true,
          message: 'Please provide TOTP code'
        });
      }

      const isValidTOTP = speakeasy.totp.verify({
        secret: user.totp_secret,
        encoding: 'base32',
        token: totp_code,
        window: 2
      });

      if (!isValidTOTP) {
        return res.status(401).json({ error: 'Invalid 2FA code' });
      }
    }

    const { accessToken, refreshToken } = generateTokens(user.id);

    // Store refresh token
    await redisClient.setEx(`refresh:${user.id}`, 7 * 24 * 3600, refreshToken);

    // Update last login
    await db('users').where({ id: user.id }).update({
      last_login_at: new Date()
    });

    logger.info(`User logged in: ${email}`);

    res.json({
      access_token: accessToken,
      refresh_token: refreshToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        has_2fa: !!user.totp_secret
      }
    });

  } catch (error) {
    logger.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Refresh token
app.post('/auth/refresh', async (req, res) => {
  try {
    const { refresh_token } = req.body;

    if (!refresh_token) {
      return res.status(401).json({ error: 'Refresh token required' });
    }

    const decoded = jwt.verify(refresh_token, process.env.JWT_REFRESH_SECRET);

    if (decoded.type !== 'refresh') {
      return res.status(401).json({ error: 'Invalid token type' });
    }

    // Check if refresh token exists in Redis
    const storedToken = await redisClient.get(`refresh:${decoded.userId}`);
    if (storedToken !== refresh_token) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }

    const { accessToken, refreshToken: newRefreshToken } = generateTokens(decoded.userId);

    // Update stored refresh token
    await redisClient.setEx(`refresh:${decoded.userId}`, 7 * 24 * 3600, newRefreshToken);

    res.json({
      access_token: accessToken,
      refresh_token: newRefreshToken
    });

  } catch (error) {
    logger.error('Token refresh error:', error);
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});

// Logout
app.post('/auth/logout', authenticateToken, async (req, res) => {
  try {
    const token = req.headers['authorization'].split(' ')[1];

    // Blacklist the access token
    const decoded = jwt.decode(token);
    const ttl = decoded.exp - Math.floor(Date.now() / 1000);
    if (ttl > 0) {
      await redisClient.setEx(`blacklist:${token}`, ttl, '1');
    }

    // Remove refresh token
    await redisClient.del(`refresh:${req.user.id}`);

    logger.info(`User logged out: ${req.user.email}`);
    res.json({ message: 'Logged out successfully' });

  } catch (error) {
    logger.error('Logout error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get user profile
app.get('/users/me', authenticateToken, async (req, res) => {
  try {
    const organizations = await db('organization_members')
      .join('organizations', 'organization_members.organization_id', 'organizations.id')
      .where('organization_members.user_id', req.user.id)
      .select('organizations.id', 'organizations.name', 'organization_members.role');

    res.json({
      id: req.user.id,
      email: req.user.email,
      name: req.user.name,
      created_at: req.user.created_at,
      last_login_at: req.user.last_login_at,
      has_2fa: !!req.user.totp_secret,
      organizations
    });

  } catch (error) {
    logger.error('Get profile error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Setup 2FA
app.post('/users/me/2fa/setup', authenticateToken, async (req, res) => {
  try {
    if (req.user.totp_secret) {
      return res.status(400).json({ error: '2FA already enabled' });
    }

    const secret = speakeasy.generateSecret({
      name: `IRIS Platform (${req.user.email})`,
      issuer: 'IRIS Platform'
    });

    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

    // Store temporary secret (not activated yet)
    await redisClient.setEx(`2fa_setup:${req.user.id}`, 300, secret.base32);

    res.json({
      secret: secret.base32,
      qr_code: qrCodeUrl,
      backup_codes: [], // In production, generate backup codes
    });

  } catch (error) {
    logger.error('2FA setup error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Verify and enable 2FA
app.post('/users/me/2fa/verify', authenticateToken, [
  body('totp_code').isLength({ min: 6, max: 6 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { totp_code } = req.body;

    const tempSecret = await redisClient.get(`2fa_setup:${req.user.id}`);
    if (!tempSecret) {
      return res.status(400).json({ error: '2FA setup not found or expired' });
    }

    const isValid = speakeasy.totp.verify({
      secret: tempSecret,
      encoding: 'base32',
      token: totp_code,
      window: 2
    });

    if (!isValid) {
      return res.status(400).json({ error: 'Invalid TOTP code' });
    }

    // Enable 2FA
    await db('users').where({ id: req.user.id }).update({
      totp_secret: tempSecret,
      updated_at: new Date()
    });

    // Clean up temp secret
    await redisClient.del(`2fa_setup:${req.user.id}`);

    logger.info(`2FA enabled for user: ${req.user.email}`);
    res.json({ message: '2FA enabled successfully' });

  } catch (error) {
    logger.error('2FA verification error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Organization management
app.get('/organizations', authenticateToken, async (req, res) => {
  try {
    const organizations = await db('organization_members')
      .join('organizations', 'organization_members.organization_id', 'organizations.id')
      .where('organization_members.user_id', req.user.id)
      .select(
        'organizations.id',
        'organizations.name',
        'organizations.created_at',
        'organization_members.role',
        'organization_members.joined_at'
      );

    res.json({ organizations });

  } catch (error) {
    logger.error('Get organizations error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get organization members
app.get('/organizations/:orgId/members', authenticateToken, checkOrgAccess(), async (req, res) => {
  try {
    const members = await db('organization_members')
      .join('users', 'organization_members.user_id', 'users.id')
      .where('organization_members.organization_id', req.params.orgId)
      .select(
        'users.id',
        'users.name',
        'users.email',
        'organization_members.role',
        'organization_members.joined_at'
      );

    res.json({ members });

  } catch (error) {
    logger.error('Get members error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  logger.info(`User service running on port ${PORT}`);
});

module.exports = app;