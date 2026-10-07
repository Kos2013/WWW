from datetime import datetime, timedelta

class Airport:
    def __init__(self, code: str, name: str, city: str):
        self.code = code.upper()  # Например, "SVO"
        self.name = name
        self.city = city

    def __repr__(self):
        return f"{self.city} ({self.code})"


class Flight:
    def __init__(self, flight_number: str, origin: Airport, destination: Airport, 
                 departure_time: datetime, duration_minutes: int, extra_services: dict = None):
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.duration = timedelta(minutes=duration_minutes)
        
        self.extra_services = extra_services if extra_services else {"meal": True, "extra_baggage": False}
       
        self.seats = {} 

    def set_seat_configuration(self, config: dict):
        """
        Устанавливает конфигурацию мест. 
        Принимает словарь вида: {"business": (ряды_от, ряды_до, мест_в_ряду), "economy": ...}
        Пример: {"business": (1, 2, 4), "economy": (3, 10, 6)}
        Буквы мест генерируются автоматически (A, B, C, D...)
        """
        letters = "ABCDEFGH"
        for seat_class, (start_row, end_row, seats_per_row) in config.items():
            self.seats[seat_class] = []
            for row in range(start_row, end_row + 1):
                for seat_idx in range(seats_per_row):
                    letter = letters[seat_idx]
                    self.seats[seat_class].append([str(row), letter, False])

    def get_free_seats_count(self, seat_class: str) -> int:
        if seat_class not in self.seats:
            return 0
        return sum(1 for seat in self.seats[seat_class] if not seat[2])

    def book_seat(self, seat_class: str, row: str, letter: str) -> bool:
        """Бронирует конкретное место."""
        if seat_class not in self.seats:
            return False
        for seat in self.seats[seat_class]:
            if seat[0] == row and seat[1] == letter:
                if not seat[2]:  # Если свободно
                    seat[2] = True  # Занимаем
                    return True
                return False
        return False

    def find_adjacent_seats(self, seat_class: str, count: int) -> list:
        """Ищет несколько свободных мест рядом (на одном ряду)."""
        if seat_class not in self.seats:
            return []
        
        # Группируем места по рядам
        rows = {}
        for row, letter, is_booked in self.seats[seat_class]:
            if row not in rows:
                rows[row] = []
            rows[row].append((letter, is_booked))
        
        for row, seats_in_row in rows.items():
  
            seats_in_row.sort(key=lambda x: x[0])
            
            adjacent = []
            for letter, is_booked in seats_in_row:
                if not is_booked:
                    adjacent.append(f"{row}{letter}")
                    if len(adjacent) == count:
                        return adjacent
                else:
                    adjacent = [] 
        return []

    def print_cabin_map(self):
        """Печатает наглядную карту салона."""
        print(f"\n--- План салона рейса {self.flight_number} ---")
        for seat_class, seats in self.seats.items():
            print(f"Класс: {seat_class.upper()}")
            current_row = None
            row_str = ""
            for row, letter, is_booked in seats:
                if current_row != row:
                    if current_row is not None:
                        print(row_str)
                    current_row = row
                    row_str = f"Ряд {row:2}: "
                
                # [X] - занято, [ ] - свободно
                status = "[X]" if is_booked else f"[{letter}]"
                row_str += status + " "
            if row_str:
                print(row_str)


class BookingSystem:
    def __init__(self):
        self.airports = {}  # {code: Airport}
        self.flights = []   # список объектов Flight

    def add_airport(self, code: str, name: str, city: str):
        airport = Airport(code, name, city)
        self.airports[airport.code] = airport
        print(f"Аэропорт {airport} успешно добавлен.")

    def add_flight(self, flight_number: str, origin_code: str, dest_code: str, 
                   departure_str: str, duration_minutes: int, extra_services: dict = None) -> Flight:
        """departure_str формат: 'YYYY-MM-DD HH:MM'"""
        origin = self.airports.get(origin_code.upper())
        dest = self.airports.get(dest_code.upper())
        
        if not origin or not dest:
            print("Ошибка: Аэропорт вылета или прибытия не найден в системе!")
            return None
            
        departure_time = datetime.strptime(departure_str, "%Y-%m-%d %H:%M")
        flight = Flight(flight_number, origin, dest, departure_time, duration_minutes, extra_services)
        self.flights.append(flight)
        print(f"Рейс {flight_number} {origin.code} -> {dest.code} добавлен.")
        return flight

    def search_flights(self, origin_code: str, dest_code: str, seat_class: str, 
                       time_preference: str = None, min_seats_adjacent: int = 1) -> list:
        """
        Поиск подходящих рейсов по направлению и фильтрам.
        time_preference: 'morning' (06-12), 'afternoon' (12-18), 'evening' (18-24), 'night' (00-06)
        """
        found_flights = []
        now = datetime.now() # Ищем только будущие рейсы (в рамках симуляции можно убрать)

        for flight in self.flights:
            if flight.origin.code == origin_code.upper() and flight.destination.code == dest_code.upper():
                if flight.get_free_seats_count(seat_class) < min_seats_adjacent:
                    continue
                if min_seats_adjacent > 1 and not flight.find_adjacent_seats(seat_class, min_seats_adjacent):
                    continue
                if time_preference:
                    hour = flight.departure_time.hour
                    if time_preference == "morning" and not (6 <= hour < 12): continue
                    if time_preference == "afternoon" and not (12 <= hour < 18): continue
                    if time_preference == "evening" and not (18 <= hour < 24): continue
                    if time_preference == "night" and not (0 <= hour < 6): continue

                found_flights.append(flight)
        found_flights.sort(key=lambda x: x.departure_time)
        return found_flights