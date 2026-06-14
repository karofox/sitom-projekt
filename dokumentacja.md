# Statystyka i Teoria Obsługi Masowej - Projekt

Zespół:
- Jakub Jegiełka,
- Karolina Kozubik.

Wydział Matematyki Stosowanej

Informatyka, st. II, sem. I

## Model

### Zjawisko

Modelowanym przez nas zjawiskiem jest system wezwań pogotowia ratunkowego. Przy modelowaniu zjawiska przyjęto następujące założenia:

- Model obsługuje pojedynczą karetkę.
- W przypadku awarii karetki, wezwanie musi zostać obsłużone od samego początku. Naprawa nie dzieje się na miejscu, i karetka musi ponownie jechać do wezwania.
- Wezwania posiadają priorytet, według którego są wybierane.


### Zdarzenia w systemie

Model zakłada cztery możliwe zdarzenia w systemie. Zostały one zaimplementowane w ramach enumeratora `EventType`.

| zdarzenie | opis | rozkład | uzasadnienie |
| --------- | ---- | ------- | ------------ |
| `EventType.Arrival` | 