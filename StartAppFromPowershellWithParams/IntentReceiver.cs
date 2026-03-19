using UnityEngine;

public class IntentReceiver : MonoBehaviour
{
    // Make sure this GameObject persists across scenes if needed
    void Awake()
    {
        DontDestroyOnLoad(gameObject);
    }

    // Java will automatically call this method and pass the string
    public void OnReceiveJson(string base64String)
    {
        byte[] decodedBytes = System.Convert.FromBase64String(base64String);
        string rawJson = System.Text.Encoding.UTF8.GetString(decodedBytes);
        Debug.Log(">>> INTENT CAUGHT LIVE: json is " + rawJson);
        // TODO: Update your  game logic here
    }
}