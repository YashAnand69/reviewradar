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
