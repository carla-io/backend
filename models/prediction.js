const mongoose = require("mongoose");

// Sub-schema for pqprediction_jhs
const pqPredictionSchema = new mongoose.Schema({
  predictedStrand: { type: String, default: "Unknown" },
  predictionScores: [{
    score: { type: Number, min: 0, max: 100, required: true }, // Ensure valid range
    strand: { type: String, required: true }
  }],
  strandScoresList: [{
    strand: { type: String, required: true },
    score: { type: Number, min: 0, max: 100, required: true }
  }]
}, { _id: false }); // Prevents an extra _id field

// Define the main Prediction schema
const predictionSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, required: true, ref: "User" },
  predictions: { type: Object, default: {} },
  certprediction: { type: Object, default: {} },
  pqprediction_jhs: { type: pqPredictionSchema, default: {} }, // Ensure default object
  prediction_exam_jhs: { type: Object, default: {} },
  examScores: { type: Object, default: {} } // Can be structured further if needed
}, { timestamps: true });

module.exports = mongoose.model("Prediction", predictionSchema);
