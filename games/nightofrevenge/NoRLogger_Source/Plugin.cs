using BepInEx;
using HarmonyLib;
using UnityEngine;
using BepInEx.Logging;

namespace NoRLogger;
    
[BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
[BepInProcess("NightofRevenge.exe")]
public class Plugin : BaseUnityPlugin {

    public static bool isInAnimation = false;
    public static bool isInGameOver = false;

    internal static ManualLogSource Log;

    private void Awake() {
        Plugin.Log = base.Logger;
        Logger.LogInfo($"Plugin {PluginInfo.PLUGIN_GUID} is loaded!");

        Harmony.CreateAndPatchAll(typeof(LogPatches));
    }

}