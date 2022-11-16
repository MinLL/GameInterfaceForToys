Scriptname SkyrimToyInterfacePlayerScript extends ReferenceAlias  

ReferenceAlias Property PlayerRef  Auto  
Float Property OnHitCooldown Auto
SexLabFramework property SexLab auto

; Setup handlers for mod events we are interested in.
function RegisterEvents()		
    ; RegisterForModEvent("theEvent", "OnEventHandler")
    RegisterForModEvent("EventOnSit", "OnSitDevious")
    RegisterForModEvent("DeviceVibrateEffectStart", "OnVibrateStart")
    RegisterForModEvent("DeviceVibrateEffectStop", "OnVibrateStop")
    RegisterForModEvent("DeviceActorOrgasm", "OnDeviceActorOrgasm")
    RegisterForModEvent("DeviceEdgedActor", "OnDeviceEdgedActor")
    RegisterForModEvent("HookAnimationStart", "OnSexlabAnimationStart")
    Log("Registered for mod events.")
EndFunction

Event OnSexlabAnimationStart(int threadID, bool HasPlayer)
      If !HasPlayer
      	 Log("Animation does not contain player - done.")
      	 return
      EndIf
      sslThreadController Controller = Sexlab.ThreadSlots.GetController(threadID)
      sslBaseAnimation anim = Controller.Animation
      bool boobjob = anim.HasTag("Boobjob")
      bool vaginal = anim.HasTag("Vaginal")
      bool fisting = anim.HasTag("Fisting")
      bool masturbation = anim.HasTag("Masturbation")
      bool anal = anim.HasTag("Anal")
      bool oral = anim.HasTag("Oral")
      Log("OnSexlabAnimationStart(boobjob='" + boobjob + "', vaginal='" + vaginal + "', fisting='" + fisting + "', masturbation='" + masturbation + "', anal='" + anal + "', oral='" + oral +"')")
EndEvent


Event OnVibrateStart(string eventName, string strArg, float numArg, Form sender)
    Log("OnVibrateStart()")
EndEvent


Event OnVibrateStop(string eventName, string strArg, float numArg, Form sender)
    Log("OnVibrateStop()")
EndEvent


Event OnDeviceActorOrgasm(string eventName, string strArg, float numArg, Form sender)
    Log("OnDeviceActorOrgasm()")
EndEvent


Event OnDeviceEdgedActor(string eventName, string strArg, float numArg, Form sender)
    Log("OnDeviceEdgedActor()")
EndEvent


; Called when game loads.
Event OnPlayerLoadGame()
    OnHitCooldown = Utility.GetCurrentRealTime()
    Log("OnPlayerLoadGame(): " + OnHitCooldown as string)
    RegisterEvents()
EndEvent


string Function GetVitalString(Actor akActor)
    Float health = akActor.GetActorValue("Health")
    Float magicka = akActor.GetActorValue("Magicka")
    Float stamina = akActor.GetActorValue("Stamina")
    Float maxHealth = akActor.GetBaseActorValue("Health")
    Float maxMagicka = akActor.GetBaseActorValue("Magicka")
    Float maxStamina = akActor.GetBaseActorValue("Stamina")
    return "[health='"+health+"/"+maxHealth+"', magicka='"+magicka+"/"+maxMagicka+"', stamina='"+stamina+"/"+maxStamina+"']"
EndFunction


; Called when hit in combat. Internal cooldown to reduce script load.
Event OnHit(ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked)
    if Utility.GetCurrentRealTime() > OnHitCooldown
        OnHitCooldown = Utility.GetCurrentRealTime() + 1 ; 1 second cooldown
    else
        return
    EndIf
    string output = "OnHit("
    output += "akSource='" + (akSource.GetName() as string) +"'"
    output += ", akProjectile='"+(akProjectile as string)+"'"
    output += ", abPowerAttack='" + (abPowerAttack as string)+ "'"
    output += ", abBashAttack='" +(abBashAttack as string)+"'"
    output += ", abSneakAttack='"+(abSneakAttack as string)+"'"
    output += ", abHitBlocked='"+(abHitBlocked as string)+"'"
    output += "): " + GetVitalString(PlayerRef.GetActorRef())
    Log(output)
EndEvent


; Called when sitting while wearing a devious device
Event OnSitDevious(string eventName, string strArg, float numArg, Form sender)
    Log("OnSitDevious()")
EndEvent


Function Log(string in)
    Debug.Trace("[SkyrimToyInterface]: " + in)
EndFunction
 

