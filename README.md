# Screw Land Automation Test

Project automation test game Screw Land using Airtest.

## Tree folder structor

- `common/`: Layer use maintain (BasePage)
- `pages/`: Object file with function in game
- `pixon/`: Pixon library and extention
- `DailyMission/`: All file Dailymission test `.air`

## requirement

- Python 3.7+
- Airtest
- Tesseract OCR

## how to install

## how to run

```bash
python pixon_run.py DailyMission\test_new_user.air --device android://127.0.0.1:5037/emulator-5554 --report reports
```
