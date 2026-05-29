const { recordClick, getStats } = require("../src/services/db");

jest.mock("../src/services/db", () => ({
  initDB: jest.fn().mockResolvedValue(undefined),
  recordClick: jest.fn().mockResolvedValue(undefined),
  getStats: jest.fn().mockResolvedValue({
    total_clicks: 5,
    cache_hits: 3,
    first_click: "2024-01-01T00:00:00Z",
    last_click: "2024-01-02T00:00:00Z",
  }),
}));

test("recordClick is called with correct args", async () => {
  await recordClick({
    short_code: "abc123",
    timestamp: "2024-01-01T00:00:00Z",
    cache_hit: true,
  });

  expect(recordClick).toHaveBeenCalledWith({
    short_code: "abc123",
    timestamp: "2024-01-01T00:00:00Z",
    cache_hit: true,
  });
});

test("getStats returns analytics data", async () => {
  const stats = await getStats("abc123");
  expect(stats.total_clicks).toBe(5);
  expect(stats.cache_hits).toBe(3);
});
