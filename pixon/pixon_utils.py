from airtest.core.android.adb import ADB

def is_airtest_active(serial):
    adb = ADB(serialno=serial)
    out = adb.shell("ps | grep yosemite")
    return bool(out.strip())