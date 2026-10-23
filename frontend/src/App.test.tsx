// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  act,
  cleanup,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { api } from "./api";
import packet from "../public/sample.json";

vi.mock("./api", () => ({
  api: {
    connect: vi.fn(),
    sample: vi.fn(),
    dispositions: vi.fn(),
    save: vi.fn(),
    history: vi.fn(),
    importGithub: vi.fn(),
    importSnapshot: vi.fn(),
    analyse: vi.fn(),
  },
}));

beforeEach(() => {
  vi.resetAllMocks();
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockReturnValue({ matches: false }),
  });
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
  vi.mocked(api.connect).mockResolvedValue({
    status: "ok",
    version: "test",
    model_configured: true,
    github_available: true,
    mode: "local",
  });
  vi.mocked(api.sample).mockResolvedValue(structuredClone(packet) as never);
  vi.mocked(api.dispositions).mockResolvedValue([]);
  vi.mocked(api.history).mockResolvedValue([]);
  vi.mocked(api.save).mockImplementation(
    async (analysis_id, card_id, state, note) => ({
      analysis_id,
      card_id,
      state,
      note,
      updated_at: "2026-10-23T12:00:00Z",
    }),
  );
});
afterEach(cleanup);

async function openSample() {
  const user = userEvent.setup();
  render(<App />);
  const explore = await screen.findByRole("button", {
    name: /Explore the historical sample/,
  });
  await waitFor(() => expect(explore.hasAttribute("disabled")).toBe(false));
  await user.click(explore);
  await screen.findByRole("button", { name: /Mark reviewed locally/ });
  return user;
}

describe("evidence workbench integration (DOM simulation, not a visual browser audit)", () => {
  it("retains incomplete historical context and never equates a response with a verified fix", async () => {
    await openSample();
    expect(
      screen.getByText("Incomplete coverage — inspect the sources"),
    ).toBeTruthy();
    expect(
      screen.getAllByText(/A possible response is a lead to inspect/).length,
    ).toBeGreaterThan(0);
    expect(screen.getAllByText(/Possible response/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/All caught up/i)).toBeNull();
    expect(api.analyse).not.toHaveBeenCalled();
  });
  it("saves and reopens decisions through the API without hiding the card", async () => {
    const user = await openSample();
    await user.click(
      screen.getByRole("button", { name: /Mark reviewed locally/ }),
    );
    await screen.findByRole("button", { name: /Reopen locally/ });
    expect(api.save).toHaveBeenLastCalledWith(
      packet.analysis.id,
      expect.any(String),
      "reviewed",
      "",
    );
    await user.click(screen.getByRole("button", { name: /Reopen locally/ }));
    await screen.findByRole("button", { name: /Mark reviewed locally/ });
    expect(api.save).toHaveBeenLastCalledWith(
      packet.analysis.id,
      expect.any(String),
      "open",
      "",
    );
  });
  it("keeps an unsaved note when inspecting Sources and returning", async () => {
    const user = await openSample();
    await user.type(
      screen.getByRole("textbox", { name: /Note/ }),
      "Inspect the actual patch separately",
    );
    await user.click(screen.getByRole("button", { name: /^Sources / }));
    await user.click(screen.getByRole("button", { name: /^Review queue/ }));
    expect(
      (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
        .value,
    ).toBe("Inspect the actual patch separately");
  });
  it("retains typed notes and shows an honest save failure", async () => {
    const user = await openSample();
    vi.mocked(api.save).mockRejectedValueOnce(
      new Error("Session expired; reload after copying your note."),
    );
    await user.type(
      screen.getByRole("textbox", { name: /Note/ }),
      "Keep this note",
    );
    await user.click(screen.getByRole("button", { name: /Save note/ }));
    await screen.findByText(/Not saved. Your note remains here/);
    expect(
      (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
        .value,
    ).toBe("Keep this note");
    expect(
      screen.getByRole("button", { name: /Mark reviewed locally/ }),
    ).toBeTruthy();
  });
  it("puts an upstream import error inside the active dialog", async () => {
    const user = await openSample();
    vi.mocked(api.importGithub).mockRejectedValueOnce(
      new Error("This PR is not authored by the selected account."),
    );
    await user.click(screen.getByRole("button", { name: /Import your PRs/ }));
    const dialog = screen.getByRole("dialog");
    await user.type(
      within(dialog).getByRole("textbox", { name: /GitHub account/ }),
      "example",
    );
    await user.type(
      within(dialog).getByRole("textbox", { name: /Pull-request URLs/ }),
      "https://github.com/example/project/pull/7",
    );
    await user.click(
      within(dialog).getByRole("button", { name: /Import public discussions/ }),
    );
    await waitFor(() =>
      expect(within(dialog).getByRole("alert").textContent).toContain(
        "not authored",
      ),
    );
  });
  it("does not apply a late decision save to a new analysis sharing the same card IDs", async () => {
    const user = await openSample();
    let releaseSave: (
      value: Awaited<ReturnType<typeof api.save>>,
    ) => void = () => {};
    vi.mocked(api.save).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          releaseSave = resolve;
        }),
    );
    await user.click(
      screen.getByRole("button", { name: /Mark reviewed locally/ }),
    );
    const next = { ...structuredClone(packet.analysis), id: "new-analysis-id" };
    vi.mocked(api.analyse).mockResolvedValueOnce(next as never);
    await user.click(screen.getByRole("button", { name: /Analyse locally/ }));
    await screen.findByRole("button", { name: /Mark reviewed locally/ });
    await act(async () => {
      releaseSave({
        analysis_id: packet.analysis.id,
        card_id: packet.analysis.cards[0].id,
        state: "reviewed",
        note: "old analysis only",
        updated_at: "2026-10-23T12:00:00Z",
      });
    });
    await waitFor(() =>
      expect(
        screen.queryByRole("button", { name: /Reopen locally/ }),
      ).toBeNull(),
    );
    expect(screen.getByText("Not yet reviewed locally")).toBeTruthy();
  });
});
