package com.yourcompany.yourgame;

import android.content.Intent;
import android.os.Bundle;
import com.unity3d.player.UnityPlayer;
import com.unity3d.player.UnityPlayerActivity;

public class CustomUnityActivity extends UnityPlayerActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        handleIntent(getIntent()); // Catches intent on cold boot
    }

    // THIS is the magic method. It catches intents when the app is already in the foreground.
    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent); // Update the current intent
        handleIntent(intent);
    }

    private void handleIntent(Intent intent) {
        if (intent != null && intent.hasExtra("json")) {
            String json = intent.getStringExtra("json");
            
            // Push the string directly to a C# script on a GameObject named "IntentReceiver"
            UnityPlayer.UnitySendMessage("IntentReceiverGameObjectName", "OnReceiveJson", json);
            
            // Remove the extra so it doesn't trigger again accidentally
            intent.removeExtra("json");
        }
    }
}