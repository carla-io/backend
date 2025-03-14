const mongoose = require('mongoose');
const validator = require('validator');

const UserSchema = new mongoose.Schema({
    name: { 
        type: String, 
        required: [true, 'Please enter your name'],
        maxLength: [30, 'Your name cannot exceed 30 characters'] ,
        unique: true 
    },
    email: { 
        type: String, 
        required: [true, 'Please enter your email'], 
        unique: true,
        validate: [validator.isEmail, 'Please enter valid email address']
    },
    password: { 
        type: String, 
        required: [true, 'Please enter your password'],
        minlength: [6, 'Your password must be longer than 6 characters'],
        required: true 
    },
    profilePicture: {
        public_id: {
            type: String,
            required: true
        },
        url: {
            type: String,
            required: true
        }
    },
    role: {
        type: String,
        default: 'user',
        enum: ['user', 'admin'] // you can add more roles as needed
    },
    gradeLevel :{
        type: String,
        required: [true, 'Please enter your grade level'],
        enum: {
            values: [
                'Junior High School',
                'Senior High School',
                'College'
            ],
            message: 'Please select correct grade level'
        }
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    isVerified: { type: Boolean, default: false },
    resetPasswordToken: String,
    resetPasswordExpires: Date, // New field
    isArchived: { type: Boolean, default: false }

});

module.exports = mongoose.model('User', UserSchema);