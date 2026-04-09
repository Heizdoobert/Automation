Requirements:
    Python 3.10: https://www.python.org/downloads/windows/
    Airtest: https://github.com/AirtestProject/Airtest/tree/master

Project automation test game Screw Land using Airtest.

## Cấu trúc thư mục

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
python pixon_run.py tests/DailyMission/test_new_user.air --device Android://127.0.0.1:5037/emulator-5554
