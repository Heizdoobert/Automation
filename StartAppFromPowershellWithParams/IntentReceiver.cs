using UnityEngine;

public class IntentReceiver : MonoBehaviour
{
    // Make sure this GameObject persists across scenes if needed
    void Awake()
    {
        DontDestroyOnLoad(gameObject);
    }

    // Java will automatically call this method and pass the string
    public void OnReceiveJson(string json)
    {
        Debug.Log(">>> INTENT CAUGHT LIVE: json is " + json);
        
        // TODO: Update your  game logic here
    }
}