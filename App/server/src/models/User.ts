/**
 * User Model
 */

import mongoose, { Document, Schema } from 'mongoose';
import bcrypt from 'bcrypt';

// User preferences
interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  fontSize: 'small' | 'medium' | 'large';
  dashboardLayout?: Record<string, any>;
  notifications: boolean;
}

// User document interface
export interface IUser extends Document {
  username: string;
  email: string;
  password: string;
  role: 'user' | 'admin';
  preferences: UserPreferences;
  lastLogin?: Date;
  createdAt: Date;
  updatedAt: Date;
  comparePassword(candidatePassword: string): Promise<boolean>;
}

// User schema
const UserSchema = new Schema<IUser>(
  {
    username: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      minlength: 3,
      maxlength: 30,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      lowercase: true,
    },
    password: {
      type: String,
      required: true,
      minlength: 8,
    },
    role: {
      type: String,
      enum: ['user', 'admin'],
      default: 'user',
    },
    preferences: {
      theme: {
        type: String,
        enum: ['light', 'dark', 'system'],
        default: 'system',
      },
      fontSize: {
        type: String,
        enum: ['small', 'medium', 'large'],
        default: 'medium',
      },
      dashboardLayout: {
        type: Schema.Types.Mixed,
      },
      notifications: {
        type: Boolean,
        default: true,
      },
    },
    lastLogin: {
      type: Date,
    },
  },
  {
    timestamps: true,
  }
);

// Hash password before saving
UserSchema.pre('save', async function (next) {
  const user = this;
  
  // Only hash the password if it has been modified (or is new)
  if (!user.isModified('password')) {
    return next();
  }
  
  try {
    // Generate salt
    const salt = await bcrypt.genSalt(10);
    
    // Hash password
    const hash = await bcrypt.hash(user.password, salt);
    
    // Replace plaintext password with hash
    user.password = hash;
    next();
  } catch (error) {
    return next(error as Error);
  }
});

// Compare password method
UserSchema.methods.comparePassword = async function (candidatePassword: string): Promise<boolean> {
  try {
    return await bcrypt.compare(candidatePassword, this.password);
  } catch (error) {
    return false;
  }
};

// Create and export User model
export const User = mongoose.model<IUser>('User', UserSchema);
