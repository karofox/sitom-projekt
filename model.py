"""
Model kolejkowy systemu obłsugi wezwań dla pogotowia ratunkowego.

Statystyka i Teoria Obsługi Masowej,
Wydział Matematyki Stosowanej,
Informatyka, st. II, sem. I

Jakub Jagiełka
Karolina Kozubik
"""

from dataclasses import dataclass, field
import enum
from typing import Callable
import random


class EventType(enum.Enum):
    """Rodzaje zdarzeń możliwe do wystąpienia w systemie"""

    Arrival = enum.auto()  # przyjęcie nowego wezwania, karetka wyrusza w drogę
    Service = enum.auto()  # zakończenie obługi wezwania, karetka staje się dostępna
    Breakdown = enum.auto()  # karetka ulega awarii
    Repair = enum.auto()  # karetka zostaje naprawiona


class Priority(enum.Enum):
    """Możliwe priorytety wezwań."""

    Low = 1
    Medium = 2
    High = 3


@dataclass
class SystemEvent:
    """Zdarzenie w systemie."""

    event: EventType
    time: float


@dataclass
class Call:
    """Wezwanie karetki."""

    priority: Priority
    arrival_tieme: float


@dataclass
class SystemState:
    """Stan systemu, przechowuje charakterystyki w danym czasie."""

    available_servers: int = 0  # dostępne karetki
    broken_servers: int = 0  # zepsute karetki
    current_calls: list[Call] = field(default_factory=list)

    @property
    def clients(self) -> int:
        return len(self.current_calls)


@dataclass
class TrajectoryPoint:
    """Punkt w trajektorii systemu. Przechowuje charakterystki, które można poddać analizie."""

    time: float
    state: SystemState


class EmergencyServiceSystemSim:
    def __init__(
        self,
        arrival_time_fn: Callable[[], float],
        service_time_fn: Callable[[], float],
        breakdown_time_fn: Callable[[], float],
        repair_time_fn: Callable[[], float],
        servers: int = 2,
    ) -> None:
        self._arrival_time_fn = arrival_time_fn
        self._service_time_fn = service_time_fn
        self._breakdown_time_fn = breakdown_time_fn
        self._repair_time_fn = repair_time_fn

        self._trajectory: list[TrajectoryPoint] = [
            TrajectoryPoint(
                time=0.0,
                state=SystemState(
                    available_servers=servers,
                    broken_servers=0,
                ),
            )
        ]
        self._event_schedule: list[SystemEvent] = []
        self._queue: list[Call] = []

    @property
    def current_state(self) -> SystemState:
        return self._trajectory[-1].state

    @property
    def current_time(self) -> float:
        return self._trajectory[-1].time

    @property
    def trajectory(self) -> list[TrajectoryPoint]:
        return self._trajectory

    def step(self) -> None:
        self.__update_schedule()
        self.__update_trajectory()

    def __update_schedule(self) -> None:
        """
        Uzupełnienie harmonogram zdarzeń.
        Nowe zdarzenia są dodawane, pod warunkiem, że mogą wystąpić.
        Jeśli zdarzenie danego typu jest już obecne w harmonogramie, nie pojawi się.
        """

        # Nowe wezwanie
        if not any(e.event == EventType.Arrival for e in self._event_schedule):
            new_time = self.__generate_new_event_time(EventType.Arrival)
            self._event_schedule.append(
                SystemEvent(event=EventType.Arrival, time=new_time)
            )

        # Zakończenie obsługi (tylko jeśli jakieś wezwanie jest obsługiwane)
        if self.current_state.clients > 0 and not any(
            e.event == EventType.Service for e in self._event_schedule
        ):
            new_time = self.__generate_new_event_time(EventType.Service)
            self._event_schedule.append(
                SystemEvent(event=EventType.Service, time=new_time)
            )

        # Awaria (tylko jeśli nie wszystkie karetki są zepsute)
        if self.current_state.available_servers > 0 and not any(
            e.event == EventType.Breakdown for e in self._event_schedule
        ):
            new_time = self.__generate_new_event_time(EventType.Breakdown)
            self._event_schedule.append(
                SystemEvent(event=EventType.Breakdown, time=new_time)
            )

        # Naprawa (tylko jeśli mamy zepsute karetki)
        if self.current_state.broken_servers > 0 and not any(
            e.event == EventType.Repair for e in self._event_schedule
        ):
            new_time = self.__generate_new_event_time(EventType.Repair)
            self._event_schedule.append(
                SystemEvent(event=EventType.Repair, time=new_time)
            )

        # Sortowanie harmonogramu po czasie
        self._event_schedule.sort(key=lambda e: e.time)

    def __generate_new_event_time(self, event_type: EventType) -> float:
        random_time = 0.0
        match event_type:
            case EventType.Arrival:
                random_time = self._arrival_time_fn()
            case EventType.Service:
                random_time = self._service_time_fn()
            case EventType.Breakdown:
                random_time = self._breakdown_time_fn()
            case EventType.Repair:
                random_time = self._repair_time_fn()

        return self.current_time + random_time

    def __update_trajectory(self) -> None:
        """
        Obsługa obecnego zdarzenia i zaktualizowanie stanu systemu.
        """
        current_event = self._event_schedule.pop(0)
        new_state = self.current_state

        match current_event.event:
            case EventType.Arrival:
                call = Call(
                    priority=random.choices(
                        [Priority.Low, Priority.Medium, Priority.High],
                        weights=[0.6, 0.3, 0.1],
                    )[0],
                    arrival_tieme=current_event.time,
                )
                self.__add_call_to_queue(call)

                if self.current_state.available_servers > 0:
                    new_state.current_calls.append(self._queue.pop(0))
                    new_state.available_servers -= 1

            case EventType.Service:
                new_state.available_servers += 1
                new_state.current_calls.pop(0)

                if self._queue:
                    new_state.current_calls.append(self._queue.pop(0))
                    new_state.available_servers -= 1

            case EventType.Breakdown:
                new_state.broken_servers += 1

                if self.current_state.clients > 0:
                    current_call = new_state.current_calls.pop(0)
                    self.__add_call_to_queue(current_call)  # type: ignore
                else:
                    new_state.available_servers -= 1

            case EventType.Repair:
                new_state.available_servers += 1
                new_state.broken_servers -= 1

                if self._queue:
                    new_state.current_calls.append(self._queue.pop(0))
                    new_state.available_servers -= 1

        self._trajectory.append(TrajectoryPoint(current_event.time, new_state))
        print(current_event)
        print(self.current_state)
        print(self._queue)
        print()

    def __add_call_to_queue(self, call: Call) -> None:
        self._queue.append(call)
        self._queue.sort(key=lambda c: c.priority.value, reverse=True)


if __name__ == "__main__":
    sim = EmergencyServiceSystemSim(
        lambda: random.expovariate(0.5),
        lambda: random.gammavariate(2.0, 1.5),
        lambda: random.expovariate(0.1),
        lambda: random.gammavariate(3.0, 1.0),
        servers=3,
    )

    print("Running Emergency Service System Simulation...\n")
    for _ in range(15):
        sim.step()

    print(f"{'Event Time':<15} | {'Clients'} | {'Available'} | {'Broken'}")
    print("-" * 50)
    for point in sim.trajectory:
        print(
            f"{point.time:<15.3f} | {point.state.clients:<7} | {point.state.available_servers:<9} | {point.state.broken_servers}"
        )
