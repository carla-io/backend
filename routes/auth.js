const express = require('express');
const router = express.Router();
const upload = require("../utils/multer");
const { register, 
    login, 
    user, 
    updateProfile, 
    DeleteUser,  
    verifyEmail, 
    getUserRegistrationsOverTime,  
    getGradeLevelDistribution, 
    getAllUsers,
    requestPasswordReset,
    resetPassword } = require('../controllers/authController');

router.post('/register', upload.single('profilePicture'),  register);
router.post('/login',  login);
router.post('/user', user);
router.put('/update-profile/:id', upload.single('profilePicture'), updateProfile);
router.get("/verify-email", verifyEmail); 
router.get('/registrations-over-time', getUserRegistrationsOverTime);
router.get('/grade-level-distribution', getGradeLevelDistribution);
router.get('/get-all-users', getAllUsers);
router.delete('/delete-user/:id', DeleteUser);
router.post('/request-password-reset', requestPasswordReset);
router.post('/reset-password/:token', resetPassword);

module.exports = router;
