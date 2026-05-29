require("dotenv").config();
const express = require("express");
const { startConsumer } = require("./consumers/clickConsumer");
const analyticsRoutes = require("./routes/analytics");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "analytics-service" });
});

app.use("/analytics", analyticsRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`[analytics-service] HTTP server running on port ${PORT}`);
});

// Start the SQS consumer loop
startConsumer().catch((err) => {
  console.error("[analytics-service] Consumer failed to start:", err);
  process.exit(1);
});
