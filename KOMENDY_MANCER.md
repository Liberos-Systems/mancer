# Lista komend wspieranych przez Mancer

## Komendy oficjalnie wspierane (zarejestrowane w CommandFactory)

### Komendy plikowe
1. **ls** - listowanie plików
2. **cp** - kopiowanie plików
3. **cd** - zmiana katalogu
4. **find** - wyszukiwanie plików
5. **grep** - wyszukiwanie wzorców w plikach
6. **cat** - wyświetlanie zawartości plików
7. **tail** - wyświetlanie końca plików
8. **head** - wyświetlanie początku plików

### Komendy systemowe
9. **ps** - lista procesów
10. **systemctl** - zarządzanie systemd
11. **hostname** - nazwa hosta
12. **df** - użycie dysku
13. **echo** - wyświetlanie tekstu
14. **wc** - liczenie linii/słów/znaków

### Komendy sieciowe
15. **netstat** - statystyki sieciowe

## Komendy dodatkowe (zaimplementowane, ale nie w CommandFactory)

### Komendy plikowe
- **mkdir** - tworzenie katalogów
- **mv** - przenoszenie/zmiana nazwy plików
- **rm** - usuwanie plików
- **touch** - tworzenie/aktualizacja plików

### Komendy systemowe
- **cron** - zarządzanie cron
- **kill** - zabijanie procesów
- **service** - zarządzanie usługami (legacy)

### Komendy sieciowe
- **curl** - pobieranie danych przez HTTP
- **ping** - testowanie połączenia sieciowego
- **ssh** - połączenie SSH
- **wget** - pobieranie plików

### Komendy specjalne
- **apt** - zarządzanie pakietami (Debian/Ubuntu)
- **custom** - komendy niestandardowe

---

## Status testów jednostkowych

| Komenda | Test jednostkowy | Status |
|---------|------------------|--------|
| ls | ✅ test_ls.py | ✅ Ma testy |
| cat | ✅ test_cat.py | ✅ Ma testy |
| echo | ✅ test_echo.py | ✅ Ma testy |
| wc | ✅ test_wc.py | ✅ Ma testy |
| grep | ✅ test_grep.py | ✅ Ma testy |
| head | ✅ test_head.py | ✅ Ma testy |
| tail | ✅ test_tail.py | ✅ Ma testy |
| find | ✅ test_find.py | ✅ Ma testy |
| ps | ✅ test_ps.py | ✅ Ma testy |
| df | ✅ test_df.py | ✅ Ma testy |
| cp | ✅ test_cp.py | ✅ Ma testy |
| cd | ✅ test_cd.py | ✅ Ma testy |
| hostname | ✅ test_hostname.py | ✅ Ma testy |
| netstat | ✅ test_netstat.py | ✅ Ma testy |
| systemctl | ✅ test_systemctl.py | ✅ Ma testy |
| apt | ✅ test_apt.py | ✅ Ma testy |
| custom | ✅ test_custom.py | ✅ Ma testy |
| mkdir | ✅ test_mkdir.py | ✅ Ma testy (7 testów) |
| mv | ✅ test_mv.py | ✅ Ma testy (6 testów) |
| rm | ✅ test_rm.py | ✅ Ma testy (8 testów) |
| touch | ✅ test_touch.py | ✅ Ma testy (7 testów) |
| cron | ✅ test_cron.py | ✅ Ma testy (4 testy) |
| kill | ✅ test_kill.py | ✅ Ma testy (4 testy) |
| service | ✅ test_service.py | ✅ Ma testy (5 testów) |
| curl | ✅ test_curl.py | ✅ Ma testy (6 testów) |
| ping | ✅ test_ping.py | ✅ Ma testy (5 testów) |
| ssh | ✅ test_ssh.py | ✅ Ma testy (5 testów) |
| wget | ✅ test_wget.py | ✅ Ma testy (6 testów) |

---

## Status fixtures (coreutils generator)

### Fixtures wygenerowane ✅ (WSZYSTKIE KOMENDY COREUTILS)
1. **cat** - 20 fixtures ✅
2. **echo** - 7 fixtures ✅
3. **grep** - 22 fixtures ✅
4. **head** - 20 fixtures ✅
5. **ls** - 39 fixtures ✅
6. **sort** - 22 fixtures ✅
7. **tail** - 6 fixtures ✅
8. **uniq** - 22 fixtures ✅
9. **wc** - 11 fixtures ✅
10. **find** - 16 fixtures ✅
11. **cp** - 22 fixtures ✅
12. **df** - 22 fixtures ✅
13. **hostname** - 9 fixtures ✅
14. **ps** - 12 fixtures ✅ (ps jest z procps, ale działa)
15. **mkdir** - 22 fixtures ✅
16. **mv** - 22 fixtures ✅
17. **rm** - 24 fixtures ✅
18. **touch** - 24 fixtures ✅

**Łącznie: 18 komend coreutils z 342 fixtures**

### Komendy nie-coreutils (nie można wygenerować fixtures)
- **cd** - problematyczne (zmienia katalog roboczy) ⚠️
- **netstat** - nie jest coreutils (net-tools) ⚠️
- **systemctl** - nie jest coreutils (systemd) ⚠️
- **apt** - nie jest coreutils (apt package manager) ⚠️
- **cron** - nie jest coreutils (cronie) ⚠️
- **kill** - nie jest coreutils (procps) ⚠️
- **service** - nie jest coreutils (sysvinit) ⚠️
- **curl** - nie jest coreutils ⚠️
- **ping** - nie jest coreutils (iputils) ⚠️
- **ssh** - nie jest coreutils (openssh) ⚠️
- **wget** - nie jest coreutils ⚠️

---

## Plan generowania fixtures

### Priorytet 1: Komendy coreutils z testami jednostkowymi (DO WYGENEROWANIA)
1. ✅ **find** - w commands.yaml, wygenerować fixtures
2. ✅ **cp** - w commands.yaml, wygenerować fixtures
3. ✅ **df** - w commands.yaml, wygenerować fixtures
4. ✅ **hostname** - w commands.yaml, wygenerować fixtures
5. ✅ **ps** - w commands.yaml, wygenerować fixtures (ps jest z procps, ale działa)
6. ⚠️ **cd** - NIE w commands.yaml (problematyczne - zmienia katalog roboczy, może wymagać specjalnego podejścia)

### Priorytet 2: Komendy nie-coreutils z testami (wymagają rozszerzenia generatora)
7. ⚠️ **netstat** - nie jest coreutils (net-tools), może wymagać osobnego generatora
8. ⚠️ **systemctl** - nie jest coreutils (systemd), może wymagać osobnego generatora
9. ⚠️ **apt** - nie jest coreutils (apt), może wymagać osobnego generatora

### Priorytet 3: Komendy coreutils bez testów (opcjonalne)
10. **sort** - już ma fixtures, można dodać testy
11. **uniq** - już ma fixtures, można dodać testy
12. **mkdir** - dodać do commands.yaml i wygenerować
13. **mv** - dodać do commands.yaml i wygenerować
14. **rm** - dodać do commands.yaml i wygenerować (ostrożnie z error_arguments)
15. **touch** - dodać do commands.yaml i wygenerować

---

## Podsumowanie

### Komendy z testami i fixtures ✅ (COREUTILS)
- **ls, cat, echo, wc, grep, head, tail, find, cp, df, hostname, ps, mkdir, mv, rm, touch** - 16 komend
- **sort, uniq** - 2 komendy (mają fixtures, brak testów - opcjonalne)

### Komendy z testami, nie-coreutils ⚠️ (nie można wygenerować fixtures)
- **cd** - problematyczne (zmienia katalog)
- **netstat, systemctl, apt, cron, kill, service, curl, ping, ssh, wget** - nie są coreutils

### Status: ✅ WSZYSTKIE KOMENDY COREUTILS MAJĄ FIXTURES!

---

## Status: ✅ WSZYSTKIE FIXTURES WYGENEROWANE!

### ✅ Zakończone
1. **Fixtures wygenerowane** - wszystkie 18 komend coreutils mają fixtures (377 fixtures łącznie)
2. **Testy zmigrowane na fixtures** - ls, cat, echo, wc, grep, head, tail
3. **Nowe komendy zaimplementowane** - mkdir, mv, rm, touch, cron, kill, service, curl, ping, ssh, wget
4. **Nowe testy stworzone** - wszystkie nowe komendy mają testy jednostkowe (65 testów)

### ✅ Zakończone migracje testów
**Testy używające fixtures (11 komend):**
- test_ls.py, test_cat.py, test_echo.py, test_wc.py, test_grep.py
- test_head.py, test_tail.py
- test_mkdir.py, test_mv.py, test_rm.py, test_touch.py

**Testy używające mocków (7 komend):**
- test_cron.py, test_kill.py, test_service.py (system)
- test_curl.py, test_ping.py, test_ssh.py, test_wget.py (network)

### 🔄 Do zrobienia (opcjonalne)
1. **Zmigrować pozostałe testy na fixtures:**
   - test_find.py
   - test_cp.py
   - test_df.py
   - test_hostname.py
   - test_ps.py

2. **Dodać testy dla komend z fixtures:**
   - **sort** - ma fixtures (22), brak testów
   - **uniq** - ma fixtures (22), brak testów

3. **Rozważyć specjalne przypadki:**
   - **cd** - problematyczne (zmienia katalog), może wymagać specjalnego podejścia
