const User = require('../models/user');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cloudinary = require('../config/cloudinary');
const crypto = require('crypto');
const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
    host: process.env.MAILTRAP_HOST,
    port: process.env.MAILTRAP_PORT,
    auth: {
        user: process.env.MAILTRAP_USER,
        pass: process.env.MAILTRAP_PASS
    }
});


// Registration Controller
const register = async (req, res) => {
    const { name, email, password, gradeLevel } = req.body;

    try {
        const existingUser = await User.findOne({ email });
        if (existingUser) return res.status(400).json({ message: 'User already exists' });

        const hashedPassword = await bcrypt.hash(password, 10);

        let profilePicture = { public_id: '', url: '' };
        if (req.file) {
            const result = await cloudinary.uploader.upload(req.file.path, {
                folder: 'profile',
                width: 150,
                crop: 'scale',
            });
            profilePicture = { public_id: result.public_id, url: result.secure_url };
        }

        const user = await User.create({
            name,
            email,
            password: hashedPassword,
            gradeLevel,
            role: 'user',
            profilePicture,
            isVerified: false // New user must verify email
        });

        // Generate verification token
        const verificationToken = jwt.sign({ email: user.email }, process.env.JWT_SECRET, { expiresIn: "1d" });

        const verificationLink = `https://backend-6ioq.onrender.com/api/auth/verify-email?token=${verificationToken}`;

        const mailOptions = {
            from: process.env.MAILTRAP_HOST,
            to: user.email,
            subject: "Verify Your Email",
            html: `<p>Click <a href="${verificationLink}">here</a> to verify your email.</p>`,
        };

        await transporter.sendMail(mailOptions);

        res.status(201).json({
            message: "User registered! Please check your email to verify.",
            user: {
                id: user._id,
                name: user.name,
                email: user.email,
                gradeLevel: user.gradeLevel,
                role: user.role,
                profilePicture: user.profilePicture
            }
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};
// Login Controller
const login = async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await User.findOne({ email });
        if (!user) return res.status(400).json({ message: 'User not found' });

        if (!user.isVerified) return res.status(400).json({ message: 'Please verify your email before logging in.' });

        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) return res.status(400).json({ message: 'Invalid credentials' });

        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET, { expiresIn: '30d' });

        res.status(200).json({
            user: {
                id: user._id,
                name: user.name,
                email: user.email,
                gradeLevel: user.gradeLevel,
                role: user.role,
                profilePicture: user.profilePicture,
            },
            token,
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};


// Get user details from token
const user = async (req, res) => {
    try {
        const { token } = req.body;
        if (!token) return res.status(401).json({ message: 'No token provided' });

        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.id).select('-password');

        if (!user) return res.status(404).json({ message: 'User not found' });

        res.status(200).json({ user });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Update Profile
const updateProfile = async (req, res) => {
    try {
        const { name, email, gradeLevel } = req.body;
        const userId = req.params.id;

        const user = await User.findById(userId);
        if (!user) return res.status(404).json({ message: 'User not found' });

        // Upload new profile picture if provided
        let profilePicture = user.profilePicture;
        if (req.file) {
            if (profilePicture?.public_id) {
                await cloudinary.uploader.destroy(profilePicture.public_id); // Remove old image if exists
            }
            const result = await cloudinary.uploader.upload(req.file.path, {
                folder: 'profile',
                width: 150,
                crop: 'scale',
            });
            profilePicture = { public_id: result.public_id, url: result.secure_url };
        }
        

        // Update user fields
        user.name = name || user.name;
        user.email = email || user.email;
        user.gradeLevel = gradeLevel || user.gradeLevel;
        user.profilePicture = profilePicture;

        await user.save();

        res.status(200).json({ success: true, user });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

const verifyEmail = async (req, res) => {
    const { token } = req.query;

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findOne({ email: decoded.email });

        if (!user) return res.status(400).json({ message: "Invalid or expired token" });

        user.isVerified = true;
        await user.save();

        res.json({ message: "Email verified successfully! You can now log in." });
    } catch (error) {
        res.status(400).json({ message: "Invalid or expired token" });
    }
};

const getUserRegistrationsOverTime = async (req, res) => {
    try {
      const registrations = await User.aggregate([
        {
          $group: {
            _id: { $dateToString: { format: "%Y-%m-%d", date: "$createdAt" } },
            count: { $sum: 1 }
          }
        },
        { $sort: { _id: 1 } }
      ]);
  
      res.status(200).json({ data: registrations });
    } catch (error) {
      res.status(500).json({ message: 'Error retrieving user registration data', error });
    }
  };

  const getGradeLevelDistribution = async (req, res) => {
    try {
      const distribution = await User.aggregate([
        {
          $group: {
            _id: "$gradeLevel",
            count: { $sum: 1 }
          }
        },
        { $sort: { _id: 1 } }
      ]);
  
      res.status(200).json({ data: distribution });
    } catch (error) {
      res.status(500).json({ message: 'Error retrieving grade level distribution', error });
    }
  };

  const getAllUsers = async (req, res) => {
    try {
      const users = await User.find({ role: 'user' }).select('-password'); // Exclude password field
      res.status(200).json(users);
    } catch (error) {
      res.status(500).json({ message: 'Error retrieving users', error });
    }
  };


  const DeleteUser = async (req, res) => {  
    try {
        const userId = req.params.id;
        await User.findByIdAndDelete(userId);
        res.status(200).json({ message: 'User deleted successfully' });
      } catch (error) {
        res.status(500).json({ message: 'Error deleting user', error });
      }
  };

  const requestPasswordReset = async (req, res) => {
    const { email } = req.body;
  
    try {
      const user = await User.findOne({ email });
      if (!user) return res.status(404).json({ message: 'User not found' });
  
      // Generate a reset token
      const resetToken = crypto.randomBytes(32).toString('hex');
      const resetTokenHash = crypto.createHash('sha256').update(resetToken).digest('hex');
  
      // Set token and expiration on user object
      user.resetPasswordToken = resetTokenHash;
      user.resetPasswordExpires = Date.now() + 3600000; // 1 hour
      await user.save();
  
      // Construct reset URL
      const resetURL = `http://localhost:8081/ResetPassword/${resetToken}`; // Update to frontend URL
  
      // Email content
      const mailOptions = {
        from: 'no-reply@yourdomain.com', // Ensure this email is authorized in Mailtrap
        to: user.email,
        subject: 'Password Reset Request',
        html: `<p>You requested a password reset. Click <a href="${resetURL}">here</a> to reset your password.</p>`
      };
  
      // Send email
      await transporter.sendMail(mailOptions);
  
      res.status(200).json({ message: 'Password reset link sent to your email.' });
    } catch (error) {
      console.error('Error sending password reset email:', error);
      res.status(500).json({ message: 'Error processing password reset request', error });
    }
  };
  

// Reset Password
const resetPassword = async (req, res) => {
    const { token } = req.params;
    const { newPassword } = req.body;

    // Validate the newPassword input
    if (!newPassword || typeof newPassword !== 'string' || newPassword.length < 6) {
        return res.status(400).json({ message: 'Invalid or missing new password.' });
    }

    try {
        const resetTokenHash = crypto.createHash('sha256').update(token).digest('hex');

        // Find user by token and ensure token is not expired
        const user = await User.findOne({
            resetPasswordToken: resetTokenHash,
            resetPasswordExpires: { $gt: Date.now() }
        });

        if (!user) {
            return res.status(400).json({ message: 'Invalid or expired token' });
        }

        // Hash new password
        const hashedPassword = await bcrypt.hash(newPassword, 10);

        // Update user's password and clear reset token fields
        user.password = hashedPassword;
        user.resetPasswordToken = undefined;
        user.resetPasswordExpires = undefined;
        await user.save();

        res.status(200).json({ message: 'Password has been reset successfully.' });
    } catch (error) {
        console.error('Error resetting password:', error);
        res.status(500).json({ message: 'Error resetting password', error: error.message });
    }
};




module.exports = { register, 
    login, 
    user, 
    updateProfile, 
    DeleteUser,  
    verifyEmail,  
    getUserRegistrationsOverTime,  
    getGradeLevelDistribution, 
    getAllUsers,
    requestPasswordReset,
    resetPassword};
