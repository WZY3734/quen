from __future__ import annotations

import os
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

_matplotlib_cache = Path(tempfile.gettempdir()) / "queenquest-matplotlib"
_matplotlib_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_matplotlib_cache))
os.environ.setdefault("XDG_CACHE_HOME", str(_matplotlib_cache))

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from queenquest.tracing import ALGORITHMS, SearchTrace, TraceFrame, TraceSettings, build_trace
from queenquest.problem import NQueensProblem


class QueenQuestApp(tk.Tk):
    """Interactive desktop application for exploring N-Queens solvers."""

    def __init__(self) -> None:
        super().__init__()
        self.title("QueenQuest")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.trace: SearchTrace | None = None
        self.frame_index = 0
        self.is_playing = False
        self.play_job: str | None = None

        self._create_variables()
        self._create_layout()
        self._create_trace()

    def _create_variables(self) -> None:
        self.algorithm_var = tk.StringVar(value="Backtracking")
        self.size_var = tk.IntVar(value=8)
        self.speed_var = tk.IntVar(value=120)
        self.max_steps_var = tk.IntVar(value=2_000)
        self.restarts_var = tk.IntVar(value=20)
        self.population_var = tk.IntVar(value=80)
        self.generations_var = tk.IntVar(value=300)
        self.mutation_var = tk.DoubleVar(value=0.2)
        self.temperature_var = tk.DoubleVar(value=5.0)
        self.cooling_var = tk.DoubleVar(value=0.995)
        self.seed_var = tk.StringVar(value="7")

    def _create_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        controls = ttk.Frame(self, padding=16)
        controls.grid(row=0, column=0, sticky="ns")
        controls.columnconfigure(1, weight=1)

        workspace = ttk.Frame(self, padding=(0, 16, 16, 16))
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(0, weight=1)

        self._create_controls(controls)
        self._create_canvas(workspace)
        self._create_timeline(workspace)

    def _create_controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="QueenQuest", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        row = 1
        ttk.Label(parent, text="Algorithm").grid(row=row, column=0, sticky="w")
        algorithm = ttk.Combobox(
            parent,
            textvariable=self.algorithm_var,
            values=ALGORITHMS,
            state="readonly",
            width=22,
        )
        algorithm.grid(row=row, column=1, sticky="ew", pady=4)
        algorithm.bind("<<ComboboxSelected>>", lambda _event: self._create_trace())

        row += 1
        ttk.Label(parent, text="Board size").grid(row=row, column=0, sticky="w")
        ttk.Spinbox(
            parent,
            from_=4,
            to=14,
            textvariable=self.size_var,
            command=self._create_trace,
            width=8,
        ).grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        ttk.Label(parent, text="Speed (ms)").grid(row=row, column=0, sticky="w")
        ttk.Scale(parent, from_=30, to=800, variable=self.speed_var, orient="horizontal").grid(
            row=row, column=1, sticky="ew", pady=4
        )

        row += 1
        ttk.Separator(parent).grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)

        row = self._add_spinbox(parent, row + 1, "Max steps", self.max_steps_var, 100, 50_000)
        row = self._add_spinbox(parent, row, "Restarts", self.restarts_var, 1, 200)
        row = self._add_spinbox(parent, row, "Population", self.population_var, 10, 500)
        row = self._add_spinbox(parent, row, "Generations", self.generations_var, 10, 5_000)
        row = self._add_entry(parent, row, "Mutation rate", self.mutation_var)
        row = self._add_entry(parent, row, "Temperature", self.temperature_var)
        row = self._add_entry(parent, row, "Cooling rate", self.cooling_var)
        row = self._add_entry(parent, row, "Seed", self.seed_var)

        ttk.Button(parent, text="Build Trace", command=self._create_trace).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(14, 6)
        )
        row += 1
        ttk.Button(parent, text="Open Final Board", command=self._open_final_board).grid(
            row=row, column=0, columnspan=2, sticky="ew"
        )

        row += 1
        self.summary_var = tk.StringVar(value="")
        ttk.Label(parent, textvariable=self.summary_var, wraplength=260, justify="left").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(16, 0)
        )

    def _add_spinbox(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.IntVar,
        lower: int,
        upper: int,
    ) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        ttk.Spinbox(parent, from_=lower, to=upper, textvariable=variable, width=8).grid(
            row=row, column=1, sticky="ew", pady=4
        )
        return row + 1

    def _add_entry(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.Variable,
    ) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        ttk.Entry(parent, textvariable=variable, width=10).grid(row=row, column=1, sticky="ew", pady=4)
        return row + 1

    def _create_canvas(self, parent: ttk.Frame) -> None:
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.board_ax = self.figure.add_subplot(1, 2, 1)
        self.info_ax = self.figure.add_subplot(1, 2, 2)
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _create_timeline(self, parent: ttk.Frame) -> None:
        timeline = ttk.Frame(parent)
        timeline.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        timeline.columnconfigure(5, weight=1)

        ttk.Button(timeline, text="|<", command=self._first_frame, width=4).grid(row=0, column=0)
        ttk.Button(timeline, text="<", command=self._previous_frame, width=4).grid(row=0, column=1)
        self.play_button = ttk.Button(timeline, text="Play", command=self._toggle_playback, width=8)
        self.play_button.grid(row=0, column=2, padx=4)
        ttk.Button(timeline, text=">", command=self._next_frame, width=4).grid(row=0, column=3)
        ttk.Button(timeline, text=">|", command=self._last_frame, width=4).grid(row=0, column=4)

        self.progress_var = tk.IntVar(value=0)
        self.progress = ttk.Scale(
            timeline,
            from_=0,
            to=0,
            variable=self.progress_var,
            orient="horizontal",
            command=self._seek,
        )
        self.progress.grid(row=0, column=5, sticky="ew", padx=10)

        self.frame_label_var = tk.StringVar(value="0 / 0")
        ttk.Label(timeline, textvariable=self.frame_label_var, width=12).grid(row=0, column=6)

    def _settings(self) -> TraceSettings:
        seed_text = self.seed_var.get().strip()
        seed = int(seed_text) if seed_text else None

        return TraceSettings(
            board_size=self.size_var.get(),
            algorithm=self.algorithm_var.get(),
            max_steps=self.max_steps_var.get(),
            restarts=self.restarts_var.get(),
            population_size=self.population_var.get(),
            generations=self.generations_var.get(),
            mutation_rate=self.mutation_var.get(),
            initial_temperature=self.temperature_var.get(),
            cooling_rate=self.cooling_var.get(),
            seed=seed,
        )

    def _create_trace(self) -> None:
        self._pause()
        try:
            self.trace = build_trace(self._settings())
        except Exception as exc:
            messagebox.showerror("Unable to build trace", str(exc))
            return

        self.frame_index = 0
        max_index = max(len(self.trace.frames) - 1, 0)
        self.progress.configure(to=max_index)
        self.progress_var.set(0)
        self.summary_var.set(
            f"{self.trace.algorithm}\n"
            f"Frames: {len(self.trace.frames)}\n"
            f"Solutions: {len(self.trace.solutions)}"
        )
        self._draw_current_frame()

    def _draw_current_frame(self) -> None:
        if self.trace is None:
            return

        frame = self.trace.frames[self.frame_index]
        self._draw_board(frame)
        self._draw_info(frame)
        self.progress_var.set(self.frame_index)
        self.frame_label_var.set(f"{self.frame_index + 1} / {len(self.trace.frames)}")
        self.canvas.draw_idle()

    def _draw_board(self, frame: TraceFrame) -> None:
        assert self.trace is not None
        size = self.trace.board_size
        self.board_ax.clear()
        self.board_ax.set_title(self.trace.algorithm)
        self.board_ax.set_xlim(0, size)
        self.board_ax.set_ylim(0, size)
        self.board_ax.set_aspect("equal")
        self.board_ax.invert_yaxis()
        self.board_ax.set_xticks([])
        self.board_ax.set_yticks([])

        for row in range(size):
            for col in range(size):
                color = "#f2d8a7" if (row + col) % 2 == 0 else "#8f5f3c"
                self.board_ax.add_patch(
                    Rectangle((col, row), 1, 1, facecolor=color, edgecolor="#3f2f24")
                )

        if frame.active is not None:
            col, row = frame.active
            self.board_ax.add_patch(
                Rectangle((col, row), 1, 1, facecolor="#60a5fa", alpha=0.58, linewidth=2)
            )

        for col, row in frame.conflicts:
            self.board_ax.add_patch(
                Rectangle((col, row), 1, 1, facecolor="#ef4444", alpha=0.58, linewidth=2)
            )

        for col, row in enumerate(frame.board):
            if row < 0:
                continue
            color = "#047857" if frame.is_solution else "#111827"
            self.board_ax.text(
                col + 0.5,
                row + 0.5,
                "Q",
                ha="center",
                va="center",
                fontsize=24,
                color=color,
                fontweight="bold",
            )

    def _draw_info(self, frame: TraceFrame) -> None:
        self.info_ax.clear()
        self.info_ax.axis("off")
        metrics = [f"{key}: {value}" for key, value in frame.metrics.items()]
        lines = [
            frame.phase.upper(),
            "",
            frame.message,
            "",
            f"Attempts: {frame.attempts}",
            *metrics,
            "",
            "Controls:",
            "Play/Pause: auto replay",
            "< and >: step one frame",
            "Slider: jump to any frame",
            "",
            "Legend:",
            "Blue: active candidate",
            "Red: conflict",
            "Green Q: solution",
        ]
        self.info_ax.text(
            0.02,
            0.98,
            "\n".join(lines),
            va="top",
            fontsize=11,
            family="monospace",
            bbox={"facecolor": "#f9fafb", "edgecolor": "#d1d5db", "boxstyle": "round,pad=0.7"},
        )

    def _toggle_playback(self) -> None:
        if self.is_playing:
            self._pause()
        else:
            self.is_playing = True
            self.play_button.configure(text="Pause")
            self._schedule_next_frame()

    def _pause(self) -> None:
        self.is_playing = False
        if hasattr(self, "play_button"):
            self.play_button.configure(text="Play")
        if self.play_job is not None:
            self.after_cancel(self.play_job)
            self.play_job = None

    def _schedule_next_frame(self) -> None:
        if not self.is_playing:
            return
        self.play_job = self.after(self.speed_var.get(), self._play_tick)

    def _play_tick(self) -> None:
        if self.trace is None:
            self._pause()
            return
        if self.frame_index >= len(self.trace.frames) - 1:
            self._pause()
            return
        self.frame_index += 1
        self._draw_current_frame()
        self._schedule_next_frame()

    def _seek(self, value: str) -> None:
        if self.trace is None:
            return
        self.frame_index = max(0, min(int(float(value)), len(self.trace.frames) - 1))
        self._draw_current_frame()

    def _first_frame(self) -> None:
        self._pause()
        self.frame_index = 0
        self._draw_current_frame()

    def _last_frame(self) -> None:
        self._pause()
        if self.trace is not None:
            self.frame_index = len(self.trace.frames) - 1
            self._draw_current_frame()

    def _previous_frame(self) -> None:
        self._pause()
        self.frame_index = max(0, self.frame_index - 1)
        self._draw_current_frame()

    def _next_frame(self) -> None:
        self._pause()
        if self.trace is not None:
            self.frame_index = min(len(self.trace.frames) - 1, self.frame_index + 1)
            self._draw_current_frame()

    def _open_final_board(self) -> None:
        if self.trace is None or not self.trace.solutions:
            messagebox.showinfo("No solution", "This trace has not found a solution.")
            return
        from queenquest.visualizer import show_solution

        show_solution(
            problem=NQueensProblem(self.trace.board_size),
            solution=self.trace.solutions[0],
            title=f"{self.trace.algorithm} solution",
        )


def main() -> None:
    app = QueenQuestApp()
    app.mainloop()


if __name__ == "__main__":
    main()
