// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { api } from "./api";
import packet from "../public/sample.json";

vi.mock("./api", () => ({ api: { connect: vi.fn(), sample: vi.fn() } }));
beforeEach(() => {
  vi.resetAllMocks();
  localStorage.clear();
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockReturnValue({ matches: false }),
  });
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue({
        ok: true,
        json: async () => structuredClone(packet),
      }),
  );
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe.runIf(import.meta.env.VITE_REPLAY === "1")(
  "explicit public replay adapter (DOM simulation)",
  () => {
    it("loads only the fixed mixed replay file and ignores arbitrary example URL queries", async () => {
      const user = userEvent.setup();
      const originalUrl = window.location.href;
      window.history.replaceState({}, "", "?example=https%3A%2F%2Fevil.example%2Ffake.json");
      try {
        render(<App />);
        await screen.findByRole("button", { name: /Mark reviewed locally/ });
        expect(vi.mocked(fetch).mock.calls[0][0]).toMatch(/(?:^|\/)sample\.json$/);
        const mixed = structuredClone(packet);
        mixed.analysis.id = "synthetic-replay-switch-analysis";
        vi.mocked(fetch).mockResolvedValueOnce({ok: true, json: async () => mixed} as Response);
        await user.selectOptions(screen.getByRole("combobox", { name: /^Saved example$/ }), "mixed");
        await user.click(screen.getByRole("button", { name: /Open saved example/ }));
        await waitFor(() => expect(vi.mocked(fetch).mock.calls[1][0]).toMatch(/(?:^|\/)mixed-sample\.json$/));
        expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url).includes("evil.example"))).toBe(false);
        expect(api.connect).not.toHaveBeenCalled();
        expect(api.sample).not.toHaveBeenCalled();
      } finally {
        window.history.replaceState({}, "", originalUrl);
      }
    });
    it("preserves a replay assessment and note when browser storage rejects the save", async () => {
      const user = userEvent.setup();
      render(<App />);
      await screen.findByRole("button", { name: /Mark reviewed locally/ });
      await user.selectOptions(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }), "not_a_request");
      await user.type(screen.getByRole("textbox", { name: /Note/ }), "Needs another look");
      const setItem = vi.spyOn(Storage.prototype, "setItem").mockImplementationOnce(() => { throw new Error("Storage quota exceeded"); });
      await user.click(screen.getByRole("button", { name: /Save decision/ }));
      await screen.findByText(/Not saved. Your note and assessment remain here/);
      expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("not_a_request");
      expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("Needs another look");
      expect(localStorage.getItem(`reviewradar:${packet.analysis.id}`)).toBeNull();
      setItem.mockRestore();
    });
    it("restores an old replay decision without inventing disagreement and persists a reversible assessment separately", async () => {
      const user = userEvent.setup();
      localStorage.setItem(`reviewradar:${packet.analysis.id}`, JSON.stringify([{
        analysis_id: packet.analysis.id,
        card_id: packet.analysis.cards[0].id,
        state: "reviewed",
        note: "Previously inspected",
        updated_at: "2026-10-23T12:00:00Z",
      }]));
      render(<App />);
      await screen.findByRole("button", { name: /Reopen locally/ });
      const assessment = screen.getByRole("combobox", { name: /Assessment of this model suggestion/ });
      expect((assessment as HTMLSelectElement).value).toBe("unassessed");
      await user.selectOptions(assessment, "reply_not_relevant");
      expect(localStorage.getItem(`reviewradar:${packet.analysis.id}`)).not.toContain("reply_not_relevant");
      await user.click(screen.getByRole("button", { name: /Save decision/ }));
      await waitFor(() => expect(localStorage.getItem(`reviewradar:${packet.analysis.id}`)).toContain("reply_not_relevant"));
      const saved = JSON.parse(localStorage.getItem(`reviewradar:${packet.analysis.id}`)!)[0];
      expect(saved.state).toBe("reviewed");
      expect(saved.note).toBe("Previously inspected");
      expect(packet.analysis.prompt_version).toBe("human-review-passages-v9");
      await user.click(screen.getByRole("button", { name: /Reset my replay choices/ }));
      await screen.findByRole("button", { name: /Mark reviewed locally/ });
      expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("unassessed");
    });
    it("labels the saved historical run and never attempts a local backend connection", async () => {
      render(<App />);
      await screen.findByRole("button", { name: /Mark reviewed locally/ });
      expect(screen.getByText("Historical replay")).toBeTruthy();
      expect(
        screen.getByText("A real historical sample, not a live inbox"),
      ).toBeTruthy();
      expect(
        screen.queryByRole("button", { name: /Import your PRs/ }),
      ).toBeNull();
      expect(
        screen.queryByRole("button", { name: /Analyse locally/ }),
      ).toBeNull();
      expect(api.connect).not.toHaveBeenCalled();
      expect(api.sample).not.toHaveBeenCalled();
    });
    it("saves choices only in browser storage and resets the displayed note and state", async () => {
      const user = userEvent.setup();
      render(<App />);
      await screen.findByRole("button", { name: /Mark reviewed locally/ });
      await user.type(
        screen.getByRole("textbox", { name: /Note/ }),
        "A browser-local trial note",
      );
      await user.click(
        screen.getByRole("button", { name: /Mark reviewed locally/ }),
      );
      await screen.findByRole("button", { name: /Reopen locally/ });
      expect(
        localStorage.getItem(`reviewradar:${packet.analysis.id}`),
      ).toContain("browser-local trial note");
      await user.click(
        screen.getByRole("button", { name: /Reset my replay choices/ }),
      );
      await screen.findByRole("button", { name: /Mark reviewed locally/ });
      expect(
        (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
          .value,
      ).toBe("");
      expect(
        localStorage.getItem(`reviewradar:${packet.analysis.id}`),
      ).toBeNull();
    });
    it("reports an unavailable replay without silently changing into local mode", async () => {
      vi.mocked(fetch).mockResolvedValueOnce({ ok: false } as Response);
      render(<App />);
      await waitFor(() =>
        expect(screen.getByRole("alert").textContent).toContain(
          "sample is unavailable",
        ),
      );
      expect(screen.getByRole("button", { name: /Retry sample/ })).toBeTruthy();
      expect(api.connect).not.toHaveBeenCalled();
    });
  },
);
