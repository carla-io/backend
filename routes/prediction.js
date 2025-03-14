const express = require("express");
const Prediction = require("../models/prediction");
const mongoose = require("mongoose");

const router = express.Router();

// Save or Update Predictions
router.post("/save", async (req, res) => {
  try {
    const { userId, predictions, certprediction, pqprediction_jhs, prediction_exam_jhs, examScores } = req.body;

    if (!userId || !mongoose.Types.ObjectId.isValid(userId)) {
      return res.status(400).json({ success: false, message: "Invalid or missing user ID" });
    }

    const updateFields = {};
    if (predictions) updateFields.predictions = predictions;
    if (certprediction) updateFields.certprediction = certprediction;
    if (pqprediction_jhs) {
      updateFields.pqprediction_jhs = {
        ...pqprediction_jhs,
        strandScoresList: pqprediction_jhs.predictionScores
          ? pqprediction_jhs.predictionScores.map(({ strand, score }) => ({ strand, score }))
          : [],
      };
    }
    if (prediction_exam_jhs) updateFields.prediction_exam_jhs = prediction_exam_jhs;
    if (examScores) updateFields.examScores = examScores;

    updateFields.updatedAt = new Date();

    const updatedPrediction = await Prediction.findOneAndUpdate(
      { userId: new mongoose.Types.ObjectId(userId) },
      { $set: updateFields },
      { new: true, upsert: true }
    );

    res.status(200).json({ success: true, message: "Predictions updated successfully.", data: updatedPrediction });
  } catch (error) {
    console.error("Error saving predictions:", error);
    res.status(500).json({ success: false, message: "Server error", error });
  }
});

// Get Top Strands
router.get("/top-strands", async (req, res) => {
  try {
    const allPredictions = await Prediction.find();

    if (!allPredictions.length) {
      return res.status(404).json({ success: false, message: "No predictions found." });
    }

    const strandScores = {};

    allPredictions.forEach((prediction) => {
      Object.entries(prediction.predictions || {}).forEach(([strand, data]) => {
        const strandAvg = data.strand_average || 0;
        if (!strandScores[strand]) {
          strandScores[strand] = { total: 0, count: 0 };
        }
        strandScores[strand].total += strandAvg;
        strandScores[strand].count += 1;
      });
    });

    const sortedStrands = Object.entries(strandScores)
      .map(([strand, { total, count }]) => ({
        strand,
        average: total / count,
      }))
      .sort((a, b) => b.average - a.average);

    res.status(200).json({ success: true, data: sortedStrands });
  } catch (error) {
    console.error("Error fetching top strands:", error);
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

    const userPrediction = await Prediction.findOne({ userId: new mongoose.Types.ObjectId(userId) });

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
    // Fetch all exam scores without filtering by userId
    const allExamScores = await ExamScoreModel.find();

    if (!allExamScores.length) {
      return res.status(404).json({ success: false, message: "No exam scores found." });
    }

    // Aggregate exam scores
    const categoryScores = {};

    allExamScores.forEach((exam) => {
      Object.entries(exam.scores || {}).forEach(([category, score]) => {
        if (!categoryScores[category]) {
          categoryScores[category] = { total: 0, count: 0 };
        }
        categoryScores[category].total += score;
        categoryScores[category].count += 1;
      });
    });

    const sortedCategories = Object.entries(categoryScores)
      .map(([category, { total, count }]) => ({
        category,
        averageScore: total / count,
      }))
      .sort((a, b) => b.averageScore - a.averageScore);

    res.status(200).json({ success: true, data: sortedCategories });
  } catch (error) {
    console.error("Error fetching exam scores:", error);
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
