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
    async (analysis_id, card_id, state, note, assessment) => ({
      analysis_id,
      card_id,
      state,
      note,
      assessment,
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
  it("opens a fixed mixed example and restores the original example's unsaved decision on return", async () => {
    const user = await openSample();
    await user.type(screen.getByRole("textbox", { name: /Note/ }), "Original example draft");
    await user.selectOptions(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }), "not_a_request");
    const mixed = structuredClone(packet);
    mixed.analysis.id = "synthetic-switch-test-mixed-analysis";
    vi.mocked(api.sample).mockResolvedValueOnce(mixed as never);
    await user.selectOptions(screen.getByRole("combobox", { name: /^Saved example$/ }), "mixed");
    expect(api.sample).toHaveBeenCalledTimes(1);
    await user.click(screen.getByRole("button", { name: /Open saved example/ }));
    await waitFor(() => expect(api.sample).toHaveBeenLastCalledWith("mixed"));
    expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("");
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("unassessed");
    await user.selectOptions(screen.getByRole("combobox", { name: /^Saved example$/ }), "original");
    await user.click(screen.getByRole("button", { name: /Open saved example/ }));
    await waitFor(() => expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("Original example draft"));
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("not_a_request");
    expect(api.analyse).not.toHaveBeenCalled();
    expect(api.save).not.toHaveBeenCalled();
  });
  it("records disagreement explicitly without changing review state, hiding evidence or rewriting the model", async () => {
    const user = await openSample();
    const originalRationale = packet.analysis.cards[0].rationale;
    const explanation = screen.getByText("Unverified model explanation").closest("details")!;
    expect(explanation.open).toBe(false);
    expect(explanation.textContent).toContain(originalRationale);
    const assessment = screen.getByRole("combobox", { name: /Assessment of this model suggestion/ });
    await user.selectOptions(assessment, "reply_not_relevant");
    expect(api.save).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await screen.findByText("Saved locally. GitHub was not changed.");
    expect(api.save).toHaveBeenLastCalledWith(packet.analysis.id, packet.analysis.cards[0].id, "open", "", "reply_not_relevant");
    expect(screen.getByText("Not yet reviewed locally")).toBeTruthy();
    expect(explanation.textContent).toContain(originalRationale);
    await user.click(screen.getByRole("button", { name: /Mark reviewed locally/ }));
    await screen.findByRole("button", { name: /Reopen locally/ });
    expect(api.save).toHaveBeenLastCalledWith(packet.analysis.id, packet.analysis.cards[0].id, "reviewed", "", "reply_not_relevant");
    await user.selectOptions(assessment, "unassessed");
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await waitFor(() => expect(api.save).toHaveBeenLastCalledWith(packet.analysis.id, packet.analysis.cards[0].id, "reviewed", "", "unassessed"));
  });
  it("keeps a failed assessment and note together when changing cards or opening Sources", async () => {
    const user = await openSample();
    const firstCard = packet.analysis.cards[0];
    await user.type(screen.getByRole("textbox", { name: /Note/ }), "This is a status update, not a demand");
    await user.selectOptions(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }), "not_a_request");
    vi.mocked(api.save).mockRejectedValueOnce(new Error("Disk write failed"));
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await screen.findByText(/Not saved. Your note and assessment remain here/);
    const cards = within(screen.getByRole("region", { name: "Review request list" })).getAllByRole("button");
    await user.click(cards[1]);
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("unassessed");
    expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("");
    await user.click(cards[0]);
    await user.click(screen.getByRole("button", { name: /^Sources / }));
    await user.click(screen.getByRole("button", { name: /^Review queue/ }));
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("not_a_request");
    expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("This is a status update, not a demand");
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await waitFor(() => expect(api.save).toHaveBeenLastCalledWith(packet.analysis.id, firstCard.id, "open", "This is a status update, not a demand", "not_a_request"));
  });
  it("does not offer reply disagreement without a response or model controls in baseline mode", async () => {
    const changed = structuredClone(packet);
    changed.analysis.cards[0].response = null as never;
    changed.analysis.cards[0].interpretation = "follow_up";
    vi.mocked(api.sample).mockResolvedValueOnce(changed as never);
    const user = await openSample();
    expect(screen.queryByRole("option", { name: "Reply not relevant" })).toBeNull();
    const baseline = { ...changed.analysis, id: "baseline-run", mode: "baseline", model: null };
    vi.mocked(api.analyse).mockResolvedValueOnce(baseline as never);
    await user.click(screen.getByRole("button", { name: /Chronology baseline/ }));
    await waitFor(() => expect(screen.queryByRole("combobox", { name: /Assessment of this model suggestion/ })).toBeNull());
  });
  it("does not apply an in-flight card assessment to another selected card", async () => {
    const user = await openSample();
    let finish: (value: Awaited<ReturnType<typeof api.save>>) => void = () => {};
    vi.mocked(api.save).mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    await user.selectOptions(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }), "not_a_request");
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    expect(screen.getByRole("textbox", { name: /Note/ }).hasAttribute("disabled")).toBe(true);
    const cards = within(screen.getByRole("region", { name: "Review request list" })).getAllByRole("button");
    await user.click(cards[1]);
    await user.type(screen.getByRole("textbox", { name: /Note/ }), "Second card draft");
    await act(async () => finish({
      analysis_id: packet.analysis.id,
      card_id: packet.analysis.cards[0].id,
      state: "open",
      assessment: "not_a_request",
      note: "",
      updated_at: "2026-10-24T10:00:00Z",
    }));
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("unassessed");
    expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("Second card draft");
    await user.click(cards[0]);
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("not_a_request");
    expect(screen.getByRole("button", { name: /Save decision/ }).hasAttribute("disabled")).toBe(true);
  });
  it("keeps one save per analysis and card pending across A to B to A remounts", async () => {
    const user = await openSample();
    let finish: (value: Awaited<ReturnType<typeof api.save>>) => void = () => {};
    vi.mocked(api.save).mockImplementationOnce(
      () => new Promise((resolve) => { finish = resolve; }),
    );
    await user.type(screen.getByRole("textbox", { name: /Note/ }), "A decision awaiting storage");
    await user.selectOptions(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }), "not_a_request");
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    const cards = within(screen.getByRole("region", { name: "Review request list" })).getAllByRole("button");
    await user.click(cards[1]);
    await user.type(screen.getByRole("textbox", { name: /Note/ }), "B draft is independent");
    await user.click(cards[0]);
    expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("A decision awaiting storage");
    expect(screen.getByRole("textbox", { name: /Note/ }).hasAttribute("disabled")).toBe(true);
    expect(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }).hasAttribute("disabled")).toBe(true);
    expect(screen.getByRole("button", { name: /Save decision/ }).hasAttribute("disabled")).toBe(true);
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    expect(api.save).toHaveBeenCalledTimes(1);
    await user.click(screen.getByRole("button", { name: /^Sources / }));
    await user.click(screen.getByRole("button", { name: /^Review queue/ }));
    expect(screen.getByRole("button", { name: /Save decision/ }).hasAttribute("disabled")).toBe(true);
    await act(async () => finish({
      analysis_id: packet.analysis.id,
      card_id: packet.analysis.cards[0].id,
      state: "open",
      assessment: "not_a_request",
      note: "A decision awaiting storage",
      updated_at: "2026-10-24T10:00:00Z",
    }));
    await waitFor(() => expect(screen.getByRole("textbox", { name: /Note/ }).hasAttribute("disabled")).toBe(false));
    expect(screen.getByRole("button", { name: /Save decision/ }).hasAttribute("disabled")).toBe(true);
    const newCards = within(screen.getByRole("region", { name: "Review request list" })).getAllByRole("button");
    await user.click(newCards[1]);
    expect((screen.getByRole("textbox", { name: /Note/ }) as HTMLTextAreaElement).value).toBe("B draft is independent");
    expect(api.save).toHaveBeenCalledTimes(1);
  });
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
      "unassessed",
    );
    await user.click(screen.getByRole("button", { name: /Reopen locally/ }));
    await screen.findByRole("button", { name: /Mark reviewed locally/ });
    expect(api.save).toHaveBeenLastCalledWith(
      packet.analysis.id,
      expect.any(String),
      "open",
      "",
      "unassessed",
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
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await screen.findByText(/Not saved. Your note and assessment remain here/);
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
    await user.selectOptions(screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }), "not_a_request");
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
        assessment: "not_a_request",
        updated_at: "2026-10-23T12:00:00Z",
      });
    });
    await waitFor(() =>
      expect(
        screen.queryByRole("button", { name: /Reopen locally/ }),
      ).toBeNull(),
    );
    expect(screen.getByText("Not yet reviewed locally")).toBeTruthy();
    expect((screen.getByRole("combobox", { name: /Assessment of this model suggestion/ }) as HTMLSelectElement).value).toBe("unassessed");
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
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
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
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await screen.findByText("Saved locally. GitHub was not changed.");
    expect(api.save).toHaveBeenLastCalledWith(
      packet.analysis.id,
      expect.any(String),
      "open",
      "Keep my review context",
      "unassessed",
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
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
    await screen.findByText(/Not saved. Your note and assessment remain here/);
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
    await user.click(screen.getByRole("button", { name: /Save decision/ }));
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
