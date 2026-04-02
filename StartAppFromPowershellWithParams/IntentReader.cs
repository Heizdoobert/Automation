using UnityEngine;

public class IntentReader : MonoBehaviour
{
    void Start()
    {
        ReadAndroidIntent();
    }

    private void ReadAndroidIntent()
    {
        #if UNITY_ANDROID && !UNITY_EDITOR
        try
        {
            using (AndroidJavaClass unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            {
                AndroidJavaObject currentActivity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");
                AndroidJavaObject intent = currentActivity.Call<AndroidJavaObject>("getIntent");

                if (intent != null)
                {
                    string base64String = intent.Call<string>("getStringExtra", "json");
                    if (!string.IsNullOrEmpty(json))
                    {
                        byte[] decodedBytes = System.Convert.FromBase64String(base64String);
                        string rawJson = System.Text.Encoding.UTF8.GetString(decodedBytes);
                        Debug.Log(">>> INTENT DATA RECEIVED: json is " + rawJson);
                        
                        // TODO: Apply this data to your game 
                    }
                    else
                    {
                        Debug.Log(">>> INTENT DATA RECEIVED: No json found.");
                    }
                }
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError(">>> INTENT ERROR: " + e.Message);
        }
        #endif
    }

   
}