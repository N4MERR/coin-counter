# Coin Identifier

## Základní informace

* **Název projektu:** Coin Identifier
* **Autor:** Zhao Xiang Yang
* **Škola:** SPŠE Ječná
* **Typ projektu:** Školní projekt

---

## 1. Požadavky na aplikaci

### Funkční požadavky

* Uživatel může nahrát jeden nebo více obrázků mincí
* Aplikace identifikuje mince pomocí AI modelu
* Aplikace zobrazí název mince a confidence score
* Uživatel může změnit AI model
* Aplikace umožňuje jednoduché ovládání přes GUI

### Nefunkční požadavky

* Aplikace běží jako desktopová (.exe)
* Rychlá odezva (řádově sekundy)
* Offline provoz (není potřeba internet)
* Podpora formátů JPG, PNG

### Use Case (textově)

* Uživatel nahraje obrázek → aplikace zpracuje → zobrazí výsledek
* Uživatel nahradí model → aplikace použije nový model

---

## 2. Architektura aplikace

### Komponenty

* **GUI (PySide)**
  Uživatelské rozhraní

* **Inference modul (YOLOv8)**
  Detekce a klasifikace mincí

* **Image processing (OpenCV)**
  Předzpracování obrazu

### Schéma

```id="m92k1x"
Uživatel → GUI → YOLOv8 model → Výsledek → GUI
```

---

## 3. Chování aplikace

### Typický průběh

1. Uživatel spustí aplikaci
2. Nahraje obrázek
3. Proběhne preprocessing
4. Model provede detekci
5. Výsledek se zobrazí

### Stavy aplikace

* Idle
* Loading Image
* Processing
* Displaying Result

---

## 4. Použité technologie a závislosti

### Knihovny

* Python
* PySide
* YOLOv8 (Ultralytics)
* OpenCV

### Závislosti

* Lokální `.pt` model
* YAML konfigurační soubor

---

## 5. Právní a licenční aspekty

* YOLOv8 (Ultralytics) – open-source licence
* OpenCV – open-source
* Projekt je určen pro vzdělávací účely

---

## 6. Konfigurace aplikace

Aplikace umožňuje změnu modelu:

* Model musí být uložen ve složce `AI_model`
* Musí mít formát `.pt`
* K modelu je nutné dodat odpovídající `.yaml` soubor

### Příklad YAML konfigurace

```yaml id="p4x8zt"
path: /content/split_dataset
train: images/train
val: images/val
test: /content/test_data

nc: 6
names:
  - 10kc
  - 1kc
  - 20kc
  - 2kc
  - 50kc
  - 5kc
```

---

## 7. Instalace a spuštění

* Stáhnout `.exe` soubor z Releases
* Spustit aplikaci

Není potřeba instalace ani internet.

---

## 8. Chybové stavy

* **Neplatný soubor**
  → nahrát podporovaný formát

* **Chybějící model (.pt)**
  → zkontrolovat složku `AI_model`

* **Chybějící YAML soubor**
  → přidat odpovídající konfiguraci

* **Nízká kvalita obrázku**
  → použít kvalitnější snímek

---

## 9. Testování a validace

### Testy

* Test českých mincí (1, 2, 5, 10, 20, 50 Kč)
* Test různých světelných podmínek
* Test více obrázků najednou

### Výsledky

* Vysoká přesnost u 10, 20 a 50 Kč
* Horší výsledky u 1 Kč, 2 Kč a 5 Kč

### Zhodnocení

Aplikace splňuje požadavky, ale přesnost závisí na kvalitě datasetu a podobnosti mincí.

---

## 10. Verze a známé chyby

### Verze

* v1.0 – základní verze

### Známé problémy

* Nižší přesnost u mincí 1 Kč, 2 Kč, 5 Kč
* Citlivost na kvalitu obrázku

---

## 14. Import / Export

### Import

* JPG, PNG
* Jeden nebo více obrázků

### Export

* Výstup pouze v GUI
* Export není implementován

---

## Závěr

Aplikace Coin Identifier využívá model YOLOv8 pro rozpoznávání českých mincí. Umožňuje flexibilní výměnu modelu a demonstruje praktické využití AI v oblasti počítačového vidění.
