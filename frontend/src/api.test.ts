import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
const health = { status: "ok", model_configured: true, model_ready: true };
const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
let fetchMock: ReturnType<typeof vi.fn>;
let api: (typeof import("./api"))["api"];
beforeEach(async () => {
  vi.resetModules();
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  api = (await import("./api")).api;
});
afterEach(() => vi.unstubAllGlobals());
async function connect() {
  fetchMock
    .mockResolvedValueOnce(json({ api_token: "first-session" }))
    .mockResolvedValueOnce(json(health));
  await api.connect();
  fetchMock.mockClear();
}
describe("local connection recovery", () => {
  it("explains an offline server without retrying a potentially executed write", async () => {
    await connect();
    fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));
    await expect(
      api.save("analysis", "card", "reviewed", "keep note"),
    ).rejects.toMatchObject({
      name: "LocalConnectionError",
      message: expect.stringContaining("typed notes remain"),
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it("renews a rejected session once and retries the same write with a new token", async () => {
    await connect();
    fetchMock
      .mockResolvedValueOnce(json({ detail: "unauthorized" }, 401))
      .mockResolvedValueOnce(json({ api_token: "new-session" }))
      .mockResolvedValueOnce(json({ state: "reviewed" }));
    await expect(
      api.save("analysis", "card", "reviewed", "check patch"),
    ).resolves.toEqual({ state: "reviewed" });
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[0][1].body).toBe(
      fetchMock.mock.calls[2][1].body,
    );
    expect(fetchMock.mock.calls[2][1].headers["X-ReviewRadar-Token"]).toBe(
      "new-session",
    );
    expect(fetchMock.mock.calls[1][0]).toBe("/runtime-config");
  });
  it("stops after a second rejected token instead of looping", async () => {
    await connect();
    fetchMock
      .mockResolvedValueOnce(json({}, 401))
      .mockResolvedValueOnce(json({ api_token: "new-session" }))
      .mockResolvedValueOnce(json({}, 401));
    await expect(api.sample()).rejects.toMatchObject({
      name: "LocalConnectionError",
      message: expect.stringContaining("could not be renewed"),
    });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
  it("does not replay a model operation after a server error", async () => {
    await connect();
    fetchMock.mockResolvedValueOnce(
      json({ detail: "Model unavailable; use the baseline." }, 503),
    );
    await expect(api.analyse("snapshot", "model")).rejects.toThrow(
      "Model unavailable",
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it("treats failed session renewal as disconnected and preserves the original action", async () => {
    await connect();
    fetchMock
      .mockResolvedValueOnce(json({}, 401))
      .mockRejectedValueOnce(new TypeError("Failed to fetch"));
    await expect(
      api.importGithub("author", ["https://github.com/a/b/pull/1"]),
    ).rejects.toMatchObject({ name: "LocalConnectionError" });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
  it("uses the same one-time recovery for a review-sheet download", async () => {
    await connect();
    fetchMock
      .mockResolvedValueOnce(json({}, 401))
      .mockResolvedValueOnce(json({ api_token: "renewed" }))
      .mockResolvedValueOnce(new Response("# Review sheet"));
    expect(await (await api.export("analysis")).text()).toBe("# Review sheet");
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
  it("gives an actionable startup error when the first connection cannot be made", async () => {
    fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));
    await expect(api.connect()).rejects.toMatchObject({
      name: "LocalConnectionError",
      message: expect.stringContaining("Retry connection"),
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it("classifies an HTML bootstrap response as a connection failure", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response("<html>Not the local app</html>"),
    );
    await expect(api.connect()).rejects.toMatchObject({
      name: "LocalConnectionError",
      message: expect.stringContaining("configuration is invalid"),
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it("classifies a null bootstrap response as a connection failure", async () => {
    fetchMock.mockResolvedValueOnce(json(null));
    await expect(api.connect()).rejects.toMatchObject({
      name: "LocalConnectionError",
      message: expect.stringContaining("configuration is invalid"),
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
