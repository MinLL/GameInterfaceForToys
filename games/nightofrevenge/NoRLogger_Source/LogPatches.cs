using HarmonyLib;
using UnityEngine;

namespace NoRLogger;

class LogPatches {

  [HarmonyPatch(typeof(EnemyDate), "Nakadasi")]
  [HarmonyPostfix]
  static void LogEnemyOrgasm() {
    Plugin.Log.LogInfo("Enemy Orgasm");
  }

  [HarmonyPatch(typeof(Trapdata), "Library_Naka")]
  [HarmonyPostfix]
  static void LogTrapOrgasm() {
    Plugin.Log.LogInfo("Trap Orgasm");
  }

  [HarmonyPatch(typeof(EnemyDate), "LostVirgin")]
  [HarmonyPostfix]
  static void LogLostVirgin() {
    Plugin.Log.LogInfo("First Penetration");
  }

  [HarmonyPatch(typeof(EnemyDate), "Player_Orgsm")]
  [HarmonyPostfix]
  static void LogOrgasm() {
    Plugin.Log.LogInfo("Player Orgasm");
  }

  [HarmonyPatch(typeof(playercon), "fun_damage")]
  [HarmonyPatch(typeof(playercon), "fun_damage_Improvement")]
  [HarmonyPrefix]
  static void LogDamage(playercon __instance, PlayerStatus ___playerstatus, bool ___stabnow, bool ___parrynow, float ___guradcount) {
    if (!__instance.stepfrag && !___stabnow) {
      if (__instance.guard && ___playerstatus.Sp > 0f && __instance.justguard >= ___playerstatus._GuardCutTime && ___guradcount == 0f) {
        Plugin.Log.LogInfo("Player Block Damage");
      } else if (!__instance.guard && !___parrynow && !__instance.mutekitime) {
        Plugin.Log.LogInfo("Player Damage");
      }
    }
  }

  [HarmonyPatch(typeof(playercon), "SpDeath")]
  [HarmonyPostfix]
  static void LogDeath(bool ___Death) {
    if (___Death) {
      Plugin.Log.LogInfo("Player Death");
    }
  }

  [HarmonyPatch(typeof(playercon), "Update")]
  [HarmonyPostfix]
  static void LogEroAnimation(playercon __instance) {
    if (__instance.erodown != 0 && __instance.eroflag) {
      if (!Plugin.isInAnimation) {
        Plugin.isInAnimation = true;
        Plugin.Log.LogInfo("Ero Animation Start");
      }
    } else {
      if (Plugin.isInAnimation) {
        Plugin.isInAnimation = false;
        Plugin.Log.LogInfo("Ero Animation End");
      }
    }
  }

  [HarmonyPatch(typeof(REgame), "GOsceneLoad")]
  [HarmonyPatch(typeof(StartTyoukyoushiERO), "GOsceneLoad")]
  [HarmonyPatch(typeof(StartPraymaidenERO), "GOsceneLoad")]
  [HarmonyPatch(typeof(BlackMafiaERO), "GOsceneLoad")]
  [HarmonyPostfix]
  static void LogGameOverStart() {
    Plugin.Log.LogInfo("GameOver Start");
  }

  [HarmonyPatch(typeof(AnimationOnlyGO), "REstrat")]
  [HarmonyPatch(typeof(AnimationOnlyGosecond), "REstrat")]
  [HarmonyPatch(typeof(BigoniERO), "REstrat")]
  [HarmonyPatch(typeof(DialogControllerEroEv), "REstrat")]
  [HarmonyPatch(typeof(DialogControllerEroEVunderWindow), "REstrat")]
  [HarmonyPatch(typeof(DialogControllerMainEVunder), "REstrat")]
  [HarmonyPatch(typeof(DialogControllerNpcEVunder), "REstrat")]
  [HarmonyPatch(typeof(PraymaidenERO), "REstrat")]
  [HarmonyPatch(typeof(SlumToiletGoEro), "REstrat")]
  [HarmonyPatch(typeof(TextController), "REstrat")]
  [HarmonyPatch(typeof(TextControllerGO), "REstrat")]
  [HarmonyPatch(typeof(TyoukyoushiERO), "REstrat")]
  [HarmonyPrefix]
  static void LogGameOverEnd() {
    Plugin.Log.LogInfo("GameOver End");
  }
}
