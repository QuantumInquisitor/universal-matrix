"""Synthetic endpoint acquisition and shared FIFO delivery; no hardware energy model."""

import heapq
import math
from collections import deque

import numpy as np

from .time_crystal_clock_subsystem import clock_receiver


def _real(value, name):
    if isinstance(value, (bool, np.bool_)) or np.iscomplexobj(value) or np.ndim(value) != 0:
        raise ValueError(f"{name} must be a finite nonnegative real scalar")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite nonnegative real scalar") from error
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be a finite nonnegative real scalar")
    return result


def _integer(value, name, minimum=1):
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        or value < minimum
    ):
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def endpoint_availability(*, cycles, shots, lanes, preparation_periods=0.0, readout_periods=0.0):
    """Request endpoint n at n; independent fresh shots use earliest-free lanes.

    Service per shot is preparation+n+readout drive periods. Equal availability
    chooses the lower lane index. All shots for lower endpoints enter first.
    """
    cycles = _integer(cycles, "cycles", 2)
    shots, lanes = _integer(shots, "shots"), _integer(lanes, "lanes")
    preparation = _real(preparation_periods, "preparation_periods")
    readout = _real(readout_periods, "readout_periods")
    workers = [(0.0, i) for i in range(lanes)]
    heapq.heapify(workers)
    ready = []
    for n in range(cycles + 1):
        last = 0.0
        for _ in range(shots):
            free, lane = heapq.heappop(workers)
            finish = max(float(n), free) + preparation + n + readout
            if not math.isfinite(finish):
                raise ValueError("nonfinite acquisition completion")
            heapq.heappush(workers, (finish, lane))
            last = max(last, finish)
        ready.append(last)
    return ready


def endpoint_resources(*, cycles, shots, qubits, interactions=True):
    cycles = _integer(cycles, "cycles", 2)
    shots, qubits = _integer(shots, "shots"), _integer(qubits, "qubits", 2)
    if not isinstance(interactions, bool):
        raise ValueError("interactions must be boolean")
    periods = shots * cycles * (cycles + 1) // 2
    return dict(
        state_preparations=shots * (cycles + 1),
        floquet_periods=periods,
        single_spin_rotations=2 * qubits * periods,
        interaction_rotations=(qubits - 1) * periods if interactions else 0,
        energy_joules=None,
    )


def timing_delivery(
    signal,
    *,
    ready_times=None,
    receiver_service_periods=0.0,
    competing_jobs=(),
    queue_capacity=None,
    deadline_periods=0.0,
    threshold=0.2,
):
    """Shared FIFO, capacity counts all unfinished jobs including one in service.

    Completions precede arrivals at equal times; competing jobs precede source
    samples at equal arrivals, then input order. No preemption or cancellation.
    Deadlines are inclusive, relative to each source cycle. Late jobs still use
    service but their samples are unavailable to the on-time clock receiver.
    Missing original sample indices break edges; parity never repairs samples.
    """
    try:
        if any(isinstance(x, (bool, np.bool_)) for x in signal):
            raise ValueError("boolean samples are not real measured amplitudes")
    except TypeError as error:
        raise ValueError("signal must be an iterable of real amplitudes") from error
    intrinsic = clock_receiver(signal, threshold=threshold)
    values = np.asarray(signal, dtype=float)
    service = _real(receiver_service_periods, "receiver_service_periods")
    deadline = _real(deadline_periods, "deadline_periods")
    capacity = None if queue_capacity is None else _integer(queue_capacity, "queue_capacity")
    if ready_times is None:
        ready = np.arange(len(values), dtype=float)
    else:
        if (
            np.ndim(ready_times) != 1
            or np.iscomplexobj(ready_times)
            or any(isinstance(x, (bool, np.bool_)) for x in ready_times)
        ):
            raise ValueError("real availability times required")
        ready = np.asarray(ready_times, dtype=float)
    if (
        ready.shape != values.shape
        or not np.isfinite(ready).all()
        or np.any(ready < np.arange(len(values)))
        or np.any(np.diff(ready) < 0)
    ):
        raise ValueError("availability must be finite, ordered and no earlier than source cycle")
    arrivals = []
    try:
        competing_jobs = list(competing_jobs)
    except TypeError as error:
        raise ValueError("competing jobs must be an iterable of pairs") from error
    for index, job in enumerate(competing_jobs):
        if not isinstance(job, (list, tuple, np.ndarray)) or np.ndim(job) != 1 or len(job) != 2:
            raise ValueError("each competing job needs arrival and service")
        arrivals.append((_real(job[0], "arrival"), 0, index, _real(job[1], "service")))
    arrivals.extend((float(t), 1, n, service) for n, t in enumerate(ready))
    arrivals.sort()
    pending = deque()
    last_finish = 0.0
    samples = [None] * len(values)
    jobs = []
    peak = 0
    for arrival, kind, index, duration in arrivals:
        while pending and pending[0] <= arrival:
            pending.popleft()
        accepted = capacity is None or len(pending) < capacity
        finish = None
        if accepted:
            finish = max(arrival, last_finish) + duration
            if not math.isfinite(finish):
                raise ValueError("nonfinite receiver completion")
            last_finish = finish
            if finish > arrival:
                pending.append(finish)
            peak = max(peak, len(pending))
        record = dict(
            kind="source" if kind else "competing",
            index=index,
            arrival_periods=arrival,
            accepted=accepted,
            completion_periods=finish,
        )
        jobs.append(record)
        if kind:
            samples[index] = dict(
                source_cycle=index,
                ready_periods=arrival,
                completion_periods=finish,
                accepted=accepted,
                on_time=accepted and finish <= index + deadline,
                delivery_latency_periods=None if finish is None else finish - index,
            )
    timely = np.array([v if s["on_time"] else 0.0 for v, s in zip(values, samples, strict=True)])
    delivered = clock_receiver(timely, threshold=threshold)
    ticks = [
        dict(
            source_cycle=n,
            completion_periods=samples[n]["completion_periods"],
            latency_periods=samples[n]["delivery_latency_periods"],
        )
        for n in delivered["edge_cycles"]
    ]
    return dict(
        samples=samples,
        jobs=jobs,
        intrinsic_receiver=intrinsic,
        on_time_receiver=delivered,
        delivered_ticks=ticks,
        peak_unfinished_receiver_jobs=peak,
        dropped_source_samples=sum(not s["accepted"] for s in samples),
        late_source_samples=sum(s["accepted"] and not s["on_time"] for s in samples),
        energy_joules=None,
        scope="Synthetic drive-period service contract; no physical sensor backaction, continuous readout, energy or hardware timing advantage established.",
    )
