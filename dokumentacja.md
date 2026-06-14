# Statystyka i Teoria Obsługi Masowej - Projekt

Zespół:
- Jakub Jegiełka,
- Karolina Kozubik.

Wydział Matematyki Stosowanej

Informatyka, st. II, sem. I

## Model

### Zjawisko

Modelowanym przez nas zjawiskiem jest system wezwań pogotowia ratunkowego. Przy modelowaniu zjawiska przyjęto następujące założenia:

- Model może obsługiwać wiele karetek.
- W przypadku awarii karetki, wezwanie musi zostać obsłużone od samego początku. Naprawa nie dzieje się na miejscu, więc kolejna karetka musi ponownie jechać do wezwania.
- Awarie zdarzają się karetkom, które aktualnie obsługują wezwania, chyba że takich nie ma. W takiej sytuacji awaria przydarza się dowolnej karetce bez wezwania.
- Wezwania posiadają priorytet, według którego są wybierane.
- Przyjęta jednostka czasu symulacji to jedna godzina.

### Elementy modelu

Struktury występujące w modelu to:

- harmonogram zdarzeń (lista zdarzeń systemowych (`SystemEvent`) sortowana czasem zdarzenia),
- kolejka oczekujących wezwań (FIFO),
- trajektoria, przechowująca stan systemu w danym czasie (`TrajectoryPoint`, które przechowuje `SystemState` oraz czas).

#### Stan systemu

Przechowuje informacje o dostępnych oraz zepsutych karetkach wraz z kolejką (FIFO) obecnie obsługiwanych wezwań.

### Zdarzenia w systemie

Model zakłada cztery możliwe zdarzenia w systemie. Zostały one zaimplementowane w ramach enumeratora `EventType`.

| zdarzenie | opis | rozkład |
| --------- | ---- | ------- |
| `EventType.Arrival` | Do systemu trafia nowe wezwanie. Wezwanie uzyskuje swój priorytet i trafia do kolejki oczekujących wezwań. Jeśli dostępne są karetki, zaczyna się jego obsługa. | Wykładniczy |
| `EventType.Service` | Wezwanie zostało obsłużone. Jeśli w kolejce oczekujących wezwań znajduje się jakieś wezwanie, zostaje rozpoczęta jego obsługa. | Gamma |
| `EventType.Breakdown` | Karetka uległa awarii. Jeśli obsługiwała wezwanie, trafia ono z powrotem do kolejki oczekujących wezwań. | Wykładniczy |
| `EventType.Repair` | Karetka została naprawiona. Jeśli w kolejce oczekujących wezwań znajduje się jakieś wezwanie, zostaje rozpoczęta jego obsługa. | Gamma |

#### Określenie priorytetu wezwania

Wezwania mogą mieć przypisany jeden z trzech priorytetów (reprezentowanych przez enumerator `Priority`):

- `Priority.Low`, który występuje z prawdopodobieństwem p=0.6,
- `Priority.Medium`, który występuje z prawdopodobieństwem p=0.3,
- `Priority.High`, który występuje z prawdopodobieństwem p=0.1.

#### Rozkłady zdarzeń

Zdarzenia typu `EventType.Arrival` oraz `EventType.Breakdown` korzystają z rozkłady wykładniczego. Wezwania pogotowia ratunkowego lub awarie karetek to procesy Poissona, rzadkie w czasie i niezależne.

Parametr alfa rozkładu wykładniczego można w obu tych przypadkach interpretować jako średnia częstotliwość występowania zdarzenia w jednostce czasu. 

Dla zdarzenia `EventType.Arrival` przyjęto alfa = 0.5, co odpowiada wezwaniom średnio co 2 godziny. Dla `EventType.Breakdown` przyjęto alfa = 0.1, co odpowiada awarii średnio co 10 godzin.

Zdarzenia typu `EventType.Service` oraz `EventType.Repair` korzystają z rozkładu Gamma, który jest uogólnionym rozkładem Erlanga, przeznaczonym do modelowania czasu oczekiwania.

Dla `EventType.Service` przyjęto parametr kształtu rozkładu gamma alfa = 21 oraz parametr skali beta = 0.0259167. Wynika z nich:
- alfa * beta = 0.54, średni czas obsługi wezwania,
- sqrt(alfa) * beta ~ 0,12, odchylenie standardowe czasu obsługi wezwania.

Dla tego typu zdarzenia parametry zostały określone na podstawie reportu GUS "Zdrowie i ochrona Zdrowia w 2024r." (https://stat.gov.pl/obszary-tematyczne/zdrowie/zdrowie/zdrowie-i-ochrona-zdrowia-w-2024-r-,1,15.html) dla danych krajowych dla miast powyżej 10 tys. mieszkańców. Za czas obsługi wezwania uznajemy czas dotarcia karetki (na podstawie raportu) oraz szacowany czas udzielenia pomocy oraz powrotu do szpitala.

Dla `EventType.Repair` przyjęto parametr kształtu rozkładu gamma alfa = 3.0 oraz parametr skali beta = 1.0. Wynika z nich:
- alfa * beta = 3.0, średni czas naprawy karetki,
- sqrt(alfa) * beta ~ 1.73, odchylenie standardowe czasu obsługi wezwana.