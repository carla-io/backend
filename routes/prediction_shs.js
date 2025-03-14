const express = require("express");
const PredictionSHS = require("../models/prediction_shs"); // Ensure correct import
const mongoose = require("mongoose");

const router = express.Router();

router.post("/save", async (req, res) => {
    try {
      const { userId, predictions, certprediction, shspqprediction, prediction_exam_shs, examScores } = req.body;
  
      const updateFields = { predictions, certprediction, shspqprediction, prediction_exam_shs, examScores };
  
      const updatedPrediction = await PredictionSHS.findOneAndUpdate(
        { userId: new mongoose.Types.ObjectId(userId) }, 
        { $set: updateFields },
        { new: true, upsert: true }
      );
  
      res.json({ success: true, message: "Prediction saved!", data: updatedPrediction });
    } catch (error) {
      console.error("Error saving prediction:", error);
      res.status(500).json({ success: false, message: "Server error" });
    }
  });
// Save or Update Predictions
// router.post("/save", async (req, res) => {
//   try {
//     const { userId, predictions, certprediction, shspqprediction, prediction_exam_shs, examScores } = req.body;

//     if (!userId || !mongoose.Types.ObjectId.isValid(userId)) {
//       return res.status(400).json({ success: false, message: "Invalid or missing user ID" });
//     }

//     const updateFields = {};
//     if (predictions) updateFields.predictions = predictions;
//     if (certprediction) updateFields.certprediction = certprediction;
//     if (shspqprediction) {
//       updateFields.shspqprediction = {
//         ...shspqprediction,
//         strandScoresList: shspqprediction.predictionScores
//           ? shspqprediction.predictionScores.map(({ strand, score }) => ({ strand, score }))
//           : [],
//       };
//     }
//     if (prediction_exam_shs) updateFields.prediction_exam_shs = prediction_exam_shs;
//     if (examScores) updateFields.examScores = examScores;

//     updateFields.updatedAt = new Date();

//     const updatedPrediction = await PredictionSHS.findOneAndUpdate(
//         { userId: new mongoose.Types.ObjectId(userId) },
//         { $set: updateFields },
//         { new: true, upsert: true }
//       );
      

//     res.status(200).json({ success: true, message: "Predictions updated successfully.", data: updatedPrediction });
//   } catch (error) {
//     console.error("Error saving predictions:", error);
//     res.status(500).json({ success: false, message: "Server error", error });
//   }
// });

// Get Top Strands
router.get("/top-courses", async (req, res) => {
    try {
        const allPredictions = await PredictionSHS.find();

        if (!allPredictions.length) {
            return res.status(404).json({ success: false, message: "No predictions found." });
        }

        const courseScores = {};
        let totalPredictions = 0; // Track total predictions for percentage calculation

        allPredictions.forEach((prediction) => {
            Object.entries(prediction.predictions || {}).forEach(([course, data]) => {
                const percentage = data.percentage || 0; // Get percentage directly

                if (!courseScores[course]) {
                    courseScores[course] = { total: 0, count: 0 };
                }

                courseScores[course].total += percentage;
                courseScores[course].count += 1;
                totalPredictions += 1; // Count total course predictions
            });
        });

        const sortedCourses = Object.entries(courseScores)
            .map(([course, { total, count }]) => ({
                course,
                averagePercentage: (total / count).toFixed(2), // Average percentage
                overallPercentage: ((total / totalPredictions) * 100).toFixed(2) // Percentage relative to total
            }))
            .sort((a, b) => b.averagePercentage - a.averagePercentage);

        res.status(200).json({ success: true, data: sortedCourses });
    } catch (error) {
        console.error("Error fetching top courses:", error);
        res.status(500).json({ success: false, message: "Server error", error });
    }
});

  

// Get User Predictions
router.get("/:userId", async (req, res) => {
  try {
    const { userId } = req.params;

    if (!mongoose.Types.ObjectId.isValid(userId)) {
      return res.status(400).json({ success: false, message: "Invalid user ID format" });
    }

    const userPrediction = await PredictionSHS.findOne({ userId: new mongoose.Types.ObjectId(userId) });

    if (!userPrediction) {
      return res.status(404).json({ success: false, message: "No predictions found" });
    }

    const sortedPredictions = Object.entries(userPrediction.predictions || {})
      .sort((a, b) => (b[1]?.strand_average || 0) - (a[1]?.strand_average || 0))
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});

    res.json({ success: true, data: sortedPredictions });
  } catch (error) {
    console.error("Error fetching user predictions:", error);
    res.status(500).json({ success: false, message: "Server error", error });
  }
});

// Get Exam Scores for a Specific User
router.get("/exam-scores", async (req, res) => {
  try {
    const predictions = await Prediction.find({}, "examScores");

    if (!predictions.length) {
      return res.status(404).json({ success: false, message: "No exam scores found." });
    }

    const totalScores = {
      "Mathematics Section": 0,
      "Scientific Ability": 0,
      "Verbal Ability": 0,
      "Mechanical and Technical Ability": 0,
      "Entrepreneurial Skills": 0,
    };

    predictions.forEach((pred) => {
      if (pred.examScores) {
        Object.keys(totalScores).forEach((key) => {
          const scoreString = pred.examScores[key]; // Example: "7 / 20 (35.00%)"
          if (scoreString) {
            const match = scoreString.match(/\((\d+\.\d+)%\)/);
            const percentage = match ? parseFloat(match[1]) : 0; // Extract percentage
            totalScores[key] += percentage;
          }
        });
      }
    });

    res.status(200).json({ success: true, totalExamScores: totalScores });
  } catch (error) {
    console.error("Error fetching total exam scores:", error);
    res.status(500).json({ success: false, message: "Server error", error });
  }
});


// ✅ THEN define the user-specific exam scores route
// router.get("/exam-scores/:userId", async (req, res) => {
//   try {
//     const { userId } = req.params;

//     console.log("Received userId:", userId);

//     // Validate if userId is a valid ObjectId
//     if (!mongoose.Types.ObjectId.isValid(userId)) {
//       return res.status(400).json({ success: false, message: "Invalid user ID format" });
//     }

//     const prediction = await Prediction.findOne({ userId: new mongoose.Types.ObjectId(userId) });

//     if (!prediction || !prediction.examScores) {
//       return res.status(404).json({ success: false, message: "No exam scores found for this user." });
//     }

//     res.status(200).json({ success: true, examScores: prediction.examScores });
//   } catch (error) {
//     console.error("Error fetching user exam scores:", error);
//     res.status(500).json({ success: false, message: "Server error", error });
//   }
// });


module.exports = router;
