const express = require("express");
const { getStats } = require("../services/db");

const router = express.Router();

router.get("/:short_code", async (req, res) => {
  try {
    const stats = await getStats(req.params.short_code);
    if (!stats || stats.total_clicks === 0) {
      return res.status(404).json({ error: "No analytics found for this code" });
    }
    res.json({
      short_code: req.params.short_code,
      ...stats,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

module.exports = router;
