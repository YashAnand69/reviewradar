// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  act,
  cleanup,
  fireEvent,
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
    health: vi.fn(),
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
  vi.mocked(api.health).mockResolvedValue({
    status: "ok",
    version: "test",
    model_configured: true,
    model_ready: true,
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
  it("warns when the current request wording was edited after a possible reply", async () => {
    const changed = structuredClone(packet);
    const first = changed.analysis.cards[0];
    const source = changed.snapshot.prs.find((pr) => pr.id === first.pr_id)!;
    source.comments.find((c) => c.id === first.request.comment_id)!.updated_at =
      "2026-10-22T12:00:00Z";
    vi.mocked(api.sample).mockResolvedValueOnce(changed as never);
    await openSample();
    expect(
      screen.getByText("The request was edited after this reply"),
    ).toBeTruthy();
  });
  it("orders source entries by their actual instants across timezone offsets", async () => {
    const changed = structuredClone(packet);
    const [request, response] = changed.snapshot.prs[0].comments;
    request.created_at = request.updated_at = "2026-10-23T09:30:00+05:30";
    response.created_at = response.updated_at = "2026-10-23T05:00:00Z";
    vi.mocked(api.sample).mockResolvedValueOnce(changed as never);
    const user = await openSample();
    await user.click(screen.getByRole("button", { name: /^Sources / }));
    const sourcePr = screen
      .getByRole("link", { name: /fossasia\/eventyay#6104/ })
      .closest("section")!;
    expect(
      Array.from(sourcePr.querySelectorAll("time"), (time) =>
        time.getAttribute("datetime"),
      ),
    ).toEqual([request.created_at, response.created_at]);
  });
  it("keeps mobile focus on the next evidence when the reviewed card is filtered out", async () => {
    vi.mocked(window.matchMedia).mockReturnValue({
      matches: true,
    } as MediaQueryList);
    const user = await openSample();
    await user.click(
      screen.getByRole("checkbox", { name: /Include reviewed locally/ }),
    );
    const requestList = screen.getByRole("region", {
      name: "Review request list",
    });
    await user.click(within(requestList).getAllByRole("button")[0]);
    const oldHeading = within(
      screen.getByRole("region", { name: "Selected evidence" }),
    ).getByRole("heading", { level: 2 });
    expect(document.activeElement).toBe(oldHeading);
    await user.click(
      screen.getByRole("button", { name: /Mark reviewed locally/ }),
    );
    await waitFor(() => {
      const nextHeading = within(
        screen.getByRole("region", { name: "Selected evidence" }),
      ).getByRole("heading", { level: 2 });
      expect(nextHeading).not.toBe(oldHeading);
      expect(document.activeElement).toBe(nextHeading);
    });
  });
  it("returns focus to Saved analyses after dismissing its asynchronously loaded dialog", async () => {
    const user = await openSample();
    let finishLoading: (value: []) => void = () => {};
    vi.mocked(api.history).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finishLoading = resolve;
        }),
    );
    const opener = screen.getByRole("button", { name: /Saved analyses/ });
    await user.click(opener);
    const dialog = screen.getByRole("dialog");
    expect(opener.hasAttribute("disabled")).toBe(true);
    await act(async () => finishLoading([]));
    const close = within(dialog).getByRole("button", { name: /Close dialog/ });
    await waitFor(() => expect(close.hasAttribute("disabled")).toBe(false));
    close.focus();
    fireEvent(dialog, new Event("cancel", { cancelable: true }));
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(document.activeElement).toBe(opener);
  });
  it("disconnects after a failed save and reconnects without losing the draft or evidence", async () => {
    const user = await openSample();
    const failure = new Error(
      "The local server is offline. Your typed notes remain. Start ReviewRadar, then choose Retry connection.",
    );
    failure.name = "LocalConnectionError";
    vi.mocked(api.save).mockRejectedValueOnce(failure);
    await user.type(
      screen.getByRole("textbox", { name: /Note/ }),
      "Keep my review context",
    );
    await user.click(screen.getByRole("button", { name: /Save note/ }));
    await screen.findByText("Local connection needed");
    expect(
      (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
        .value,
    ).toBe("Keep my review context");
    expect(
      screen
        .getByRole("button", { name: /Analyse locally/ })
        .hasAttribute("disabled"),
    ).toBe(true);
    await user.click(screen.getByRole("button", { name: /Retry connection/ }));
    await screen.findByText("Local workspace");
    expect(
      (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
        .value,
    ).toBe("Keep my review context");
    expect(api.sample).toHaveBeenCalledTimes(1);
    await user.click(screen.getByRole("button", { name: /Save note/ }));
    await screen.findByText("Saved locally. GitHub was not changed.");
    expect(api.save).toHaveBeenLastCalledWith(
      packet.analysis.id,
      expect.any(String),
      "open",
      "Keep my review context",
    );
  });
  it("checks connectivity when the tab returns without polling or clearing the workbench", async () => {
    await openSample();
    const failure = new Error("The local server stopped. Retry connection.");
    failure.name = "LocalConnectionError";
    vi.mocked(api.health).mockRejectedValueOnce(failure);
    fireEvent(window, new Event("focus"));
    await screen.findByText("Local connection needed");
    expect(screen.getByRole("textbox", { name: /Note/ })).toBeTruthy();
    expect(api.health).toHaveBeenCalledTimes(1);
    fireEvent(window, new Event("focus"));
    await screen.findByText("Local workspace");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(
      screen.getByText(
        /Connection restored. Your evidence and notes were kept/,
      ),
    ).toBeTruthy();
    expect(api.sample).toHaveBeenCalledTimes(1);
  });
  it("offers the working baseline when configuration exists but the model is offline", async () => {
    vi.mocked(api.connect).mockResolvedValueOnce({
      status: "ok",
      version: "test",
      model_configured: true,
      model_ready: false,
      model_reason: "Start the model service and check again.",
      github_available: true,
      mode: "local",
    });
    await openSample();
    expect(screen.getByText("Local model is offline")).toBeTruthy();
    expect(
      screen
        .getByRole("button", { name: /Analyse locally/ })
        .hasAttribute("disabled"),
    ).toBe(true);
    expect(
      screen
        .getByRole("button", { name: /Chronology baseline/ })
        .hasAttribute("disabled"),
    ).toBe(false);
    expect(
      screen.getByRole("button", { name: /Check connection/ }),
    ).toBeTruthy();
  });
  it("clears a recovered connection failure inside the open import dialog", async () => {
    const user = await openSample();
    const failure = new Error("The local server stopped. Retry connection.");
    failure.name = "LocalConnectionError";
    vi.mocked(api.importGithub).mockRejectedValueOnce(failure);
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
        "server stopped",
      ),
    );
    fireEvent(window, new Event("focus"));
    await waitFor(() => expect(within(dialog).queryByRole("alert")).toBeNull());
    expect(
      (
        within(dialog).getByRole("textbox", {
          name: /GitHub account/,
        }) as HTMLInputElement
      ).value,
    ).toBe("example");
    expect(
      screen.queryByText("Reconnect without losing your place"),
    ).toBeNull();
  });
  it("preserves an unrelated save error when the connection is restored", async () => {
    const user = await openSample();
    const failure = new Error("The local server stopped. Retry connection.");
    failure.name = "LocalConnectionError";
    vi.mocked(api.health).mockRejectedValueOnce(failure);
    fireEvent(window, new Event("focus"));
    await screen.findByText("Local connection needed");
    vi.mocked(api.save).mockRejectedValueOnce(
      new Error("The local note could not be stored."),
    );
    await user.type(
      screen.getByRole("textbox", { name: /Note/ }),
      "Keep my next step",
    );
    await user.click(screen.getByRole("button", { name: /Save note/ }));
    await screen.findByText(/Not saved. Your note remains here/);
    fireEvent(window, new Event("focus"));
    await screen.findByText("Local workspace");
    expect(screen.getByRole("alert").textContent).toContain(
      "note could not be stored",
    );
    expect(
      (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
        .value,
    ).toBe("Keep my next step");
  });
  it("keeps Retry connection available after dismissing the error and preserves the draft", async () => {
    const user = await openSample();
    const failure = new Error("The local server stopped. Retry connection.");
    failure.name = "LocalConnectionError";
    vi.mocked(api.save).mockRejectedValueOnce(failure);
    await user.type(
      screen.getByRole("textbox", { name: /Note/ }),
      "Do not lose this draft",
    );
    await user.click(screen.getByRole("button", { name: /Save note/ }));
    await screen.findByText("Local connection needed");
    await user.click(screen.getByRole("button", { name: /Dismiss error/ }));
    expect(screen.queryByRole("alert")).toBeNull();
    await user.click(screen.getByRole("button", { name: /Retry connection/ }));
    await screen.findByText("Local workspace");
    expect(
      (screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement)
        .value,
    ).toBe("Do not lose this draft");
    expect(api.sample).toHaveBeenCalledTimes(1);
  });
});
