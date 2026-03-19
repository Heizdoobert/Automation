- use with packagename and default main activity
just need to add IntentReader.cs into project, edit the data handle part

start the app by run:
.\start_app.ps1 "com.pool.match.puzzle3d" -json "data.json"
.\start_app.ps1 "com.pool.match.puzzle3d"




-use with custom activity
add IntentReceiver.cs, CustomUnityActivity.java, make CustomUnityActivity your LAUNCHER in AndroidManifest.xml

during game play, run command:
.\start_app.ps1 "com.pool.match.puzzle3d/com.unity3d.player.CustomUnityActivity" -json "data.json"

