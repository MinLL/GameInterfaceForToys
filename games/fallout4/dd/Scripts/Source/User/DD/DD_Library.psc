Scriptname DD:DD_Library extends Quest

;-----------------------------------------------------------------------------------------------
; Devious Devices - DD_Library
; By Kimy
;
; Merged database fixes by Tron91 and Elsidia
; Added animation system by Dlinny_Lag
; Added Actorvalue system for arousal tracking by naaitsab and Elsidia
; Added plug system by naaitsab and Elsidia
; Modded MT equip to prevent race conditions (EffectQueue) by EgoBallistic
;-----------------------------------------------------------------------------------------------

Group InternalProperties
Actor Property Player Auto Const								; Reference pointer to the player. Very useful and a lot faster than Game.GetPlayer()!
FormList Property DD_PlayerEquippedItems Auto Const				; List containing all items currently worn by the player.
FormList Property DD_PlayerJammedLocks Auto Const				; List keeping track of the player character's jammed locks.
FormList Property DD_ItemTypeKeywords Auto Const				; This list contains all valid item type keywords.
FormList Property DD_MaleModelItems Auto Const					; This list contains items that can be equipped on a male.
Keyword[] Property DD_BoundAnimKeywords Auto Const				; This list contains all valid bondage animation keywords.
GlobalVariable Property DD_GagTalkDoneFlag Auto Const			; This flag is set true for a brief period when the gag dialogue terminates and will allow a gagged character to talked normally.
ReferenceAlias Property GagDialogueTarget Auto Const			; When gagged the NPC you talk to is forced into this alias
GlobalVariable Property DD_PipBoyAlwaysHide Auto Const			; If set to 1, the PipBoy will be always hidden. Default 0 hides the PipBoy only for flagged restraints. -1 turns this feature off completely.
ImageSpaceModifier Property DD_BlindfoldImageSpace Auto Const	; The default blurred screen effect for the blindfold.
Armor Property DD_Stripper Auto Const							; This armor strips you naked. Yeah...really.
Armor Property DD_StripperPA Auto Const							; This armor strips you REALLY naked. Including Power Armor pieces.
Weapon Property DD_SmokinGun Auto Const							; The most evil gun ever. It has no purpose other than unequip whatever the character has drawn.
MiscObject Property BobbyPin Auto Const							; The trustworthy bobby pin. Can be used to pick some restraints.
Keyword Property DD_kw_Event_IsVibrating Auto Const				; Used to make sure two vibrating events don't occur at the same time.
Keyword Property _TD_AnimArchetypeBound Auto Const				; Keyword used for the animation system. Auto-fill and do not change!
Keyword Property AnimArchetypePlayer Auto Const					; Keyword used for the animation system. Auto-fill and do not change!
Armor Property Pipboy Auto Const								; Standard PipBoy
Armor Property DD_Pipboy Auto Const								; Hidden PipBoy, visible only in first person view.
FormList Property DD_StandardCuttingToolsList Auto				; List of standard tools able to be used in cutting attempts.
Int Property DD_EffectQueueHead Auto Hidden						; Start of MT script effect
Int Property DD_EffectQueueTail Auto Hidden						; end of MT script effect
EndGroup

Group ActorValues
ActorValue Property DD_AV_Arousal Auto Const					; For arousal tracker. Very light alternative to SL Aroused
ActorValue Property DD_AV_InflateStatusAnal Auto Const	
ActorValue Property DD_AV_InflateStatusVaginal Auto Const
ActorValue Property DD_AV_VibrateStrengthAnal Auto Const	
ActorValue Property DD_AV_VibrateStrengthVaginal Auto Const
ActorValue Property SpeedMult Auto Const						;100 is default
EndGroup

Group Perks
Perk Property DD_Perk_DisablePowerArmor Auto Const					; This perk will prevent the player from activating powerarmor.
Perk Property DD_Perk_DisableLockPick Auto Const					; This perk will prevent the player from picking locks
Perk Property DD_Perk_DisablePickpocket Auto Const					; This perk will prevent the player from pickpocketing
Perk Property DD_Perk_DisableTrapInteraction Auto Const				; This perk will prevent the player from disarming traps
Perk Property DD_Perk_DisableWorkbench Auto Const					; This perk will prevent the player from using workbenches
EndGroup	

Group Sounds
Sound Property DD_SoundGagged Auto Const
Sound Property DD_SoundMoan Auto Const
Sound Property DD_SoundOrgasm Auto Const
Sound Property DD_SoundMoanShort Auto Const
Sound Property DD_SoundPantShort Auto Const
Sound Property DD_SoundEdged Auto Const
Sound Property DD_SoundEdgedWinddown Auto Const
Sound Property DD_SoundDescSexGaggedHotF Auto Const
Sound Property DD_SoundDescSexGaggedMediumF Auto Const
Sound Property DD_SoundDescSexGaggedMildF Auto Const
Sound Property DD_SoundDescSexGaggedHotM Auto Const
Sound Property DD_SoundDescSexGaggedMediumM Auto Const
Sound Property DD_SoundDescSexGaggedMildM Auto Const
Sound Property DD_SoundDescVibrateVeryWeak Auto Const
Sound Property DD_SoundDescVibrateWeak Auto Const
Sound Property DD_SoundDescVibrateStandard Auto Const
Sound Property DD_SoundDescVibrateStrong Auto Const
Sound Property DD_SoundDescVibrateVeryStrong Auto Const
EndGroup

Group StandardKeys
Key Property DD_RestraintsKey Auto Const					; Standard restraints key, will unlock most generic restraining devices.
Key Property DD_ChastityKey Auto Const						; Standard chastity key, will unlock most generic chastity devices, piercings and plugs.
Key Property DD_HighSecurityKey Auto Const					; Key for high security devices.
Key Property DD_InstituteKey Auto Const						; Key for institute devices.
EndGroup

Group APIKeywords
Keyword Property DD_kw_IsQuestItem Auto Const				; This keyword marks this item as a quest item. It should not be removed by anyone for any reason except by the mod that equipped it!
Keyword Property DD_kw_IsNotGenericItem Auto Const			; This keyword marks this item as non-generic, NOT suitable for random equips or removal by helpful mechanics etc. Other mods are allowed to remove this item if needed.
Keyword Property DD_kw_InventoryItem Auto Const				; This keyword marks the item as an inventory item. The keyword has to be present on the script item.
Keyword Property DD_kw_RenderedItem Auto Const				; This keyword marks the item as rendered item. The keyword has to be present on the item to be displayed on the character.
Keyword Property DD_kw_IsDDKey Auto Const					; This keyword marks the item as a DD key.
EndGroup

Group Topics
Topic Property DialogueGenericHitGroup Auto Const
EndGroup

Group ItemTypes
Keyword Property DD_kw_ItemType_Collar Auto Const			; Used for items that lock on the subject's neck.
Keyword Property DD_kw_ItemType_WristCuffsDisconnected Auto Const		; Used for items that lock on the subject's wrists and/or arms. Usually restraining her hands.
Keyword Property DD_kw_ItemType_WristCuffs Auto Const		; Used for items that lock on the subject's wrists and/or arms. Usually restraining her hands.
Keyword Property DD_kw_ItemType_LegCuffs Auto Const			; Used for items that lock on the subject's ankles and/or legs. Usually restraining her legs. but do not have bound animations or effects
Keyword Property DD_kw_ItemType_LegCuffsHobble Auto Const	; Used for items that lock on the subject's ankles and/or legs and bound her legs together
Keyword Property DD_kw_ItemType_ChastityBelt Auto Const		; Used for items that lock on the subject's waist. Usually cover her privates.
Keyword Property DD_kw_ItemType_ChastityBra Auto Const		; Used for items that lock on the subject's chest. Usually cover her breasts.
Keyword Property DD_kw_ItemType_Harness Auto Const			; Used for items that lock on the subject's torso/upper body. (E.g. Slave Harness. Corsets)
Keyword Property DD_kw_ItemType_Suit Auto Const				; Used for items that lock on the subject's entire body (E.g. Catsuits, Hobble Skirts, Dresses). Can function as restraints, too.
Keyword Property DD_kw_ItemType_Gag Auto Const				; Used for items that lock on the subject's mouth. Usually preventing her from speaking.
Keyword Property DD_kw_ItemType_Blindfold Auto Const		; Used for items that lock on the subject's eyes. Usually preventing her from seeing.
Keyword Property DD_kw_ItemType_Boots Auto Const			; Used for items that lock on the subject's feet. Usually making her walk slower.
Keyword Property DD_kw_ItemType_PlugVaginal Auto Const		; Used for items that lock on the subject's vagina (e.g. dildos).
Keyword Property DD_kw_ItemType_PlugAnal Auto Const			; Used for items that lock on the subject's backside (e.g. anal plug).
Keyword Property DD_kw_ItemType_Gloves Auto Const			; Used for items that lock on the subject's hands (e.g. bondage mittens).
Keyword Property DD_kw_ItemType_Hood Auto Const				; Used for items that lock on the subject's head.
Keyword Property DD_kw_ItemType_NipplePiercings Auto Const	; Used for items that lock on the subject's nipples.
EndGroup

Group ItemSubTypes											; Item subtypes are for identifying items having specific traits and attributes, even if they share the same basic item type.
Keyword Property DD_kw_ItemSubType_Armbinder Auto Const		; An item with this keyword is an armbinder. Subtype of Wrist Cuffs.
Keyword Property DD_kw_ItemSubType_Corset Auto Const		; An item with this keyword is a corset. Subtype of Harnesses.
Keyword Property DD_kw_ItemSubType_CollarHarness Auto Const	; An item with this keyword is a collar harness. Subtype of Harnesses.
Keyword Property DD_kw_ItemSubType_Yoke Auto Const			; An item with this keyword is a yoke. Subtype of Wrist Cuffs.
Keyword Property DD_kw_ItemSubType_HobbleSkirt Auto Const	; An item with this keyword is a hobble skirt. Subtype of Suits.
Keyword Property DD_kw_ItemSubType_Catsuit Auto Const		; An item with this keyword is a catsuit. Subtype of Suits.
Keyword Property DD_kw_ItemSubType_Straitjacket Auto Const	; An item with this keyword is a straitjacket. Subtype of Suits.
Keyword Property DD_kw_ItemSubType_InflatablePlugVaginal Auto Const
Keyword Property DD_kw_ItemSubType_InflatablePlugAnal Auto Const
Keyword Property DD_kw_ItemSubType_VibratingPlugVaginal Auto Const ;Can vibrate
Keyword Property DD_kw_ItemSubType_VibratingPlugAnal Auto Const
Keyword Property DD_kw_ItemSubType_ShockingPlugVaginal Auto Const
Keyword Property DD_kw_ItemSubType_ShockingPlugAnal Auto Const
EndGroup

Group ItemEffects											; These keywords implement standard behaviors for bondage items. The effect will be applied of this keyword in on the RENDERED item!
Keyword Property DD_kw_EffectType_BondageMittens Auto Const	; This keyword marks the item as rendering your hands useless. If it is equipped, no DD item can be removed, other than the ones with this keyword.
Keyword Property DD_kw_EffectType_GagTalkStrict Auto Const	; This keyword marks the item as sealing your mouth. If it is equipped, all dialogue will be disabled.
Keyword Property DD_kw_EffectType_GagTalkNormal Auto Const	; This keyword marks the item as sealing your mouth. If it is equipped, the player has to go through the gag talk, but eventually will be understood.
Keyword Property DD_kw_EffectType_Blindfold Auto Const		; This keyword marks the item as sealing your eyes. If it is equipped, your vision will be limited.
Keyword Property DD_kw_EffectType_BlockPowerArmor Auto Const; This keyword marks the item as rendering the character unable to operte power armor.
Keyword Property DD_kw_EffectType_HidesPipBoy Auto Const	; This keyword marks the item as hiding the PipBoy.
Keyword Property DD_kw_EffectType_DisableFastTravel Auto Const	; This keyword marks the item as prohibiting fast travel.
Keyword Property DD_kw_EffectType_RestrainedLegs Auto Const	; This keyword disables running, sneaking, jumping and sprinting.
Keyword Property DD_kw_EffectType_RestrainedArms Auto Const	; This keyword disables fighting and accessing the favorites.
Keyword Property DD_kw_EffectType_HighHeels Auto Const		; This keyword disables sprinting and running.
Keyword Property DD_kw_EffectType_BlockLockpick Auto Const	; This keyword disables lockpicking
Keyword Property DD_kw_EffectType_BlockPickpocket Auto Const ; This keyword disables pickpocketing
Keyword Property DD_kw_EffectType_BlockTrapInteraction Auto Const ; This keyword trap disabling
Keyword Property DD_kw_EffectType_BlockWorkbench Auto Const	; This keyword disables workbenches
Keyword Property DD_kw_ItemEffect_PlugVibrate Auto Const	; plugs can vibrate
Keyword Property DD_kw_ItemEffect_PlugVibrate_EdgeOnly Auto Const ;Plugs only edge the player
Keyword Property DD_kw_ItemEffect_PlugShock Auto Const		; Plugs can shock the wearer
Keyword Property DD_kw_ItemEffect_PlugInflate Auto Const	;plugs can in-/deflate 
Keyword Property DD_kw_ItemEffect_PlugNoEffect Auto Const	;plugs have no special effects 
EndGroup

Group DeviceLibrary
Armor Property DD_Blindfold_Cloth_Inventory Auto Const
Armor Property DD_Blindfold_Cloth_Rendered Auto Const
Armor Property DD_Blindfold_Inventory Auto Const
Armor Property DD_Blindfold_Rendered Auto Const
Armor Property DD_Boots_Restrictive_Latex_Inventory Auto Const
Armor Property DD_Boots_Restrictive_Latex_Rendered Auto Const
Armor Property DD_Boots_Restrictive_Leather_Inventory Auto Const
Armor Property DD_Boots_Restrictive_Leather_Rendered Auto Const
Armor Property DD_Catsuit_Latex_Inventory Auto Const
Armor Property DD_Catsuit_Latex_Rendered Auto Const
Armor Property DD_ChastityBelt_Corset_BeltAddon_Latex_Inventory Auto Const
Armor Property DD_ChastityBelt_Corset_BeltAddon_Latex_Rendered Auto Const
Armor Property DD_ChastityBelt_Corset_BeltAddon_Leather_Inventory Auto Const
Armor Property DD_ChastityBelt_Corset_BeltAddon_Leather_Rendered Auto Const
Armor Property DD_ChastityBeltGold_Corset_BeltAddon_Latex_Inventory Auto Const
Armor Property DD_ChastityBeltGold_Corset_BeltAddon_Latex_Rendered Auto Const
Armor Property DD_ChastityBeltGold_Corset_BeltAddon_Leather_Inventory Auto Const
Armor Property DD_ChastityBeltGold_Corset_BeltAddon_Leather_Rendered Auto Const
Armor Property DD_ChastityBelt_Institute_Inventory Auto Const
Armor Property DD_ChastityBelt_Institute_Rendered Auto Const
Armor Property DD_ChastityBelt_Iron_Inventory Auto Const
Armor Property DD_ChastityBelt_Iron_Rendered Auto Const
Armor Property DD_ChastityBelt_Rust_Inventory Auto Const
Armor Property DD_ChastityBelt_Rust_Rendered Auto Const
Armor Property DD_ChastityBelt_Steel_Gold_Inventory Auto Const
Armor Property DD_ChastityBelt_Steel_Gold_Rendered Auto Const
Armor Property DD_ChastityBelt_Steel_Inventory Auto Const
Armor Property DD_ChastityBelt_Steel_Rendered Auto Const
Armor Property DD_ChastityBelt_Steel_Silver_Inventory Auto Const
Armor Property DD_ChastityBelt_Steel_Silver_Rendered Auto Const
Armor Property DD_ChastityBra_Iron_Inventory Auto Const
Armor Property DD_ChastityBra_Iron_Rendered Auto Const
Armor Property DD_ChastityBra_Steel_Gold_Inventory Auto Const
Armor Property DD_ChastityBra_Steel_Gold_Rendered Auto Const
Armor Property DD_Collar_Harness_Latex_Inventory Auto Const
Armor Property DD_Collar_Harness_Latex_Rendered Auto Const
Armor Property DD_Collar_Heavy_Inventory Auto Const
Armor Property DD_Collar_Heavy_Rendered Auto Const
Armor Property DD_Collar_Institute_Inventory Auto Const
Armor Property DD_Collar_Institute_Rendered Auto Const
Armor Property DD_Collar_Iron_Inventory Auto Const
Armor Property DD_Collar_Iron_Rendered Auto Const
Armor Property DD_Collar_Leather_Inventory Auto Const
Armor Property DD_Collar_Leather_Rendered Auto Const
Armor Property DD_Collar_Posture_Inventory Auto Const
Armor Property DD_Collar_Posture_Rendered Auto Const
Armor Property DD_Collar_Posture_Steel_Inventory Auto Const
Armor Property DD_Collar_Posture_Steel_Rendered Auto Const
Armor Property DD_Collar_Restrictive_Latex_Inventory Auto Const
Armor Property DD_Collar_Restrictive_Latex_Rendered Auto Const
Armor Property DD_Collar_Restrictive_Leather_Inventory Auto Const
Armor Property DD_Collar_Restrictive_Leather_Rendered Auto Const
Armor Property DD_Collar_Rope_Inventory Auto Const
Armor Property DD_Collar_Rope_Rendered Auto Const
Armor Property DD_Collar_Slave_Inventory Auto Const
Armor Property DD_Collar_Slave_Rendered Auto Const
Armor Property DD_Collar_Steel_Gold_Inventory Auto Const
Armor Property DD_Collar_Steel_Gold_Rendered Auto Const
Armor Property DD_Collar_Steel_Inventory Auto Const
Armor Property DD_Collar_Steel_Rendered Auto Const
Armor Property DD_Collar_Steel_Silver_Inventory Auto Const
Armor Property DD_Collar_Steel_Silver_Rendered Auto Const
Armor Property DD_Collar_Strict_Inventory Auto Const
Armor Property DD_Collar_Strict_Rendered Auto Const
Armor Property DD_Collar_Vault_Inventory Auto Const
Armor Property DD_Collar_Vault_Rendered Auto Const
Armor Property DD_Collar_Vault_Shock_Inventory Auto Const
Armor Property DD_Collar_Vault_Shock_Rendered Auto Const
Armor Property DD_Dress_Corset_Latex_Black_Inventory Auto Const
Armor Property DD_Dress_Corset_Latex_Black_Rendered Auto Const
Armor Property DD_Dress_Corset_Latex_Pink_Inventory Auto Const
Armor Property DD_Dress_Corset_Latex_Pink_Rendered Auto Const
Armor Property DD_Dress_Corset_Latex_Red_Inventory Auto Const
Armor Property DD_Dress_Corset_Latex_Red_Rendered Auto Const
Armor Property DD_Dress_Latex_Bikini_Black_Inventory Auto Const
Armor Property DD_Dress_Latex_Bikini_Black_Rendered Auto Const
Armor Property DD_Dress_Latex_Bikini_Pink_Inventory Auto Const
Armor Property DD_Dress_Latex_Bikini_Pink_Rendered Auto Const
Armor Property DD_Dress_Latex_Bikini_Red_Inventory Auto Const
Armor Property DD_Dress_Latex_Bikini_Red_Rendered Auto Const
Armor Property DD_Dress_Latex_Black_Inventory Auto Const
Armor Property DD_Dress_Latex_Black_Rendered Auto Const
Armor Property DD_Dress_Latex_Mesh_Inventory Auto Const
Armor Property DD_Dress_Latex_Mesh_Rendered Auto Const
Armor Property DD_Dress_Latex_Pattern_Inventory Auto Const
Armor Property DD_Dress_Latex_Pattern_Rendered Auto Const
Armor Property DD_Dress_Latex_Pink_Inventory Auto Const
Armor Property DD_Dress_Latex_Pink_Rendered Auto Const
Armor Property DD_Dress_Latex_Red_Inventory Auto Const
Armor Property DD_Dress_Latex_Red_Rendered Auto Const
Armor Property DD_Dress_Spandex_Black_Inventory Auto Const
Armor Property DD_Dress_Spandex_Black_Rendered Auto Const
Armor Property DD_Dress_Spandex_Pink_Inventory Auto Const
Armor Property DD_Dress_Spandex_Pink_Rendered Auto Const
Armor Property DD_Dress_Spandex_Red_Inventory Auto Const
Armor Property DD_Dress_Spandex_Red_Rendered Auto Const
Armor Property DD_ElegantDress_Latex_Black_Inventory Auto Const
Armor Property DD_ElegantDress_Latex_Black_Rendered Auto Const
Armor Property DD_ElegantDress_Latex_Red_Inventory Auto Const
Armor Property DD_ElegantDress_Latex_Red_Rendered Auto Const
Armor Property DD_ElegantDress_Latex_White_Inventory Auto Const
Armor Property DD_ElegantDress_Latex_White_Rendered Auto Const
Armor Property DD_ElegantDress_Leather_Black_Inventory Auto Const
Armor Property DD_ElegantDress_Leather_Black_Rendered Auto Const
Armor Property DD_ElegantDress_Leather_Red_Inventory Auto Const
Armor Property DD_ElegantDress_Leather_Red_Rendered Auto Const
Armor Property DD_ElegantDress_Leather_White_Inventory Auto Const
Armor Property DD_ElegantDress_Leather_White_Rendered Auto Const
Armor Property DD_Gag_Ball_Harness_Inventory Auto Const
Armor Property DD_Gag_Ball_Harness_Rendered Auto Const
Armor Property DD_Gag_Ball_Strap_Inventory Auto Const
Armor Property DD_Gag_Ball_Strap_Rendered Auto Const
Armor Property DD_Gag_Bit_Inventory Auto Const
Armor Property DD_Gag_Bit_Rendered Auto Const
Armor Property DD_Gag_Panel_Harness_Inventory Auto Const
Armor Property DD_Gag_Panel_Harness_Rendered Auto Const
Armor Property DD_Gag_Panel_Strap_Inventory Auto Const
Armor Property DD_Gag_Panel_Strap_Rendered Auto Const
Armor Property DD_Gag_Pear_Inventory Auto Const
Armor Property DD_Gag_Pear_Rendered Auto Const
Armor Property DD_Gag_PearBit_Inventory Auto Const
Armor Property DD_Gag_PearBit_Rendered Auto Const
Armor Property DD_Gag_Penis_Harness_Inventory Auto Const
Armor Property DD_Gag_Penis_Harness_Rendered Auto Const
Armor Property DD_Gag_Tape_Inventory Auto Const
Armor Property DD_Gag_Tape_Rendered Auto Const
Armor Property DD_Gag_TapeLarge_Inventory Auto Const
Armor Property DD_Gag_TapeLarge_Rendered Auto Const
Armor Property DD_Gloves_BondageMittens_Latex_Inventory Auto Const
Armor Property DD_Gloves_BondageMittens_Latex_Rendered Auto Const
Armor Property DD_Gloves_BondageMittens_Leather_Inventory Auto Const
Armor Property DD_Gloves_BondageMittens_Leather_Rendered Auto Const
Armor Property DD_Gloves_Restrictive_Latex_Inventory Auto Const
Armor Property DD_Gloves_Restrictive_Latex_Rendered Auto Const
Armor Property DD_Gloves_Restrictive_Leather_Inventory Auto Const
Armor Property DD_Gloves_Restrictive_Leather_Rendered Auto Const
Armor Property DD_Harness_Chain_Locked_Rusty_Inventory Auto Const
Armor Property DD_Harness_Chain_Locked_Rusty_Rendered Auto Const
Armor Property DD_Harness_Chain_Locked_Silver_Inventory Auto Const
Armor Property DD_Harness_Chain_Locked_Silver_Rendered Auto Const
Armor Property DD_Harness_Chain_Rusty_Inventory Auto Const
Armor Property DD_Harness_Chain_Rusty_Rendered Auto Const
Armor Property DD_Harness_Chain_Silver_Inventory Auto Const
Armor Property DD_Harness_Chain_Silver_Rendered Auto Const
Armor Property DD_Harness_Corset_Latex_Inventory Auto Const
Armor Property DD_Harness_Corset_Latex_Rendered Auto Const
Armor Property DD_Harness_Corset_Leather_Inventory Auto Const
Armor Property DD_Harness_Corset_Leather_Rendered Auto Const
Armor Property DD_Harness_Latex_Inventory Auto Const
Armor Property DD_Harness_Latex_Rendered Auto Const
Armor Property DD_HobbleSkirt_Latex_Inventory Auto Const
Armor Property DD_HobbleSkirt_Latex_Rendered Auto Const
Armor Property DD_HobbleSkirt_Leather_Inventory Auto Const
Armor Property DD_HobbleSkirt_Leather_Rendered Auto Const
Armor Property DD_HobbleSkirt_Open_Latex_Inventory Auto Const
Armor Property DD_HobbleSkirt_Open_Latex_Rendered Auto Const
Armor Property DD_HobbleSkirt_Open_Leather_Inventory Auto Const
Armor Property DD_HobbleSkirt_Open_Leather_Rendered Auto Const
Armor Property DD_Hood_Balloon_Latex_Inventory Auto Const
Armor Property DD_Hood_Balloon_Latex_Rendered Auto Const
Armor Property DD_Hood_Latex_Black_Inventory Auto Const
Armor Property DD_Hood_Latex_Black_Rendered Auto Const
Armor Property DD_Hood_MaskofShame_Inventory Auto Const
Armor Property DD_Hood_MaskofShame_Rendered Auto Const
Armor Property DD_Legcuffs_Institute_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Institute_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Institute_Inventory Auto Const
Armor Property DD_Legcuffs_Institute_Rendered Auto Const
Armor Property DD_Legcuffs_Leather_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Leather_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Leather_Inventory Auto Const
Armor Property DD_Legcuffs_Leather_Rendered Auto Const
Armor Property DD_Legcuffs_Slave_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Slave_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Slave_Inventory Auto Const
Armor Property DD_Legcuffs_Slave_Rendered Auto Const
Armor Property DD_Legcuffs_Steel_Gold_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Steel_Gold_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Steel_Gold_Inventory Auto Const
Armor Property DD_Legcuffs_Steel_Gold_Rendered Auto Const
Armor Property DD_Legcuffs_Steel_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Steel_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Steel_Inventory Auto Const
Armor Property DD_Legcuffs_Steel_Rendered Auto Const
Armor Property DD_Legcuffs_Steel_Silver_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Steel_Silver_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Steel_Silver_Inventory Auto Const
Armor Property DD_Legcuffs_Steel_Silver_Rendered Auto Const
Armor Property DD_Legcuffs_Vault_Hobble_Inventory Auto Const
Armor Property DD_Legcuffs_Vault_Hobble_Rendered Auto Const
Armor Property DD_Legcuffs_Vault_Inventory Auto Const
Armor Property DD_Legcuffs_Vault_Rendered Auto Const
Armor Property DD_NipplePiercings_Blue_Inventory Auto Const
Armor Property DD_NipplePiercings_Blue_Rendered Auto Const
Armor Property DD_NipplePiercings_Clamps_Rust_Inventory Auto Const
Armor Property DD_NipplePiercings_Clamps_Rust_Rendered Auto Const
Armor Property DD_NipplePiercings_Clamps_Silver_Inventory Auto Const
Armor Property DD_NipplePiercings_Clamps_Silver_Rendered Auto Const
Armor Property DD_NipplePiercings_Pink_Inventory Auto Const
Armor Property DD_NipplePiercings_Pink_Rendered Auto Const
Armor Property DD_NipplePiercings_Purple_Inventory Auto Const
Armor Property DD_NipplePiercings_Purple_Rendered Auto Const
Armor Property DD_NipplePiercings_Vice_Rust_Inventory Auto Const
Armor Property DD_NipplePiercings_Vice_Rust_Rendered Auto Const
Armor Property DD_NipplePiercings_Vice_Silver_Inventory Auto Const
Armor Property DD_NipplePiercings_Vice_Silver_Rendered Auto Const
Armor Property DD_PlugAnal_Atomic_Blue_Inventory Auto Const
Armor Property DD_PlugAnal_Atomic_Blue_Rendered Auto Const
Armor Property DD_PlugAnal_Atomic_Purple_Inventory Auto Const
Armor Property DD_PlugAnal_Atomic_Purple_Rendered Auto Const
Armor Property DD_PlugAnal_Atomic_White_Inventory Auto Const
Armor Property DD_PlugAnal_Atomic_White_Rendered Auto Const
Armor Property DD_PlugAnal_ChainBell_Inventory Auto Const
Armor Property DD_PlugAnal_ChainBell_Rendered Auto Const
Armor Property DD_PlugAnal_Inflatable_Inventory Auto Const
Armor Property DD_PlugAnal_Inflatable_Rendered Auto Const
Armor Property DD_PlugAnal_Steel_Inventory Auto Const
Armor Property DD_PlugAnal_Steel_Rendered Auto Const
Armor Property DD_PlugVaginal_Atomic_Blue_Inventory Auto Const
Armor Property DD_PlugVaginal_Atomic_Blue_Rendered Auto Const
Armor Property DD_PlugVaginal_Atomic_Purple_Inventory Auto Const
Armor Property DD_PlugVaginal_Atomic_Purple_Rendered Auto Const
Armor Property DD_PlugVaginal_Atomic_White_Inventory Auto Const
Armor Property DD_PlugVaginal_Atomic_White_Rendered Auto Const
Armor Property DD_PlugVaginal_ChainBell_Inventory Auto Const
Armor Property DD_PlugVaginal_ChainBell_Rendered Auto Const
Armor Property DD_PlugVaginal_Inflatable_Inventory Auto Const
Armor Property DD_PlugVaginal_Inflatable_Rendered Auto Const
Armor Property DD_PlugVaginal_Steel_Inventory Auto Const
Armor Property DD_PlugVaginal_Steel_Rendered Auto Const
Armor Property DD_SlaveHeels_Inventory Auto Const
Armor Property DD_SlaveHeels_Rendered Auto Const
Armor Property DD_SlaveHeels_Rust_Inventory Auto Const
Armor Property DD_SlaveHeels_Rust_Rendered Auto Const
Armor Property DD_SlaveHeelsRestrictive_Inventory Auto Const
Armor Property DD_SlaveHeelsRestrictive_Rendered Auto Const
Armor Property DD_SlaveHeelsRestrictive_Rust_Inventory Auto Const
Armor Property DD_SlaveHeelsRestrictive_Rust_Rendered Auto Const
Armor Property DD_SlaveRingHeels_Inventory Auto Const
Armor Property DD_SlaveRingHeels_Rendered Auto Const
Armor Property DD_SlaveRingHeels_Rust_Inventory Auto Const
Armor Property DD_SlaveRingHeels_Rust_Rendered Auto Const
Armor Property DD_Straitjacket_Boots_Latex_Inventory Auto Const
Armor Property DD_Straitjacket_Boots_Latex_Rendered Auto Const
Armor Property DD_Straitjacket_Boots_Open_Latex_Inventory Auto Const
Armor Property DD_Straitjacket_Boots_Open_Latex_Rendered Auto Const
Armor Property DD_Straitjacket_Dress_Latex_Inventory Auto Const
Armor Property DD_Straitjacket_Dress_Latex_Rendered Auto Const
Armor Property DD_Straitjacket_Dress_Open_Latex_Inventory Auto Const
Armor Property DD_Straitjacket_Dress_Open_Latex_Rendered Auto Const
Armor Property DD_Straitjacket_Latex_Inventory Auto Const
Armor Property DD_Straitjacket_Latex_Rendered Auto Const
Armor Property DD_Straitjacket_Leather_Inventory Auto Const
Armor Property DD_Straitjacket_Leather_Rendered Auto Const
Armor Property DD_Straitjacket_Open_Latex_Inventory Auto Const
Armor Property DD_Straitjacket_Open_Latex_Rendered Auto Const
Armor Property DD_Wristcuffs_Armbinder_Latex_Inventory Auto Const
Armor Property DD_Wristcuffs_Armbinder_Latex_Rendered Auto Const
Armor Property DD_Wristcuffs_Armbinder_Leather_Inventory Auto Const
Armor Property DD_Wristcuffs_Armbinder_Leather_Rendered Auto Const
Armor Property DD_Wristcuffs_Heavy_Inventory Auto Const
Armor Property DD_Wristcuffs_Heavy_Rendered Auto Const
Armor Property DD_Wristcuffs_Heavy_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Heavy_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Institute_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Institute_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Institute_Inventory Auto Const
Armor Property DD_Wristcuffs_Institute_Rendered Auto Const
Armor Property DD_Wristcuffs_Iron_Inventory Auto Const
Armor Property DD_Wristcuffs_Iron_Rendered Auto Const
Armor Property DD_Wristcuffs_Iron_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Iron_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Leather_Inventory Auto Const
Armor Property DD_Wristcuffs_Leather_Rendered Auto Const
Armor Property DD_Wristcuffs_Leather_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Leather_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Rope_Inventory Auto Const
Armor Property DD_Wristcuffs_Rope_Rendered Auto Const
Armor Property DD_Wristcuffs_Slave_Inventory Auto Const
Armor Property DD_Wristcuffs_Slave_Rendered Auto Const
Armor Property DD_Wristcuffs_Slave_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Slave_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Steel_Gold_Inventory Auto Const
Armor Property DD_Wristcuffs_Steel_Gold_Rendered Auto Const
Armor Property DD_Wristcuffs_Steel_Gold_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Steel_Gold_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Steel_Inventory Auto Const
Armor Property DD_Wristcuffs_Steel_Rendered Auto Const
Armor Property DD_Wristcuffs_Steel_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Steel_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Steel_Silver_Inventory Auto Const
Armor Property DD_Wristcuffs_Steel_Silver_Rendered Auto Const
Armor Property DD_Wristcuffs_Steel_Silver_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Steel_Silver_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Vault_Inventory Auto Const
Armor Property DD_Wristcuffs_Vault_Rendered Auto Const
Armor Property DD_Wristcuffs_Vault_Disconnected_Inventory Auto Const
Armor Property DD_Wristcuffs_Vault_Disconnected_Rendered Auto Const
Armor Property DD_Wristcuffs_Yoke_Heavy_Inventory Auto Const
Armor Property DD_Wristcuffs_Yoke_Heavy_Rendered Auto Const
Armor Property DD_Wristcuffs_Yoke_Inventory Auto Const
Armor Property DD_Wristcuffs_Yoke_Rendered Auto Const
EndGroup

Group BoundAnimationKeywords
Keyword Property _TD_GenericBoundHands Auto Const
Keyword Property _TD_GenericBoundHandsArmsBehindBack Auto Const
Keyword Property _TD_GenericBoundHandsMidMovement Auto Const
Keyword Property _TD_InstituteCuffsFboundHandsBack Auto Const
Keyword Property _TD_InstituteCuffsFboundHandsFront Auto Const
Keyword Property _TD_InstituteCuffsFboundHandsFrontLow Auto Const
Keyword Property _TD_GenericBoundFeetSolid Auto Const
Keyword Property _TD_BoundFeetHobble Auto Const
EndGroup

Group SpellEffects
Spell Property DD_EffectSpell_Armbinder Auto Const							; Items with this spell effect tie the character's arms behind her back. Meant for armbinders.
Spell Property DD_EffectSpell_Blindfold Auto Const							; Items with this spell effect apply a blind effect to the character. This spell sets the strength ONLY!!! The effect keyword needs to be on the item.
Spell Property DD_EffectSpell_CuffedLegs_Strict Auto Const					; Items with this spell effect tie the character's legs tightly together, forcing her to hop.
Spell Property DD_EffectSpell_CuffedWrists_Institute_Random Auto Const		; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_CuffedWrists_Institute_Back Auto Const		; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_CuffedWrists_Institute_FrontHigh Auto Const	; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_CuffedWrists_Institute_FrontLow Auto Const	; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_CuffedWrists_Random Auto Const				; Items with this spell effect tie the character's legs tightly together. Meant for regular cuffs.
Spell Property DD_EffectSpell_CuffedWrists_Back Auto Const					; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_CuffedWrists_BackMid Auto Const				; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_CuffedWrists_BackStrict Auto Const			; Items with this spell effect tie the character's wrists tightly together. Meant for larger cuffs.
Spell Property DD_EffectSpell_EventPlugs Auto Const							; Items with this spell effect can vibrate and stimulate a character.
Spell Property DD_EffectSpell_EventArmbinderStruggle Auto Const				; Items with this spell effect make the character struggle against her armbinder.
Spell Property DD_EffectSpell_Disarm Auto Const								; Items with this spell effect will unequip the character's weapons when the item equips.
Spell Property DD_EffectSpell_Strip Auto Const								; Items with this spell effect will unequip the character's armor when the item equips.
Spell Property DD_EffectSpell_NoItemEquip Auto Const						; Items with this spell effect do not allow equipping weapons or armor while they are worn.
Spell Property DD_EffectSpell_NoItemPickup Auto Const						; Items with this spell effect do not allow picking up items other than keys when worn.
Spell Property DD_EffectSpell_GagMoan Auto Const							; Items with this spell effect make a character moan occassionally.
Spell Property DD_EffectSpell_Yoke Auto Const								; Items with this spell effect tie the character's arms next to her head. Meant for yokes.
Spell Property DD_EffectSpell_Yoke_Heavy Auto Const							; Items with this spell effect tie the character's arms next to her head. Meant for heavy (Koffi's) yokes.
Spell Property DD_EffectSpell_EventCuffedStruggle Auto Const				; Items with this spell effect make the character stuggle. Meant for handcuffs.
Spell Property DD_EffectSpell_Shock Auto Const
Spell Property DD_EffectSpell_EventCollarStruggle Auto Const
Spell Property DD_EffectSpell_EventTrip Auto Const
EndGroup

Group LeveledLists															; These lists are useful if you want to assign restraints drops to loot tables etc. Should be self-explainatory.
LeveledItem Property DD_LL_AnalPlugs Auto Const
LeveledItem Property DD_LL_Blindfolds Auto Const
LeveledItem Property DD_LL_ChastityBelts Auto Const
LeveledItem Property DD_LL_ChastityBras Auto Const
LeveledItem Property DD_LL_Collars Auto Const
LeveledItem Property DD_LL_Gags Auto Const
LeveledItem Property DD_LL_Gloves Auto Const
LeveledItem Property DD_LL_Gloves_All Auto Const
LeveledItem Property DD_LL_Gloves_BondageMittens Auto Const
LeveledItem Property DD_LL_Harnesses Auto Const
LeveledItem Property DD_LL_Hoods Auto Const
LeveledItem Property DD_LL_LegCuffs Auto Const
LeveledItem Property DD_LL_NipplePiercings Auto Const
LeveledItem Property DD_LL_Suits_All Auto Const
LeveledItem Property DD_LL_Suits_Catsuits Auto Const
LeveledItem Property DD_LL_Suits_ChainHarness Auto Const
LeveledItem Property DD_LL_Suits_Dresses Auto Const
LeveledItem Property DD_LL_Suits_HobbleSkirts Auto Const
LeveledItem Property DD_LL_Suits_Straitjackets Auto Const
LeveledItem Property DD_LL_Suits_RestraintDresses Auto Const
LeveledItem Property DD_LL_VaginalPlugs Auto Const
LeveledItem Property DD_LL_WristCuffs Auto Const
LeveledItem Property DD_LL_All Auto Const
EndGroup

Group FormLists															; These lists are used for random item equips. Pass as argument to EquipRandomDevice().
FormList Property DD_FL_AnalPlugs Auto Const
FormList Property DD_FL_Blindfolds Auto Const
FormList Property DD_FL_ChastityBelts Auto Const
FormList Property DD_FL_ChastityBras Auto Const
FormList Property DD_FL_Collars Auto Const
FormList Property DD_FL_Gags Auto Const
FormList Property DD_FL_Gloves Auto Const
FormList Property DD_FL_Gloves_All Auto Const
FormList Property DD_FL_Gloves_BondageMittens Auto Const
FormList Property DD_FL_Harnesses Auto Const
FormList Property DD_FL_Hoods Auto Const
FormList Property DD_FL_LegCuffs Auto Const
FormList Property DD_FL_NipplePiercings Auto Const
FormList Property DD_FL_Suits_All Auto Const
FormList Property DD_FL_Suits_Catsuits Auto Const
FormList Property DD_FL_Suits_ChainHarness Auto Const
FormList Property DD_FL_Suits_Dresses Auto Const
FormList Property DD_FL_Suits_HobbleSkirts Auto Const
FormList Property DD_FL_Suits_Straitjackets Auto Const
FormList Property DD_FL_Suits_RestraintDresses Auto Const
FormList Property DD_FL_VaginalPlugs Auto Const
FormList Property DD_FL_WristCuffs Auto Const
FormList Property DD_FL_All Auto Const
EndGroup

Group UserSettings	 ;legacy purpose only												
GlobalVariable Property DD_Config_lockPickSystem Auto 		; Setting for the escape system. 0 = RNG (default), 1 = Lockpick Minigame
GlobalVariable Property DD_Config_DifficultyModifier Auto	; Setting for the difficulty modifier.
EndGroup

; internal use only!
DD:DD_ConfigQuest Property config Auto Const		; For mod settings/MCM
ObjectReference Property doorLock Auto Const
ObjectReference Property doorMarker Auto Const
Perk Property LockSmith01 Auto Const
Perk Property LockSmith02 Auto Const
Perk Property LockSmith03 Auto Const
Perk Property LockSmith04 Auto Const
FormList Property WorkshopMenuRaider Auto Const
FormList Property DD_WorkshopMenu Auto Const
ObjectReference Property VirtualInventory Auto Const
Bool Property removaltoken = false Auto Hidden 		; token for the restraints script to determine if the item removal is legit.
Keyword Property PreferredBondagePose Auto Hidden	; parameter the restraints script can read to see if a specific pose should be used.
Int Property CurrentVersion = 0 Auto Hidden			; stores the current version.
Float Property BlindfoldStrength = 0.75 Auto Hidden	; Effect strength as passed by the effect. Not an ideal implementation, but I can't think of a better one that can still handle multiple items with blindfold effects.
Bool BlindFoldApplied = False
InputEnableLayer Property DDLayer Auto Hidden		; Sets player controls.
Bool Property bProcessing Auto Hidden 				; Used for internal functions concerning color mods.
Bool dbUpdateRunning = False						; Test purpose only
Int dbUpdateCount = 0								; Test purpose only
int VibrateSoundinstanceID = 0						; for plug sounds
GlobalVariable FPA_Value_Arousal					; Sex Attributes Arousal
int PlayerSpeedDamage = 95							; for hobble 1st person exploit
bool HobbleSpeedDmgApplied = false					; for hobble 1st person exploit 
Keyword Property AAF_ActorBusy  Auto Hidden			; For AAF compatibility 

; we need this message here because it got added after many DD items were created, so this property is not guaranteed to be filled on the device.
Message Property DD_OnPutOnDeviceMSG Auto			; Message to be displayed when the player locks on an item, so she can manipulate the locks if she choses. You can customize it if you want, but make sure not to change the order and functionality of the buttons.

Group Idles	
Idle Property _TD_DDAroused01 Auto Const			; Aroused idle - fondle breasts and crossed legs
Idle Property _TD_BoundHandsBackStruggle Auto Const	; Handcuff struggle idle
Idle Property _TD_ArmbinderStruggle Auto Const		; Armbinder struggle idle
Idle Property _TD_CollarPoseFlavor Auto Const		; Collared idle
Idle Property DD_ArmbinderHorny01a  Auto Const		; knees come together - writhing animation
Idle Property DD_ArmbinderHorny01b  Auto Const		; knees come together - orgasm scene
Idle Property DD_ArmbinderHorny02a  Auto Const		; legs crossed - writhing animation
Idle Property DD_ArmbinderHorny02b  Auto Const		; legs crossed - orgasm scene
Idle Property DD_ArmbinderStanding01  Auto Const
Idle Property DD_ArmbinderStanding02  Auto Const
Idle Property DD_ArmbinderStanding03  Auto Const
Idle Property DD_ChastityHorny01  Auto Const		; unrestrained horny belt animation
Idle Property DD_Collar01a  Auto Const				; both hands tugging on the collar
Idle Property DD_CollarHorny01a  Auto Const			; mix of Standinghorny01a and tugging on the collar
Idle Property DD_StandingHorny01a  Auto Const		; knees come together - writhing animation - grab crotch
Idle Property DD_StandingHorny01b  Auto Const		; knees come together - orgasm scene
Idle Property DD_StandingHorny02a  Auto Const		; legs crossed - writhing animation
Idle Property DD_StandingHorny02b  Auto Const		; legs crossed - orgasm scene
Idle Property RaiderSheath  Auto Const				; for plug interaction with character
EndGroup

Armor Property dummyArmor Auto Const				; Used for fixing some NPC inventory glitches

CustomEvent DD_Equipped
CustomEvent DD_Unequipped

Keyword Property DD_kw_UseDatabase Auto Const
WornDevices[] database1
WornDevices[] database2
WornDevices[] database3
WornDevices[] database4
WornDevices[] database5
WornDevices[] database6
WornDevices[] database7
WornDevices[] database8
WornDevices[] database9
WornDevices[] database10
WornDevices[] database11
WornDevices[] database12
WornDevices[] database13
WornDevices[] database14
WornDevices[] database15
WornDevices[] database16
WornDevices[] database17
WornDevices[] database18
WornDevices[] database19
WornDevices[] database20
struct WornDevices
	Actor slave = None
	Armor belt = None
	Armor blindfold = None
	Armor bra = None
	Armor collar = None
	Armor gag = None
	Armor gloves = None
	Armor harness = None
	Armor hood = None
	Armor legcuffs = None
	Armor nipplepiercings = None
	Armor pluganal = None
	Armor plugvaginal = None
	Armor suit = None
	Armor wristcuffs = None
endStruct

; ----------------------------------------------------------------------------------------
; Begin public API functions
; ----------------------------------------------------------------------------------------

Int Function GetVersion()
	Return 7 		; Internal build number increment to determine the newest version - does NOT correspond with the offical version name.
EndFunction

String Function GetVersionString()
	Return "2.1" 	; string to be displayed in messages
EndFunction

; Equips a device on a character. Both "parts" of the device need to passed as arguments. If the CheckDependencies argument is true, this function will check for item dependencies.
; If the argument Pose is not None, the item will try to use the bondage pose passed, but only of that pose is valid for this item (read: in its list of valid poses)
; Returns true if an item was equipped, false otherwise.
; While still possible, it is NOT needed to pass the RenderedDevice anymore. I advise against sending it and letting the script do everything for you.
Bool Function EquipDevice(Actor akActor, Armor InventoryDevice, Armor RenderedDevice = none, Bool CheckDependencies = True, Keyword Pose = None, String Color = "none")
	ObjectReference tmpORef = Player.placeAtMe(InventoryDevice, abInitiallyDisabled = true)
	DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
	If CheckDependencies
		if tmpZRef != none
			If (tmpZRef.IsEquipDeviceConflict(akActor) || tmpZRef.IsEquipRequiredDeviceConflict(akActor))
				tmpZRef.UnregisterForAllEvents()
				tmpZRef = none
				tmpORef.Delete()
				tmpORef = None
				return False
			EndIf
		Else
			Log("EquipDevice received non DD argument.")
			tmpZRef.UnregisterForAllEvents()
			tmpZRef = none
			tmpORef.Delete()
			tmpORef = None
			Return False
		Endif
	EndIf
	If Pose
		PreferredBondagePose = Pose
	Else
		PreferredBondagePose = None
	EndIf
	; This allows the user to define which color the restraint should be. If none or invalid is passed, it defaults (usually black).
	if Color != "none" && tmpZRef.bModdable
		Int _count = akActor.GetItemCount(InventoryDevice)
		if _count > 0
			akActor.RemoveItem(InventoryDevice, _count - 1, true, VirtualInventory)
		Else
			akActor.AddItem(InventoryDevice, 1, true)
		EndIf
		if color == "black" && tmpZRef.omColorBlack
			akActor.AttachModToInventoryItem(InventoryDevice, tmpZRef.omColorBlack)
		elseif color == "red" && tmpZRef.omColorRed
			akActor.AttachModToInventoryItem(InventoryDevice, tmpZRef.omColorRed)
		elseif color == "white" && tmpZRef.omColorWhite
			akActor.AttachModToInventoryItem(InventoryDevice, tmpZRef.omColorWhite)
		elseif color == "rust" && tmpZRef.omColorRust
			akActor.AttachModToInventoryItem(InventoryDevice, tmpZRef.omColorRust)
		elseif color == "pink" && tmpZRef.omColorPink
			akActor.AttachModToInventoryItem(InventoryDevice, tmpZRef.omColorPink)
		elseif color == "blue" && tmpZRef.omColorBlue
			akActor.AttachModToInventoryItem(InventoryDevice, tmpZRef.omColorBlue)
		EndIf
		akActor.EquipItem(InventoryDevice, False, True)
	else
		if akActor.GetItemCount(InventoryDevice) <= 0
			akActor.AddItem(InventoryDevice, 1, true)
		EndIf
		akActor.Equipitem(InventoryDevice, False, True)
	endif
	; This allows mod users to skip on defining a RenderedDevice on calling the function. However, it does not break backwards-compatibility.
	; if RenderedDevice
		; akActor.Equipitem(RenderedDevice, True, True)
	; else
		; RenderedDevice = tmpZRef.RenderedDevice
		; akActor.EquipItem(RenderedDevice, True, True)
	; endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
	; need to call this trigger with a slight delay, since the script might not be initialized earlier
	Utility.Wait(0.5)
	Var[] kargs = new Var[2]
	kargs[0] = InventoryDevice
	kargs[1] = akActor
	SendCustomEvent("DD_Equipped", kargs)
	If akActor == Player
		DD_PlayerEquippedItems.AddForm(InventoryDevice)
	EndIf
	VirtualInventory.RemoveAllItems(akActor, true)
	Return True
EndFunction

; Removes a device from a character. If DestroyDevice is true, the inventory device will be removed. If the CheckDependencies argument is true, this function will check for item dependencies.
; Returns true if an item was removed, false otherwise.
Bool Function RemoveDevice(Actor akActor, Armor InventoryDevice, Armor RenderedDevice = none, Bool DestroyDevice = False, Bool CheckDependencies = True)
	ObjectReference tmpORef = Player.placeAtMe(InventoryDevice, abInitiallyDisabled = true)
	DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
	log("RemoveDevice")
	If CheckDependencies
		if tmpZRef != none
			If tmpZRef.IsUnequipDeviceConflict(akActor)
				tmpZRef.UnregisterForAllEvents()
				tmpZRef = none
				tmpORef.Delete()
				tmpORef = None
				return False
			EndIf
		Else
			Log("RemoveDevice received non DD argument.")
			tmpZRef.UnregisterForAllEvents()
			tmpZRef = none
			tmpORef.Delete()
			tmpORef = None
			Return False
		Endif
	EndIf
	removaltoken = true	
	if !RenderedDevice
		RenderedDevice = tmpZRef.RenderedDevice
	EndIf	
	if akActor.IsEquipped(RenderedDevice)
		akActor.UnEquipItem(RenderedDevice, abSilent = true)
		akActor.RemoveItem(RenderedDevice, 1, True)
		if InventoryDevice.HasKeyword(DD_kw_ItemType_Suit)
			akActor.UnEquipItemSlot(33)
		endif
	endif	
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
	akActor.Unequipitem(InventoryDevice, False, True)
	Var[] kargs = new Var[2]
	kargs[0] = InventoryDevice
	kargs[1] = akActor
	SendCustomEvent("DD_Unequipped", kargs)
	If akActor == Player
		DD_PlayerEquippedItems.RemoveAddedForm(InventoryDevice)
	EndIf
	If DestroyDevice
		akActor.RemoveItem(InventoryDevice, 1, True)
	EndIf
	Return True
EndFunction

; Returns 0 if the actor is not wearing a device of this type, 1 if she is wearing that specific device, or 2 if she's wearing another device of the same type.
Int Function IsWearingDevice(Actor akActor, Armor RenderedDevice, Keyword DeviousDevice)
	if akActor == None || RenderedDevice == None || DeviousDevice == None
		Log("IsWearingDevice received none argument.")
		return -1
	EndIf
	if akActor.WornHasKeyword(DeviousDevice)
		if akActor.GetItemCount(RenderedDevice) == 0
			return 1
		Endif
		return 2
	EndIf
	return 0
EndFunction

; Retrieves correct key for a given inventory device
Key Function GetDeviceKey(armor InventoryDevice)
    Key retval = none
    ObjectReference tmpORef = Player.placeAtMe(InventoryDevice, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none
        retval = tmpZRef.DeviceKey
    Else
        Log("GetDeviceKey received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; Retrieves device keyword for a given inventory device
Keyword Function GetDeviceKeyword(armor device)
    Keyword retval = none
    ObjectReference tmpORef = Player.placeAtMe(device, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none
        retval = tmpZRef.DeviceKeyword		
    Else
        Log("GetDeviceKeyword received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; Retrieves rendered device for a given inventory device
; Useful to check for keywords only present on the rendered device
Armor Function GetRenderedDevice(armor device)
    Armor retval = none
    ObjectReference tmpORef = Player.placeAtMe(device, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none
        retval = tmpZRef.RenderedDevice
    Else
        Log("GetRenderedDevice received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; Queries if a device is a quest device
Bool Function IsQuestDevice(armor device)
    Bool retval = False
    ObjectReference tmpORef = Player.placeAtMe(device, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none && (tmpZref.HasKeyword(DD_kw_IsQuestItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsQuestItem))
        retval = True
    Else
        Log("IsQuestDevice received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; Queries if a device is a non-generic device
Bool Function IsNonGenericDevice(armor device)
    Bool retval = False
    ObjectReference tmpORef = Player.placeAtMe(device, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none && (tmpZref.HasKeyword(DD_kw_IsNotGenericItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsNotGenericItem))
        retval = True
    Else
        Log("IsNonGenericDevice received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; Queries if a device is a generic device
Bool Function IsGenericDevice(armor device)
    Bool retval = True
    ObjectReference tmpORef = Player.placeAtMe(device, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none && (tmpZref.HasKeyword(DD_kw_IsNotGenericItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsNotGenericItem) || tmpZref.HasKeyword(DD_kw_IsQuestItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsQuestItem))
        retval = False
    Else
        Log("IsGenericDevice received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; Checks if a given device has a specific spell effect in its list.
Bool Function HasSpellEffect(Armor InventoryDevice, Spell Effect)
    Bool retval = none
    ObjectReference tmpORef = Player.placeAtMe(InventoryDevice, abInitiallyDisabled = true)
    DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
    if tmpZRef != none
		Int i = tmpZRef.AppliedSpellEffects.Length
        While I > 0 && !retval
			i -= 1
			If tmpZRef.AppliedSpellEffects[i] == Effect
				retval = true
			EndIf
		EndWhile
    Else
        Log("HasSpellEffect received non DD argument.")
    Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
    return retval
EndFunction

; This function will operate on any device, even those who's rendered device / keyword you don't know.
; Returns true if a device was successfully manipulated.
Bool Function RemoveGenericDevice(Actor akActor, Armor InventoryDevice)
	ObjectReference tmpORef = akActor.placeAtMe(InventoryDevice, abInitiallyDisabled = true)
	DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
	bool success = false
	if tmpZRef != none
		if tmpZref.HasKeyword(DD_kw_IsQuestItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsQuestItem)
			Log("RemoveGenericDevice called on a quest device.")
		Elseif akActor.IsEquipped(tmpZRef.RenderedDevice)
			RemoveDevice(akActor, InventoryDevice, tmpZRef.RenderedDevice)
			success = true
		EndIf
	Else
		Log("RemoveGenericDevice received non DD argument.")
	Endif
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
	return success
EndFunction

; This function will remove devices for which only the keyword is known. Works on player only and is painfully slow!
; If there ever will be a way to cycle through an object's inventory via script (F4SE...), I will add functionality for NPCs, too.
; The akActor parameter was added for future compatibiity. It obviously doesn't do anything yet.
; Returns true if a device was successfully manipulated.
Bool Function RemoveGenericDeviceByKeyword(Actor akActor, Keyword DeviousDevice)
	If !Player.WornHasKeyword(DeviousDevice)
		Return False
	EndIf
	bool success = False
	if akActor.HasKeyword(DD_kw_UseDatabase)
		Armor _device = databaseRetrieveDevice(akActor, DeviousDevice)
		
		ObjectReference tmpORef = Player.placeAtMe(_device, abInitiallyDisabled = true)
		DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
		
		if tmpZref.HasKeyword(DD_kw_IsQuestItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsQuestItem)
			Log("RemoveGenericDevice called on a quest device.")
		Elseif Player.IsEquipped(tmpZRef.RenderedDevice)
			RemoveDevice(Player, _device, tmpZRef.RenderedDevice)
			success = true
		EndIf
		
		tmpZRef.UnregisterForAllEvents()
		tmpZRef = none
		tmpORef.Delete()
		tmpORef = None
	Else
		if akActor != Player
			return False
		EndIf
	
		Bool HasItem = False
		Armor InventoryDevice = None
		ObjectReference tmpORef = None
		Int i = DD_PlayerEquippedItems.GetSize()
		While i > 0 && !HasItem
			i-=1
			InventoryDevice = DD_PlayerEquippedItems.GetAt(i) As Armor
			tmpORef = Player.placeAtMe(InventoryDevice, abInitiallyDisabled = true)
			DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
			if tmpZRef != none
				If tmpZRef.DeviceKeyword == DeviousDevice
					; found a match
					HasItem = True
					if tmpZref.HasKeyword(DD_kw_IsQuestItem) || tmpZRef.RenderedDevice.HasKeyword(DD_kw_IsQuestItem)
						Log("RemoveGenericDevice called on a quest device.")
					Elseif Player.IsEquipped(tmpZRef.RenderedDevice)
						RemoveDevice(Player, InventoryDevice, tmpZRef.RenderedDevice)
						success = true
					EndIf
				EndIf
			Else
				Log("RemoveGenericDevice received non DD argument.")
			EndIf
			tmpZRef.UnregisterForAllEvents()
			tmpZRef = none
			tmpORef.Delete()
			tmpORef = None
		EndWhile
	EndIf
	return success
EndFunction

; same as above, but will remove ALL worn DD items, except quest items.
Function RemoveAllGenericDevices(Actor akActor)
	Int i = DD_ItemTypeKeywords.GetSize()
	While i > 0
		i -= 1
		RemoveGenericDeviceByKeyword(akActor, DD_ItemTypeKeywords.GetAt(i) As Keyword)
	EndWhile
EndFunction

; Have some fun and jam the player's locks for some extra torment!
; Yes, jammed locks work for players only. Poor NPCs can't repair them!
Function JamLock(Keyword DeviousDevice)
	If !DD_ItemTypeKeywords.HasForm(DeviousDevice)
		return
	EndIf
	DD_PlayerJammedLocks.AddForm(DeviousDevice)
EndFunction

; This function will unjam a jammed lock and do nothing if the given device has no jammed lock.
Function UnJamLock(Keyword DeviousDevice)
	If !DD_ItemTypeKeywords.HasForm(DeviousDevice)
		return
	EndIf
	DD_PlayerJammedLocks.RemoveAddedForm(DeviousDevice)
EndFunction

; Queries whether a device locked on a player has a jammed lock.
Bool Function IsLockJammed(Keyword DeviousDevice)
	If !DD_ItemTypeKeywords.HasForm(DeviousDevice)
		return False
	EndIf
	return DD_PlayerJammedLocks.HasForm(DeviousDevice)
EndFunction

; This function checks whether a given InventoryDevice has male models available, in case you want to put Preston in cuffs for making you save yet another settlement.
Bool Function HasMaleModel(Armor InventoryDevice)
	If DD_MaleModelItems.HasForm(InventoryDevice)
		return True
	EndIf
	return False
EndFunction

; Equips a random device from a given formlist. If the Formlist contains other Formlists, the function will branch down and try again.
; There will be a maximum of MaxAttempts attempts to equip an actual armor found in the formlist.
; If MaxAttempts is greater than 1, it's good practice to check for occupied slots before actually calling this function, as it would use all attempts and waste a lot of CPU time.
; This function can take either default Formlists from this API or your own, but the formlists should not contain anything except DD inventory items and other Formlists. Do NOT add rendered items to them.
; This function accepts parameter akColor. Use it to equip a random device of a given color and type.
; E.g. you know that during your quest the player only gets equipped with red restraints, you can use this to equip a random collar that is also red (if available).
; If akColor is not defined, it defaults and chooses a random color for backwards compatibility.
Bool Function EquipRandomDevice(Actor akActor, FormList ItemList, Int MaxAttempts = 5, String akColor = "none", Bool bColorOnly = False)
	Armor Device = None
	FormList Branch = ItemList
	Form Frm
	Int i = MaxAttempts
	String _color = akColor
	While i > 0
		i -= 1
		Frm = Branch.GetAt(Utility.RandomInt(0, Branch.GetSize() - 1))
		If (Frm As Armor) && (Frm.HasKeyword(DD_kw_InventoryItem))
			Device = Frm As Armor			
			; This item is an actual DD device, so let's equip it, if we can and reset the tree if we can't!
			if _color == "none"
				_color = RandomDeviceColor(Device)
				If !akActor.WornHasKeyword(GetDeviceKeyword(Device)) && EquipDevice(akActor, Device, GetRenderedDevice(Device), CheckDependencies = True, Color = _color)
					return True
				Else
					Branch = ItemList
				EndIf
			Else
				if CanDeviceHaveColor(Device, _color) || !bColorOnly
					If !akActor.WornHasKeyword(GetDeviceKeyword(Device)) && EquipDevice(akActor, Device, GetRenderedDevice(Device), CheckDependencies = True, Color = akColor)
						return True
					Else
						Branch = ItemList
					EndIf
				Else
					Branch = ItemList
				EndIf
			EndIf
		ElseIf (Frm As FormList)
			; branch down if it's a form list
			Branch = Frm As FormList
			i += 1
		Else
			Log("EquipRandomDevice: Invalid arguments passed.")
			; somebody passed garbage as arguments, but let's pretend it didn't happen...
		EndIf
	EndWhile
	Return False
EndFunction

; ----------------------------------------------------------------------------------------
; Begin support functions
; ----------------------------------------------------------------------------------------

; Disarms a character. Useful when equipping no-fight restraints.
Function Disarm(Actor akActor)
	Weapon S
	S = DD_SmokinGun
	akActor.AddItem(S, 1, true)
	akActor.Equipitem(S, False, True)
	akActor.Unequipitem(S, False, True)
	akActor.RemoveItem(S, 1, true)
EndFunction

; Strips an actor naked, and makes them leave Power Armor and sheathe their weapons if so desired.
Function Strip(Actor akActor, Bool StripPowerArmor = True, Bool DisarmCharacter = True)
	Armor S
	If DisarmCharacter
		Disarm(akActor)
	EndIf
	If StripPowerArmor
		ExitPowerArmor(akActor)
		Utility.Wait(0.5)
		S = DD_StripperPA
	Else
		S = DD_Stripper
	EndIf
	akActor.AddItem(S, 1, true)
	akActor.Equipitem(S, False, True)
	akActor.Unequipitem(S, False, True)
	akActor.RemoveItem(S, 1, true)
EndFunction

Function ExitPowerArmor(Actor akActor)
	If akActor.IsInPowerArmor()
		akActor.SwitchToPowerArmor(None)
		; reset bound animations, the power armor probably broke them
		If akActor.HasKeyword(_TD_AnimArchetypeBound)
			akActor.ChangeAnimArchetype()
			akActor.ChangeAnimArchetype(_TD_AnimArchetypeBound)
		EndIf
	EndIf
EndFunction

; checks if it's safe to play a scene or event
Bool Function PlayerIsBusy(Bool IncludePowerArmor = true)
	If (Player.IsInPowerArmor() && IncludePowerArmor) || Player.IsInCombat() || Player.IsInScene() || Player.IsDead() || Player.IsUnconscious() || Player.IsFlying() || Player.IsOnMount() || (Player.GetSitState() > 0) || Player.IsArrested() || Player.IsTalking() || Player.HasKeyword(AAF_ActorBusy)
		return true
	EndIf
	Return False
EndFunction

Function Notify(String out, Bool MessageBox = False)
	Log(out)
	if MessageBox
		Debug.MessageBox(out)
	else
		Debug.Notification(out)
	EndIf
EndFunction

Function dbgNotify(String out, Bool _dbg = True)
	If _dbg
		if config.ShowDatabaseMessages == 1
			Debug.Notification("[DD]: " + out)
		endif
		Debug.Trace("[DD]: " + out)
	EndIf
EndFunction

Function Error(String out, Bool MessageBox = False, Bool log = False)
	if MessageBox
		Debug.MessageBox("Devious Devices Error: " + out)
	else
		Debug.Notification("Devious Devices Error: " + out)
	EndIf
	If log
		Debug.Trace("[DD]: " + out)
	EndIf
EndFunction

Function Log(String out)
	Debug.Trace("[DD]: " + out)
EndFunction

Function CloseMenus(bool CloseMessagebox = false)
	if CloseMessagebox == true && UI.IsMenuOpen("MessageBoxMenu")
		UI.CloseMenu("MessageBoxMenu")
	endif
	
	If (UI.IsMenuOpen("PipboyMenu"))
        UI.CloseMenu("PipboyMenu")
	ElseIf (UI.IsMenuOpen("ContainerMenu"))
        UI.CloseMenu("ContainerMenu")
	endif
EndFunction

Function ClearGagTargetAlias()
	GagDialogueTarget.Clear()
endfunction

; Sounds

Function GaggedMoan(Actor akActor, Int Loops = 1)
	; This function does NOT check if the actor is actually gagged. It plays the gag sound no matter what! Use it when you mean it!
	Int i = Loops
	While i > 0
		i -= 1
		DD_SoundGagged.PlayAndWait(akActor)
	EndWhile
EndFunction

Function GaggedSex(Actor akActor, Int Loops = 1, Int Excitement = 0)
	; This function does NOT check if the actor is actually gagged. It plays the gag sound no matter what! Use it when you mean it!
	Int i = Loops
	Bool sex = akActor.GetActorBase().GetSex()	
	Int Strength = Excitement	
	If Strength == 0 	; use a random value
		Strength = Utility.RandomInt(1,3)
	ElseIf Strength < 1 || Strength > 3		; sanity check
		Strength = 2
	EndIf	
	If sex == 1 ; it's a female
		If Strength == 1
			While i > 0
				i -= 1	
				DD_SoundDescSexGaggedMildF.PlayAndWait(akActor)
			EndWhile
		ElseIf Strength == 2
			While i > 0
				i -= 1	
				DD_SoundDescSexGaggedMediumF.PlayAndWait(akActor)
			EndWhile
		Else
			While i > 0
				i -= 1	
				DD_SoundDescSexGaggedHotF.PlayAndWait(akActor)
			EndWhile
		EndIf
	Else ; male
		If Strength == 1
			While i > 0
				i -= 1	
				DD_SoundDescSexGaggedMildM.PlayAndWait(akActor)
			EndWhile
		ElseIf Strength == 2
			While i > 0
				i -= 1	
				DD_SoundDescSexGaggedMediumM.PlayAndWait(akActor)
			EndWhile
		Else
			While i > 0
				i -= 1	
				DD_SoundDescSexGaggedHotM.PlayAndWait(akActor)
			EndWhile
		EndIf
	EndIf		
EndFunction

Function GaggedSexNoWait(Actor akActor, Int Excitement = 0) ;without loops
    ; This function does NOT check if the actor is actually gagged. It plays the gag sound no matter what! Use it when you mean it!
    Bool sex = akActor.GetActorBase().GetSex()    
    Int Strength = Excitement    
    If Strength == 0     ; use a random value
        Strength = Utility.RandomInt(1,3)
    ElseIf Strength < 1 || Strength > 3        ; sanity check
        Strength = 2
    EndIf    
    If sex == 1 ; it's a female
        If Strength == 1
            DD_SoundDescSexGaggedMildF.Play(akActor)
        ElseIf Strength == 2
            DD_SoundDescSexGaggedMediumF.Play(akActor)
        Else
            DD_SoundDescSexGaggedHotF.Play(akActor)
        EndIf
    Else ; male
        If Strength == 1
            DD_SoundDescSexGaggedMildM.Play(akActor)
        ElseIf Strength == 2
            DD_SoundDescSexGaggedMediumM.Play(akActor)
        Else
            DD_SoundDescSexGaggedHotM.Play(akActor)
        EndIf
    EndIf        
EndFunction

Function ArousedMoan(Actor akActor, Int Loops = 1)
	; Plays gag sounds when the player is gagged and regular moans otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedSex(akActor, Loops)
	Else
		Int i = Loops
		While i > 0
			i -= 1
			DD_SoundMoan.PlayAndWait(akActor)
		EndWhile
	EndIf
EndFunction

Function ArousedMoanNoWait(Actor akActor, Int Excitement = 0)
	; Plays gag sounds when the player is gagged and regular moans otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedSexNoWait(akActor, Excitement)
	Else
		DD_SoundMoan.Play(akActor)
	EndIf
EndFunction

Function Orgasm(Actor akActor, Int Loops = 1)
	; Plays gag sounds when the player is gagged and regular orgasm otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedSex(akActor, Loops, Excitement = 3)
	Else
		Int i = Loops
		While i > 0
			i -= 1
			DD_SoundOrgasm.PlayAndWait(akActor)
		EndWhile
	EndIf
EndFunction

Function ShortMoan(Actor akActor, Int Loops = 1)
	; Plays gag sounds when the player is gagged and regular orgasm otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedMoan(akActor, Loops)
	Else
		Int i = Loops
		While i > 0
			i -= 1
			DD_SoundMoanShort.PlayAndWait(akActor)
		EndWhile
	EndIf
EndFunction

Function ShortPant(Actor akActor, Int Loops = 1)
	; Plays gag sounds when the player is gagged and regular orgasm otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedMoan(akActor, Loops)
	Else
		Int i = Loops
		While i > 0
			i -= 1
			DD_SoundPantShort.PlayAndWait(akActor)
		EndWhile
	EndIf
EndFunction

Function Edge(Actor akActor, Int Loops = 1)
	; Plays gag sounds when the player is gagged and regular orgasm otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedMoan(akActor, Loops)
	Else
		Int i = Loops
		While i > 0
			i -= 1
			DD_SoundEdged.PlayAndWait(akActor)
		EndWhile
	EndIf
EndFunction

Function EdgeWinddown(Actor akActor, Int Loops = 1)
	; Plays gag sounds when the player is gagged and regular orgasm otherwise.
	Int sID
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedMoan(akActor, Loops)
	Else
		Int i = Loops
		While i > 0
			i -= 1
			DD_SoundEdgedWinddown.PlayAndWait(akActor)
		EndWhile
	EndIf
EndFunction

Function SayPainDialogue(Actor akActor)
	if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
		GaggedMoan(akActor)
	else
		akActor.Say(DialogueGenericHitGroup, None, false, None)
	endif
EndFunction

; On inital start-up of the DD quest, this adds the workshop category dynamically, thus avoiding conflict with other mods that add categories
Event OnQuestInit()
	log("OnQuestInit started...")
	RegisterForRemoteEvent(player, "OnPlayerLoadGame")
	log("Registered event 'OnPlayerLoadGame'...")
	WorkshopMenuRaider.AddForm(DD_WorkshopMenu)
	log("Added Workshop menu...")
	log("OnQuestInit finished...")
EndEvent

; This just sets up the database array so that we can use it later.
event OnInit()
	log("OnInit started...")
	;PopulateDB()
	;DB init rework credits by Tron91
	database1 = new WornDevices[0]
	database2 = new WornDevices[0]
	database3 = new WornDevices[0]
	database4 = new WornDevices[0]
	database5 = new WornDevices[0]
	database6 = new WornDevices[0]
	database7 = new WornDevices[0]
	database8 = new WornDevices[0]
	database9 = new WornDevices[0]
	database10 = new WornDevices[0]
	database11 = new WornDevices[0]
	database12 = new WornDevices[0]
	database13 = new WornDevices[0]
	database14 = new WornDevices[0]
	database15 = new WornDevices[0]
	database16 = new WornDevices[0]
	database17 = new WornDevices[0]
	database18 = new WornDevices[0]
	database19 = new WornDevices[0]
	database20 = new WornDevices[0]
	log("Created database....")
	databaseCreateStruct(Player)
	StartTimerGameTime(6, 1)
	log("OnInit finished...")
endEvent

; This timer runs every 6 game hours and performs clean-up operations.
event OnTimerGameTime(Int aiTimerID)
	if aiTimerID == 1
		databaseClean()
		;StartTimer(6, 1) //wrong timer type called, credits Elsidia
		StartTimerGameTime(6, 1)
	EndIf
endEvent

Event OnTimer(int aiTimerID)		
	If aiTimerID == 99 ;DD anim stuck
		SceneInterupt()
		CancelTimer(99)
	EndIf
EndEvent

; This is mostly redundant, however it's good to have this event registered if you want to remove the category in a later version.
Event Actor.OnPlayerLoadGame(Actor akActor)
	if !WorkshopMenuRaider.HasForm(DD_WorkshopMenu)
		WorkshopMenuRaider.AddForm(DD_WorkshopMenu)
	endif
	updateMod()
	DD_EffectQueueTail = 0
	DD_EffectQueueHead = 0
EndEvent

; This is a placeholder function. We can run this after updating the mod as to not having to force clean saves for minor changes.
function updateMod()
	log("Updating to version " + CurrentVersion)
	return	
EndFunction

; this will return a random possible color for a given device (as string).
string function RandomDeviceColor(Armor akArmor)
	ObjectReference tmpORef = player.PlaceAtMe(akArmor, abInitiallyDisabled = true)
	DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript	
	if !tmpZRef
		tmpZRef.UnregisterForAllEvents()
		tmpZRef = none
		tmpORef.Delete()
		tmpORef = None
		return "none"
	EndIf	
	String[] _strings = new String[0]
	if tmpZRef.bModdable
		if tmpZRef.omColorBlack
			_strings.Add("black")
		EndIf
		if tmpZRef.omColorRed
			_strings.Add("red")
		EndIf
		if tmpZRef.omColorWhite
			_strings.Add("white")
		EndIf
		if tmpZRef.omColorRust
			_strings.Add("rust")
		EndIf
		if tmpZRef.omColorPink
			_strings.Add("pink")
		endif
		if tmpZRef.omColorBlue
			_strings.Add("blue")
		endif	
		if _strings.Length == 0
			tmpZRef.UnregisterForAllEvents()
			tmpZRef = none
			tmpORef.Delete()
			tmpORef = None
			return "none"
		Else
			Int _i = Utility.RandomInt(0, _strings.Length - 1)
			String _color = _strings[0]								;modified the line to get just black items.
			if _color
				tmpZRef.UnregisterForAllEvents()
				tmpZRef = none
				tmpORef.Delete()
				tmpORef = None
				return _color
			Else
				tmpZRef.UnregisterForAllEvents()
				tmpZRef = none
				tmpORef.Delete()
				tmpORef = None
				return "none"
			EndIf
		EndIf
	EndIf
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None
	return "none"
EndFunction

; Returns true if the passed device can be colored in the passed color, return false otherwise.
; Also returns false if the passed device was invalid.
; If Color is passed an empty string "none", it will return true if the device is moddable at all, and false if it isn't.
Bool Function CanDeviceHaveColor(Armor akArmor, String Color = "none")
	ObjectReference tmpORef = player.PlaceAtMe(akArmor, abInitiallyDisabled = true)
	DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
	Bool _result = false
	if !tmpZRef
		tmpZRef.UnregisterForAllEvents()
		tmpZRef = none
		tmpORef.Delete()
		tmpORef = None
		return false
	EndIf
	if tmpZRef.bModdable
		if Color == "black"
			if tmpZRef.omColorBlack
				_result = true
			Else
				_result = false
			EndIf
		elseif Color == "red"
			if tmpZRef.omColorRed
				_result = true
			Else
				_result = false
			EndIf
		elseif Color == "white"
			if tmpZRef.omColorWhite
				_result = true
			Else
				_result = false
			EndIf
		elseif Color == "rust"
			if tmpZRef.omColorRust
				_result = true
			Else
				_result = false
			EndIf
		elseif Color == "pink"
			if tmpZRef.omColorPink
				_result = true
			Else
				_result = false
			EndIf
		elseif Color == "blue"
			if tmpZRef.omColorBlue
				_result = true
			Else
				_result = false
			EndIf
		elseif Color == "none"
			_result = true
		EndIf
	Else
		_result = false
	EndIf
	tmpZRef.UnregisterForAllEvents()
	tmpZRef = none
	tmpORef.Delete()
	tmpORef = None	
	return _result
EndFunction

; The following functions offer a fairly resource-friendly way of tracking devices on NPCs and the player.
; Be advised that by default, the database function is disabled for NPCs.
; To enable database usage for a NPC, add the keyword DD_kw_UseDatabase to the NPC or an alias containing the NPC.
; While this is very resource-friendly for what it does, it's still fairly demanding - so don't use it lightly.
; However, if you're constantly checking for devices on actors, use this!
WornDevices function databaseRetrieve(Actor akActor)
	if !akActor.HasKeyword(DD_kw_UseDatabase) && !akActor == player
		Return None
	endif
	WornDevices _struct
	Int _i = 0
	_i = database1.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database1[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database2.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database2[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database3.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database3[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database4.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database4[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database5.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database5[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database6.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database6[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database7.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database7[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database8.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database8[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database9.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database9[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database10.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database11.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database12.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database13.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database14.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database15.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database16.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database17.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database18.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	_i = database19.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
		return _struct
		EndIf
	EndIf	
	_i = database20.FindStruct("slave", akActor)	
	if _i >= 0
		_struct = database10[_i]
		if _struct.slave == akActor
			return _struct
		EndIf
	EndIf	
	return None
EndFunction

function databaseClean(Bool bReset = false)
	log("Database cleanup started.")
	Int _i	
	Int dbNum
	if !bReset
		WornDevices _struct
		_i = database1.Length
		log("Database 1 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database1[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 1 entry " + _i + " was deleted.")
				database1.Remove(_i)
			EndIf
		EndWhile		
		_i = database2.Length
		log("Database 2 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database2[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 2 entry " + _i + " was deleted.")
				database2.Remove(_i)
			EndIf
		EndWhile
		_i = database3.Length
		log("Database 3 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database3[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 3 entry " + _i + " was deleted.")
				database3.Remove(_i)
			EndIf
		EndWhile		
		_i = database4.Length
		log("Database 4 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database4[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 4 entry " + _i + " was deleted.")
				database4.Remove(_i)
			EndIf
		EndWhile
		_i = database5.Length
		log("Database 5 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database5[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 5 entry " + _i + " was deleted.")
				database5.Remove(_i)
			EndIf
		EndWhile		
		_i = database6.Length
		log("Database 6 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database6[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 6 entry " + _i + " was deleted.")
				database6.Remove(_i)
			EndIf
		EndWhile
		_i = database7.Length
		log("Database 7 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database7[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 7 entry " + _i + " was deleted.")
				database7.Remove(_i)
			EndIf
		EndWhile		
		_i = database8.Length
		log("Database 8 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database8[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 8 entry " + _i + " was deleted.")
				database8.Remove(_i)
			EndIf
		EndWhile
		_i = database9.Length
		log("Database 9 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database9[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 9 entry " + _i + " was deleted.")
				database9.Remove(_i)
			EndIf
		EndWhile		
		_i = database10.Length
		log("Database 10 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database10[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 10 entry " + _i + " was deleted.")
				database10.Remove(_i)
			EndIf
		EndWhile
		_i = database11.Length
		log("Database 11 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database11[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 11 entry " + _i + " was deleted.")
				database11.Remove(_i)
			EndIf
		EndWhile
		_i = database12.Length
		log("Database 12 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database12[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 12 entry " + _i + " was deleted.")
				database12.Remove(_i)
			EndIf
		EndWhile
		_i = database13.Length
		log("Database 13 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database13[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 13 entry " + _i + " was deleted.")
				database13.Remove(_i)
			EndIf
		EndWhile
		_i = database14.Length
		log("Database 14 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database14[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 14 entry " + _i + " was deleted.")
				database14.Remove(_i)
			EndIf
		EndWhile
		_i = database15.Length
		log("Database 15 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database15[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 15 entry " + _i + " was deleted.")
				database15.Remove(_i)
			EndIf
		EndWhile
		_i = database16.Length
		log("Database 16 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database16[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 16 entry " + _i + " was deleted.")
				database16.Remove(_i)
			EndIf
		EndWhile
		_i = database17.Length
		log("Database 17 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database17[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 17 entry " + _i + " was deleted.")
				database17.Remove(_i)
			EndIf
		EndWhile
		_i = database18.Length
		log("Database 18 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database18[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 18 entry " + _i + " was deleted.")
				database18.Remove(_i)
			EndIf
		EndWhile
		_i = database19.Length
		log("Database 19 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database19[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 19 entry " + _i + " was deleted.")
				database19.Remove(_i)
			EndIf
		EndWhile
		_i = database20.Length
		log("Database 20 contains " + _i + " entries.")
		while _i
			_i -= 1
			_struct = database20[_i]
			if (_struct.slave.IsDead() || !_struct.slave.HasKeyword(DD_kw_UseDatabase)) && _struct.slave != Player
				log("Database 20 entry " + _i + " was deleted.")
				database20.Remove(_i)
			EndIf
		EndWhile
	Else
		log("All databases have been reset.")
		dbgNotify("All databases have been reset.")
		database1.Clear()
		database2.Clear()
		database3.Clear()
		database4.Clear()
		database5.Clear()
		database6.Clear()
		database7.Clear()
		database8.Clear()
		database9.Clear()
		database10.Clear()
		database11.Clear()
		database12.Clear()
		database13.Clear()
		database14.Clear()
		database15.Clear()
		database16.Clear()
		database17.Clear()
		database18.Clear()
		database19.Clear()
		database20.Clear()
		return
	Endif
	dbNum = 0
	while dbNum < 20
		dbNum += 1
		dbgNotify("Sorting database " + dbNum)
		databaseSort(dbNum)
	EndWhile
;	databaseSort(2)
;	databaseSort(3)
;	databaseSort(4)
;	databaseSort(5)
;	databaseSort(6)
;	databaseSort(7)
;	databaseSort(8)
;	databaseSort(9)
;	databaseSort(10)
;	databaseSort(11)
;	databaseSort(12)
;	databaseSort(13)
;	databaseSort(14)
;	databaseSort(15)
;	databaseSort(16)
;	databaseSort(17)
;	databaseSort(18)
;	databaseSort(19)
;	databaseSort(20)
;	Int _length1 = database1.Length
;	Int _length2 = database2.Length
;	Int _length3 = database3.Length
;	Int _length4 = database4.Length
;	Int _length5 = database5.Length
;	Int _length6 = database6.Length
;	Int _length7 = database7.Length
;	Int _length8 = database8.Length
;	Int _length9 = database9.Length
;	Int _length10 = database10.Length
;	if _length2 > 0
;		if (_length1 + _length2) < 128
;			_i = _length2
;			while _i
;				_i -= 1
;				WornDevices _struct = database2[_i]
;				database1.Add(_struct)
;				database2.Remove(_i)
;			EndWhile
;		EndIf
;	endif	
;	if database10.Length > 120
;		error("The DD database is almost full. Entries may be dropped.", false, true)
;	EndIf
	log("Database cleanup completed.")
	dbgNotify("Database cleanup completed.")
EndFunction

function databaseSort(Int db = 1, Int i = 0)
	log("Sorting database " + db + "...")
	Int _open = i
	bool _found = False
	WornDevices[] database	
	if db == 1
		database = database1
	elseif db == 2
		database = database2
	elseif db == 3
		database = database3
	elseif db == 4
		database = database4
	elseif db == 5
		database = database5
	elseif db == 6
		database = database6
	elseif db == 7
		database = database7
	elseif db == 8
		database = database8
	elseif db == 9
		database = database9
	elseif db == 10
		database = database10
	elseif db == 11
		database = database11
	elseif db == 12
		database = database12
	elseif db == 13
		database = database13
	elseif db == 14
		database = database14
	elseif db == 15
		database = database15
	elseif db == 16
		database = database16
	elseif db == 17
		database = database17
	elseif db == 19
		database = database18
	elseif db == 19
		database = database19
	elseif db == 20
		database = database20
	EndIf	
	while i < database.Length
		if database[i] == None
			if !_found
				_found = True
				_open = i
				log("Found open spot at index " + i)
				i += 1
			Else
				i += 1
			EndIf
		Else
			if _found
				if !(database[i] == none)
					database[_open] = database[i]
					database[i] = None
					log("Moved entry " + i + " to index " + _open + "...")
					databaseSort(db, _open + 1)
					log("Sorting database " + db + " is completed.")
					return
				Else
					i += 1
				EndIf
			Else
				i += 1
			EndIf
		EndIf
	EndWhile
EndFunction
	
Armor function databaseRetrieveDevice(Actor akActor, Keyword akKeyword)
	WornDevices _struct = databaseRetrieve(akActor)	
	if _struct
		if akKeyword == DD_kw_ItemType_ChastityBelt
			return _struct.belt
		elseif akKeyword == DD_kw_ItemType_Blindfold
			return _struct.blindfold
		elseif akKeyword == DD_kw_ItemType_ChastityBra
			return _struct.bra
		elseif akKeyword == DD_kw_ItemType_Collar
			return _struct.collar
		elseif akKeyword == DD_kw_ItemType_Gag
			return _struct.gag
		elseif akKeyword == DD_kw_ItemType_Gloves
			return _struct.gloves
		elseif akKeyword == DD_kw_ItemType_Harness
			return _struct.harness
		elseif akKeyword == DD_kw_ItemType_Hood
			return _struct.hood
		elseif akKeyword == DD_kw_ItemType_LegCuffs
			return _struct.legcuffs
		elseif akKeyword == DD_kw_ItemType_NipplePiercings
			return _struct.nipplepiercings
		elseif akKeyword == DD_kw_ItemType_PlugAnal
			return _struct.pluganal
		elseif akKeyword == DD_kw_ItemType_PlugVaginal
			return _struct.plugvaginal
		elseif akKeyword == DD_kw_ItemType_Suit
			return _struct.suit
		elseif akKeyword == DD_kw_ItemType_WristCuffs
			return _struct.wristcuffs
		Else
			return None
		Endif
	EndIf
	return None
EndFunction
 
; This function is called when a device is equipped/unequipped on a tracked actor or the player.
; It updates the actor struct appropriately.
function databaseUpdate(Actor akActor, Armor akArmor = None, Armor akRenderedDevice = None, Bool bRemove = false)
	;If !akActor.HasKeyword(DD_kw_UseDatabase) && !akActor == player //wrong comparison. Credits Elsidia
	If !akActor.HasKeyword(DD_kw_UseDatabase) && akActor != player
		Return
	EndIf
	While dbUpdateRunning
		Utility.Wait(0.5)									;Lets the previous call to this function complete. Prevents duplicate records.
	EndWhile
	dbUpdateCount += 1										;Global variable keeping track of calls to this function.
	dbUpdateRunning = True									;Other instances of this function are paused.
	WornDevices _struct = databaseRetrieve(akActor)
	if _struct
		if akArmor
			if !akRenderedDevice
				ObjectReference tmpORef = player.PlaceAtMe(akArmor, abInitiallyDisabled = true)
				DD:DD_RestraintScript tmpZRef = tmpORef as DD:DD_RestraintScript
				akRenderedDevice = tmpZRef.RenderedDevice
				tmpZRef.UnregisterForAllEvents()
				tmpZRef = none
				tmpORef.Delete()
				tmpORef = None	
			EndIf
			if akRenderedDevice.HasKeyword(DD_kw_ItemType_ChastityBelt)
				_struct.belt = akArmor
				if bRemove
					_struct.belt = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Blindfold)
				_struct.blindfold = akArmor
				if bRemove
					_struct.blindfold = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_ChastityBra)
				_struct.bra = akArmor
				if bRemove
					_struct.bra = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Collar)
				_struct.collar = akArmor
				if bRemove
					_struct.collar = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Gag)
				_struct.gag = akArmor
				if bRemove
					_struct.gag = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Gloves)
				_struct.gloves = akArmor
				if bRemove
					_struct.gloves = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Harness)
				_struct.harness = akArmor
				if bRemove
					_struct.harness = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Hood)
				_struct.hood = akArmor
				if bRemove
					_struct.hood = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_LegCuffs)
				_struct.legcuffs = akArmor
				if bRemove
					_struct.legcuffs = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_NipplePiercings)
				_struct.nipplepiercings = akArmor
				if bRemove
					_struct.nipplepiercings = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_PlugAnal)
				_struct.pluganal = akArmor
				if bRemove
					_struct.pluganal = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_PlugVaginal)
				_struct.plugvaginal = akArmor
				if bRemove
					_struct.plugvaginal = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_Suit)
				_struct.suit = akArmor
				if bRemove
					_struct.suit = None
				EndIf
			elseif akRenderedDevice.HasKeyword(DD_kw_ItemType_WristCuffs)
				_struct.wristcuffs = akArmor
				if bRemove
					_struct.wristcuffs = None
				EndIf
			endif			
		EndIf
		databaseCount()
	Else
		_struct = databaseCreateStruct(akActor)
		If database1.Length < 128
			database1.Add(_struct)
			dbgNotify("Added to Database 1")
			dbgNotify(database1.Length + " entries now!")
		ElseIf database2.Length < 128
			database2.Add(_struct)
			dbgNotify("Added to Database 2")
			dbgNotify(database2.Length + " entries now!")
		ElseIf database3.Length < 128
			database3.Add(_struct)
			if database3.Length == 0
				dbgNotify("It appears you installed this modified script mid-game!")
				dbgNotify("Applying a small fix to initialize the extra databases.")
				database3 = new WornDevices[0]
				database4 = new WornDevices[0]
				database5 = new WornDevices[0]
				database6 = new WornDevices[0]
				database7 = new WornDevices[0]
				database8 = new WornDevices[0]
				database9 = new WornDevices[0]
				database10 = new WornDevices[0]
				database11 = new WornDevices[0]
				database12 = new WornDevices[0]
				database13 = new WornDevices[0]
				database14 = new WornDevices[0]
				database15 = new WornDevices[0]
				database16 = new WornDevices[0]
				database17 = new WornDevices[0]
				database18 = new WornDevices[0]
				database19 = new WornDevices[0]
				database20 = new WornDevices[0]
				database3.Add(_struct)
				if database3.Length == 0
					dbgNotify("Fix didn't work! Probably papyrus is out of memory.")
				else
					dbgNotify("It appears the fix worked!")
				endif
			endif
			dbgNotify("Added to Database 3")
			dbgNotify(database3.Length + " entries now!")
		ElseIf database4.Length < 128
			database4.Add(_struct)
			dbgNotify("Added to Database 4")
			dbgNotify(database4.Length + " entries now!")
		ElseIf database5.Length < 128
			database5.Add(_struct)
			dbgNotify("Added to Database 5")
			dbgNotify(database5.Length + " entries now!")
		ElseIf database6.Length < 128
			database6.Add(_struct)
			dbgNotify("Added to Database 6")
			dbgNotify(database6.Length + " entries now!")
		ElseIf database7.Length < 128
			database7.Add(_struct)
			dbgNotify("Added to Database 7")
			dbgNotify(database7.Length + " entries now!")
		ElseIf database8.Length < 128
			database8.Add(_struct)
			dbgNotify("Added to Database 8")
			dbgNotify(database8.Length + " entries now!")
		ElseIf database9.Length < 128
			database9.Add(_struct)
			dbgNotify("Added to Database 9")
			dbgNotify(database9.Length + " entries now!")
		ElseIf database10.Length < 128
			database10.Add(_struct)
			dbgNotify("Added to Database 10")
			dbgNotify(database10.Length + " entries now!")
		ElseIf database11.Length < 128
			database11.Add(_struct)
			dbgNotify("Added to Database 11")
			dbgNotify(database11.Length + " entries now!")
		ElseIf database12.Length < 128
			database12.Add(_struct)
			dbgNotify("Added to Database 12")
			dbgNotify(database12.Length + " entries now!")
		ElseIf database13.Length < 128
			database13.Add(_struct)
			dbgNotify("Added to Database 13")
			dbgNotify(database13.Length + " entries now!")
		ElseIf database14.Length < 128
			database14.Add(_struct)
			dbgNotify("Added to Database 14")
			dbgNotify(database14.Length + " entries now!")
		ElseIf database15.Length < 128
			database15.Add(_struct)
			dbgNotify("Added to Database 15")
			dbgNotify(database15.Length + " entries now!")
		ElseIf database16.Length < 128
			database16.Add(_struct)
			dbgNotify("Added to Database 16")
			dbgNotify(database16.Length + " entries now!")
		ElseIf database17.Length < 128
			database17.Add(_struct)
			dbgNotify("Added to Database 17")
			dbgNotify(database17.Length + " entries now!")
		ElseIf database18.Length < 128
			database18.Add(_struct)
			dbgNotify("Added to Database 18")
			dbgNotify(database18.Length + " entries now!")
		ElseIf database19.Length < 128
			database19.Add(_struct)
			dbgNotify("Added to Database 19")
			dbgNotify(database19.Length + " entries now!")
		ElseIf database20.Length < 128
			database20.Add(_struct)
			dbgNotify("Added to Database 20")
			dbgNotify(database20.Length + " entries now!")
		Else		
			error("The database is fulL!")
		EndIf
		databaseCount()
	EndIf
	If dbUpdateCount > 500								;Adjust this value according to needs.
		dbgNotify("About time! Some housekeeping...")		;Can use a while loop here, but it's my choice.
		purgeDeadActors(1)
		purgeDeadActors(2)
		purgeDeadActors(3)
		purgeDeadActors(4)
		purgeDeadActors(5)
		purgeDeadActors(6)
		purgeDeadActors(7)
		purgeDeadActors(8)
		purgeDeadActors(9)
		purgeDeadActors(10)
		purgeDeadActors(11)
		purgeDeadActors(12)
		purgeDeadActors(13)
		purgeDeadActors(14)
		purgeDeadActors(15)
		purgeDeadActors(16)
		purgeDeadActors(17)
		purgeDeadActors(18)
		purgeDeadActors(19)
		purgeDeadActors(20)
		purgeDuplicates(1)
		purgeDuplicates(2)
		purgeDuplicates(3)
		purgeDuplicates(4)
		purgeDuplicates(5)
		purgeDuplicates(6)
		purgeDuplicates(7)
		purgeDuplicates(8)
		purgeDuplicates(9)
		purgeDuplicates(10)
		purgeDuplicates(11)
		purgeDuplicates(12)
		purgeDuplicates(13)
		purgeDuplicates(14)
		purgeDuplicates(15)
		purgeDuplicates(16)
		purgeDuplicates(17)
		purgeDuplicates(18)
		purgeDuplicates(19)
		purgeDuplicates(20)
		dbUpdateCount = 0
	EndIf
	dbUpdateRunning = False
EndFunction

;Displays total records in databases.
function databaseCount()
	int Count = 0
	Count += database1.Length
	Count += database2.Length
	Count += database3.Length
	Count += database4.Length
	Count += database5.Length
	Count += database6.Length
	Count += database7.Length
	Count += database8.Length
	Count += database9.Length
	Count += database10.Length
	Count += database11.Length
	Count += database12.Length
	Count += database13.Length
	Count += database14.Length
	Count += database15.Length
	Count += database16.Length
	Count += database17.Length
	Count += database18.Length
	Count += database19.Length
	Count += database20.Length
	dbgNotify(Count + " entries in database.")
	return
EndFunction

;This function will remove dead actors from the database.
function purgeDeadActors(int db = 1)
	int _length = 0
	int _deadCounter = 0
	WornDevices _struct
	WornDevices[] database = selectDatabase(db)
	_length = database.Length
	If _length == 0
		Return
	EndIf
	While _length
		_length -= 1
		_struct = database[_length]
		If _struct.slave.IsDead() && _struct.slave != Player	;Ain't sure about the Keyword check.
			_deadCounter += 1
			database.Remove(_length)
		EndIf
	EndWhile
	If _deadCounter
		dbgNotify(_deadCounter + " dead actors removed from Database " + db)
	Else
		dbgNotify("No dead actors found in Database " + db)
	EndIf
EndFunction


;This function should ideally never have to remove actors from the database, but some fast computers may need this.
function purgeDuplicates(int db = 1)
	int _length = 0
	int _index1 = 0
	int _index2 = 0
	int _dupCounter = 0
	bool _found = False
	bool _loop = True
	WornDevices _struct1
	WornDevices _struct2
	WornDevices[] database = selectDatabase(db)
	If database.Length < 2
		Return
	EndIf
	_index2 = _index1 + 1
	While _loop
		_length = database.Length
		If _index1 < (_length - 1)
			_struct1 = database[_index1]
			_struct2 = database[_index2]
			If _struct1.slave == _struct2.slave
				_found = True
				_dupCounter += 1
				database.Remove(_index2)
			Else
				_index2 += 1
			EndIf
			If _index2 == database.Length
				_index1 += 1
				_index2 = _index1 + 1
			EndIf
		Else
			_loop = False
		EndIf
	EndWhile
	If _found
		dbgNotify(_dupCounter + " entries removed from Database " + db)
	Else
		dbgNotify("No duplicates found in Database " + db)
	EndIf
EndFunction

;Simple database selection subroutine
WornDevices[] function selectDatabase(int db = 1)
	WornDevices[] database
	If db == 1
		database = database1
	ElseIf db == 2
		database = database2
	ElseIf db == 3
		database = database3
	ElseIf db == 4
		database = database4
	ElseIf db == 5
		database = database5
	ElseIf db == 6
		database = database6
	ElseIf db == 7
		database = database7
	ElseIf db == 8
		database = database8
	ElseIf db == 9
		database = database9
	ElseIf db == 10
		database = database10
	ElseIf db == 11
		database = database11
	ElseIf db == 12
		database = database12
	ElseIf db == 13
		database = database13
	ElseIf db == 14
		database = database14
	ElseIf db == 15
		database = database15
	ElseIf db == 16
		database = database16
	ElseIf db == 17
		database = database17
	ElseIf db == 19
		database = database18
	ElseIf db == 19
		database = database19
	ElseIf db == 20
		database = database20
	EndIf
	Return database
EndFunction

WornDevices function databaseCreateStruct(Actor akActor)
	;if !akActor.HasKeyword(DD_kw_UseDatabase) && !akActor == player  //wrong comparison. Credits Elsidia
	if !akActor.HasKeyword(DD_kw_UseDatabase) && akActor != player
		Return None
	endif
	WornDevices _struct = new WornDevices
	FormList _fl
	Int _i	
	_struct.slave = akActor	
	; Belts
	_fl = DD_FL_ChastityBelts
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.belt
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.belt = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; Blindfold
	_fl = DD_FL_Blindfolds
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.blindfold
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.blindfold = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; Bras
	_fl = DD_FL_ChastityBras
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.bra
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.bra = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; Collar
	_fl = DD_FL_Collars
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.collar
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.collar = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile	
	; Gag
	_fl = DD_FL_Gags
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.gag
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.gag = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; Gloves
	_fl = DD_FL_Gloves
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.gloves
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.gloves = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; Harness
	_fl = DD_FL_Harnesses
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.harness
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.harness = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile	
	; Hood
	_fl = DD_FL_Hoods
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.hood
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.hood = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile	
	; Legcuffs
	_fl = DD_FL_LegCuffs
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.legcuffs
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.legcuffs = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; NipplePiercings
	_fl = DD_FL_NipplePiercings
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.nipplepiercings
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.nipplepiercings = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; PlugAnal
	_fl = DD_FL_AnalPlugs
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.pluganal
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.pluganal = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; PlugVaginal
	_fl = DD_FL_VaginalPlugs
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.plugvaginal
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.plugvaginal = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; Suit
	_fl = DD_FL_Suits_All
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.suit
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.suit = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	; WristCuffs
	_fl = DD_FL_WristCuffs
	_i = _fl.GetSize() - 1
	while _i >= 0 && !_struct.wristcuffs
		Armor _device = _fl.GetAt(_i) as Armor
		if _device
			if akActor.IsEquipped(_device)
				_struct.wristcuffs = _device
			EndIf
		EndIf
		_i -= 1
	EndWhile
	return _struct
EndFunction

Function UpdateLegacyModSettings()
	DD_PipBoyAlwaysHide.setvalueint(config.PipBoySetting)
	DD_Config_lockPickSystem.setvalueint(config.LockPickMinigame)
	DD_Config_DifficultyModifier.setvalueint(config.DifficultyModifier)
EndFunction

; ----------------------------------------
; idle animations
; ----------------------------------------

Function PlayHornyIdle(Actor akActor, bool DisableControls = false)
	if akActor == player
		UI.CloseMenu("pipboymenu")
	endif
	
	if DisableControls == true && akActor == player
		DisablePlayerControlForAnims()
	endif
	
	if akActor.WornHasKeyword(DD_kw_ItemSubType_Armbinder)
		PlayArmbinderStruggle(akActor)
	else
		int RndAnim = Utility.RandomInt(1,6)
		if RndAnim == 1
			PlayDDAnimation(akActor,DD_ChastityHorny01,20)
		elseif RndAnim == 2
			PlayDDAnimation(akActor,DD_StandingHorny01a,20)
		elseif RndAnim == 3
			PlayDDAnimation(akActor,DD_StandingHorny01b,20)
		elseif RndAnim == 4
			PlayDDAnimation(akActor,DD_StandingHorny02a,20)
		elseif RndAnim == 5
			PlayDDAnimation(akActor,DD_StandingHorny02b,20)
		elseif RndAnim == 6
			PlayDDAnimation(akActor,_TD_DDAroused01,20)
		endif
	endif
EndFunction

Function PlayHandcuffBackStruggle(Actor akActor, bool DisableControls = false)
	if DisableControls == true && akActor == player
		DisablePlayerControlForAnims()
	endif
	
	;akActor.PlayIdle(_TD_BoundHandsBackStruggle)
	PlayDDAnimation(akActor,_TD_BoundHandsBackStruggle,20)
EndFunction

Function PlayCollarStruggle(Actor akActor, bool DisableControls = false)
	if DisableControls == true && akActor == player
		DisablePlayerControlForAnims()
	endif
	
	int Arousal = GetArousal(akActor)
	if Arousal < 51
		;akActor.PlayIdle(DD_Collar01a)
		PlayDDAnimation(akActor,DD_Collar01a,20)
	else
		;akActor.PlayIdle(DD_CollarHorny01a)
		PlayDDAnimation(akActor,DD_CollarHorny01a,20)
	endif
EndFunction

Function TripActor(Actor akActor)
	akActor.PushActorAway(akActor, 0.01)
	akActor.ApplyHavokImpulse(0.01, 0, 0, 0.01)
	SayPainDialogue(akActor)
EndFunction

Function PlayArmbinderStruggle(Actor akActor, bool DisableControls = false)
	if DisableControls == true && akActor == player
		DisablePlayerControlForAnims()
	endif
	
	int Arousal = GetArousal(akActor)
	if Arousal < 33
		int rndan = Utility.randomInt(1,4)
		if rndan == 1
			;akActor.PlayIdle(_TD_ArmbinderStruggle)
			PlayDDAnimation(akActor,_TD_ArmbinderStruggle,20)
		elseif rndan == 2
			;akActor.PlayIdle(DD_ArmbinderStanding01)
			PlayDDAnimation(akActor,DD_ArmbinderStanding01,20)
		elseif rndan == 3
			;akActor.PlayIdle(DD_ArmbinderStanding02)
			PlayDDAnimation(akActor,DD_ArmbinderStanding02,20)
		elseif rndan == 4
			;akActor.PlayIdle(DD_ArmbinderStanding03)
			PlayDDAnimation(akActor,DD_ArmbinderStanding03,20)
		endif
	elseif Arousal >=  33 && Arousal <  66
		int rndanb = Utility.randomInt(1,2)
		if rndanb == 1
			;akActor.PlayIdle(DD_ArmbinderHorny01a)
			PlayDDAnimation(akActor,DD_ArmbinderHorny01a,20)
		elseif rndanb == 2
			;akActor.PlayIdle(DD_ArmbinderHorny02a)
			PlayDDAnimation(akActor,DD_ArmbinderHorny02a,20)
		endif
	else
		int rndanc = Utility.randomInt(1,2)
		if rndanc == 1
			;akActor.PlayIdle(DD_ArmbinderHorny01b)
			PlayDDAnimation(akActor,DD_ArmbinderHorny01b,20)
		elseif rndanc == 2
			;akActor.PlayIdle(DD_ArmbinderHorny02b)
			PlayDDAnimation(akActor,DD_ArmbinderHorny02b,20)
		endif
	endif
EndFunction

Weapon function MakeNPCReadyForAnimation(Actor akActor)
	if akActor.IsInCombat()
		akActor.StopCombat()
		akActor.StopCombatAlarm()
	endif

	akActor.SetRestrained()
	Weapon equippedWeapon
	if akActor.IsSneaking()
		akActor.StartSneaking() 
	endif
	akActor.PlayIdleAction(Game.GetFormFromFile(0x00013219, "Fallout4.esm") as Action) ;ActionSprintStop
    Utility.Wait(0.01)
	akActor.PlayIdleAction(Game.GetFormFromFile(0x000959F9, "Fallout4.esm") as Action) ;ActionMoveStop
    Utility.Wait(0.01)
	If akActor.IsWeaponDrawn()
		equippedWeapon = akActor.GetEquippedWeapon()
		if equippedWeapon
			akActor.UnequipItem(equippedWeapon)
		endIf
		akActor.PlayIdleAction(Game.GetFormFromFile(0x00046BAF, "Fallout4.esm") as Action) ;ActionSheath
        Utility.Wait(0.01)
	endIf
	akActor.PlayIdleAction(Game.GetFormFromFile(0x0005704C, "Fallout4.esm") as Action) ;ActionInstantInitializeGraphToBaseState
    Utility.Wait(0.01)
	return equippedWeapon
endfunction

Weapon function MakePlayerReadyForAnimation()
	int camMode = Game.GetCameraState()
	;Debug.Trace("Camera mode = " + camMode)
	if camMode == 1 || camMode == 3 || camMode >= 9
		return None; // nothing to do when camera is free or in dialogues
	endif

	;interrupt VATS mode
	InputEnableLayer layer = InputEnableLayer.Create()
	layer.EnableVATS(false)
	layer.Delete()
	layer = None

	;Game.SetPlayerAIDriven(true)
	Weapon equippedWeapon = MakeNPCReadyForAnimation(player)

	float cameraDistance = 0.0 ;TODO: maybe F4SE API (or its plugin) will support ini values reading?
	; change camera to 3rd person as the first step
	if camMode==0 || camMode == 4 || camMode == 5 || camMode == 7 || camMode == 2 
		Utility.SetINIFloat("fMinCurrentZoom:Camera", 0.5) ; set camera distance
		Game.ForceThirdPerson() ; switched to camera mode = 8
		Utility.wait(0.01) ; wait for a bit to be sure that camera is fully switched
		Utility.SetINIFloat("fMinCurrentZoom:Camera", cameraDistance); restore camera distance
	endIf
	return equippedWeapon
endfunction

Function RestoreActorAfterAnimation(Actor akActor, Weapon equippedWeapon)
	akActor.SetRestrained(false)
	if equippedWeapon
		akActor.EquipItem(equippedWeapon)
	endif
	if akActor != player
		akActor.EvaluatePackage()
	endif
endfunction

;PlayDDAnimation(player, Game.GetFormFromFile(0x000072B2, "TortureDevices.esm") as Idle, 15)

function PlayDDAnimation(Actor akActor, Idle animation, float animationDuration)
	Weapon equippedWeapon
	if akActor == player
        equippedWeapon = MakePlayerReadyForAnimation()
		player.PlayIdle(Game.GetFormFromFile(0x00029380, "Fallout4.esm") as Idle) ; LooseIdleStop
    else
        equippedWeapon = MakeNPCReadyForAnimation(akActor)
    endif

    if akActor.PlayIdle(animation)
		if akActor == player
			float barrier = 1
			;Game.SetPlayerAIDriven(false)
			Utility.Wait(barrier); ensure that animation will not be interrupted for a while
			; allow to rotate camera and interrupt animation
			akActor.SetRestrained(false)
			Utility.Wait(animationDuration-barrier)
		else
			Utility.Wait(animationDuration)
		endif
	else
		if player
			;Game.SetPlayerAIDriven(false)
		endif
    endif
    RestoreActorAfterAnimation(akActor, equippedWeapon)
endfunction

Function RegisterForDDanimToEnd(actor akActor)
	RegisterForAnimationEvent(akActor, "BasePoseEnter")
	RegisterForHitEvent(akActor)
	StartTimer(30,99)
EndFunction

Function UnRegisterForDDanimToEnd(actor akActor)
	UnRegisterForAnimationEvent(akActor, "BasePoseEnter")
	UnRegisterForHitEvent(akActor)
	CancelTimer(99)
EndFunction

Event OnAnimationEvent(ObjectReference akSource, string asEventName)
	if akSource == player && asEventName == "BasePoseEnter"
		UnRegisterForAnimationEvent(player, "BasePoseEnter")
		SceneInterupt(player)
	endif
endevent

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)
	UnRegisterForHitEvent(player)
	SceneInterupt(player)
EndEvent

Function SceneInterupt(actor akActor = none)
	if akActor == none
		akActor = player
	endif
	UnRegisterForDDanimToEnd(akActor)
	RestorePlayerControl()
EndFunction


; ----------------------------------------
; Animation effects
; ----------------------------------------

Function DisablePlayerControlForAnims()
	If !DDLayer
		DDLayer = InputEnableLayer.Create()
	EndIf
	DDLayer.DisablePlayerControls()
	RegisterForDDanimToEnd(player)
EndFunction

Function RestorePlayerControl()
	If !DDLayer
		DDLayer = InputEnableLayer.Create()
	EndIf
	DDLayer.EnablePlayerControls()
	ApplyInputLayerEffects()
EndFunction

Int Function GetEffectLock()
    Int MyTurn = DD_EffectQueueTail
    DD_EffectQueueTail += 1
    While (DD_EffectQueueTail > 0 && DD_EffectQueueHead < MyTurn)
        Utility.Wait(0.1)
    EndWhile
    Return MyTurn
EndFunction

Function ReleaseEffectLock()
    DD_EffectQueueHead += 1
    If (DD_EffectQueueHead >= DD_EffectQueueTail)
        DD_EffectQueueTail = 0
        DD_EffectQueueHead = 0
    EndIf
EndFunction

Function RefreshBoundAnimations(Actor akActor)
	; check if there is at least one bound keyword on the actor, and pick the fitting set of animations.
	Bool isBound = false
	Int i = DD_BoundAnimKeywords.Length
	While i > 0
		i -= 1
		If akActor.HasKeyword(DD_BoundAnimKeywords[i])
			isBound = True
		EndIf
	EndWhile
	If isBound
		akActor.ChangeAnimArchetype()
		akActor.ChangeAnimArchetype(_TD_AnimArchetypeBound)
	else
		if akActor == Player
			akActor.ChangeAnimArchetype()
			akActor.ChangeAnimArchetype(AnimArchetypePlayer)
		else
			akActor.ChangeAnimArchetype(_TD_AnimArchetypeBound)
			akActor.ChangeAnimArchetype()
		endif
	EndIf
EndFunction

; This function is called whenever a new DD item is locked on the player and upon loading games. It will process effects that only apply to the player.
Function ProcessBoundEffects()
	AutoHidePipboy()
	ApplyBlindfold()
	ApplyInputLayerEffects()
	If Player.WornHasKeyword(DD_kw_EffectType_BlockPowerArmor)		
		ExitPowerArmor(Player)
		Player.AddPerk(DD_Perk_DisablePowerArmor)
	Else
		If Player.HasPerk(DD_Perk_DisablePowerArmor)
			Player.RemovePerk(DD_Perk_DisablePowerArmor)
		EndIf
	EndIf
	
	If Player.WornHasKeyword(DD_kw_EffectType_BlockLockpick)		
		Player.AddPerk(DD_Perk_DisableLockPick)
	Else
		If Player.HasPerk(DD_Perk_DisableLockPick)
			Player.RemovePerk(DD_Perk_DisableLockPick)
		EndIf
	EndIf
	
	If Player.WornHasKeyword(DD_kw_EffectType_BlockPickpocket)		
		Player.AddPerk(DD_Perk_DisablePickpocket)
	Else
		If Player.HasPerk(DD_Perk_DisablePickpocket)
			Player.RemovePerk(DD_Perk_DisablePickpocket)
		EndIf
	EndIf
	
	If Player.WornHasKeyword(DD_kw_EffectType_BlockTrapInteraction)		
		Player.AddPerk(DD_Perk_DisableTrapInteraction)
	Else
		If Player.HasPerk(DD_Perk_DisableTrapInteraction)
			Player.RemovePerk(DD_Perk_DisableTrapInteraction)
		EndIf
	EndIf
	
	If Player.WornHasKeyword(DD_kw_EffectType_BlockWorkbench)		
		Player.AddPerk(DD_Perk_DisableWorkbench)
	Else
		If Player.HasPerk(DD_Perk_DisableWorkbench)
			Player.RemovePerk(DD_Perk_DisableWorkbench)
		EndIf
	EndIf
	
	If Player.HasKeyword(_TD_BoundFeetHobble) ;This MT does not support first person anims
		RegisterForCameraState()
		if Player.GetAnimationVariableBool("IsFirstPerson") == true
			HobbleSlowdown(true)
		endif
	Else
		UnRegisterForCameraState()	
		if HobbleSpeedDmgApplied == true
			HobbleSlowdown(false)
		endif
	EndIf
EndFunction

Function ApplyBlindfold()
    If Player.WornHasKeyword(DD_kw_EffectType_Blindfold)
        If !BlindFoldApplied
            DD_BlindfoldImageSpace.Remove()
            DD_BlindfoldImageSpace.Apply(BlindfoldStrength)
            BlindFoldApplied = True
        EndIf    
    Else
        DD_BlindfoldImageSpace.Remove()
        BlindFoldApplied = False
    EndIf
EndFunction

Function ApplyInputLayerEffects()
	If !DDLayer
		DDLayer = InputEnableLayer.Create()
	EndIf
	If Player.WornHasKeyword(DD_kw_EffectType_DisableFastTravel)
		DDLayer.EnableFastTravel(False)
	Else
		DDLayer.EnableFastTravel(True)
	EndIf
	If Player.WornHasKeyword(DD_kw_EffectType_RestrainedLegs)
		DDLayer.EnableRunning(false)
		DDLayer.EnableSprinting(false)
		DDLayer.EnableSneaking(false)
		DDLayer.EnableJumping(false)
	Else
		DDLayer.EnableRunning(True)
		DDLayer.EnableSprinting(True)
		DDLayer.EnableSneaking(True)
		DDLayer.EnableJumping(True)
	EndIf
	If Player.WornHasKeyword(DD_kw_EffectType_HighHeels) && config.HeelsPreventRunning == true
		DDLayer.EnableRunning(false)
		DDLayer.EnableSprinting(false)
	Else
		DDLayer.EnableRunning(True)
		DDLayer.EnableSprinting(True)
	EndIf
	If Player.WornHasKeyword(DD_kw_EffectType_RestrainedArms)
		DDLayer.EnableFighting(False)		
		DDLayer.EnableFavorites(False)		
	Else
		DDLayer.EnableFighting(True)
		DDLayer.EnableFavorites(True)		
	EndIf
EndFunction

Event OnPlayerCameraState(int aiOldState, int aiNewState) ;8=3rd 0=1st
	if aiNewState == 0 && HobbleSpeedDmgApplied == false
		HobbleSlowdown(true)
	else
		HobbleSlowdown(false)
	endif
EndEvent

Function HobbleSlowdown(bool applyEffect)
	if applyEffect == true
		int currSpeed = Player.GetValue(SpeedMult) as int
		int keepspeed = 100 - config.HobbleSlowdown
		PlayerSpeedDamage = currSpeed - keepspeed
		Player.DamageValue(SpeedMult, PlayerSpeedDamage)
		HobbleSpeedDmgApplied = true
	else
		Player.RestoreValue(SpeedMult, PlayerSpeedDamage)
		HobbleSpeedDmgApplied = false
	endif
EndFunction

Function AutoHidePipboy()
	; respect the global flag not to interfere with the PipBoy at all:
	If config.PipBoySetting == -1
		return
	EndIf
	If Player.WornHasKeyword(DD_kw_EffectType_HidesPipBoy) || config.PipBoySetting == 1
		HidePipBoy()
	Else
		ShowPipBoy()
	EndIf
EndFunction

Function SetHidePipBoy(Bool Hide = true)
	If config.PipBoySetting == -1
		Log("SetHidePipBoy called, but feature is disabled by user.")
		return
	EndIf
	If Hide
		config.PipBoySetting = 1
		AutoHidePipboy()
	Else
		config.PipBoySetting = 0
		AutoHidePipboy()
	EndIf
EndFunction

Function HidePipBoy()
	If Player.IsEquipped(Pipboy)
		Player.RemoveItem(Pipboy, 1, True)
		Player.EquipItem(DD_Pipboy, False, True)
	EndIf
EndFunction

Function ShowPipBoy()
	If Player.IsEquipped(DD_Pipboy)
		Player.RemoveItem(DD_Pipboy, 1, True)
		Player.EquipItem(Pipboy, False, True)
	EndIf
EndFunction

Keyword Function GetPreferredBondagePose()
	return PreferredBondagePose
EndFunction

; ----------------------------------------
; Arousal by naaitsab
; ----------------------------------------

Function LoadSexAttributessArousal()
	FPA_Value_Arousal = Game.GetFormFromFile(0x0001E80D, "FPAttributes.esp") as GlobalVariable
EndFunction

int Function GetArousal(actor akActor)
	if config.ShowDDArousalMessages == 3
		int Arousal = FPA_Value_Arousal.getvalueint()
		return Arousal
	else
		int Arousal = akActor.GetValue(DD_AV_Arousal) as int
		return Arousal
	endif
EndFunction

Function SetDDArousal(actor akActor, int val)
	if val > 100
		val = 100
	elseif val < 0
		val = 0
	endif
	akActor.SetValue(DD_AV_Arousal, val)
EndFunction

Function ModDDArousal(actor akActor, int val, bool substract = false)
	if config.ShowDDArousalMessages == 3 && akActor == player
		int Arousal = FPA_Value_Arousal.getvalueint()
		if substract == true
			if (Arousal - val) < 0
				FPA_Value_Arousal.setvalueint(0)
			else
				FPA_Value_Arousal.setvalueint(Arousal - val)
			endif
		else
			if (Arousal + val) > 100
				FPA_Value_Arousal.setvalueint(100)
			else
				FPA_Value_Arousal.setvalueint(Arousal + val)
			endif
		endif
	else
		int Arousal = akActor.GetValue(DD_AV_Arousal) as int
		
		if substract == true
			if (Arousal - val) < 0
				SetDDArousal(akActor, 0)
			else
				akActor.ModValue(DD_AV_Arousal, -val)
			endif
		else
			if (Arousal + val) > 100
				SetDDArousal(akActor, 100)
			else
				akActor.ModValue(DD_AV_Arousal, val)
			endif
		endif
	endif
EndFunction

Int Function ClampArousal(int val)
    If val>100
        return 100
    ElseIf val<0
        return 0
    EndIf
    return val
EndFunction

Function GetArousalFeedback(actor akActor)
	int Arousal = akActor.GetValue(DD_AV_Arousal) as int
	int ArousalLevel
	If Arousal < 20
		ArousalLevel = 0
	elseif Arousal < 40
		ArousalLevel = 1
	elseif Arousal < 60
		ArousalLevel = 2
	elseif Arousal < 80
		ArousalLevel = 3
	else
		ArousalLevel = 4
	Endif
	
	if akActor == player
		if ArousalLevel == 0
			notify("You are not horny.")		
		elseif ArousalLevel == 1
			notify("You feel a bit horny.")		
		elseif ArousalLevel == 2
			notify("You feel horny.")		
		elseif ArousalLevel == 3
			notify("You feel very horny.")		
		elseif ArousalLevel == 4
			notify("You feel extremely horny.")
		Endif	
	else
		if ArousalLevel == 0
			notify(akActor.GetActorBase().GetName() +" is not horny.")		
		elseif ArousalLevel == 1
			notify(akActor.GetActorBase().GetName() +" is a bit horny.")		
		elseif ArousalLevel == 2
			notify(akActor.GetActorBase().GetName() +" is horny.")		
		elseif ArousalLevel == 3
			notify(akActor.GetActorBase().GetName() +" is very horny.")		
		elseif ArousalLevel == 4
			notify(akActor.GetActorBase().GetName() +" is extremely horny.")
		Endif	
	endif
EndFunction

; ----------------------------------------
; Plugs by naaitsab & Elsidia
; ----------------------------------------

sound Function GetVibrateSounds(int strength)
    If strength == 1
		return DD_SoundDescVibrateVeryWeak
    ElseIf strength == 2
        return DD_SoundDescVibrateWeak
    ElseIf strength == 3    
        return DD_SoundDescVibrateStandard
    ElseIf strength == 4
        return DD_SoundDescVibrateStrong
    Else    
        return DD_SoundDescVibrateVeryStrong
    EndIf
EndFunction

string Function GetVibrateTextPlayer(int strength, int variant)
    if variant == 0
		If strength == 1
			return "Your Anal plug start to vibrate very weak"
		ElseIf strength == 2
			return "Your Anal plug start to vibrate weak"
		ElseIf strength == 3    
			return "Your Anal plug start to vibrate"
		ElseIf strength == 4
			return "Your Anal plug start to vibrate strongly"
		Else    
			return "Your Anal plug start to vibrate very strong"
		EndIf
	elseif variant == 1
		If strength == 1
			return "Your Vaginal plug start to vibrate very weak"
		ElseIf strength == 2
			return "Your Vaginal plug start to vibrate weak"
		ElseIf strength == 3    
			return "Your Vaginal plug start to vibrate"
		ElseIf strength == 4
			return "Your Vaginal plug start to vibrate strongly"
		Else    
			return "Your Vaginal plug start to vibrate very strong"
		EndIf
	elseif variant == 2
		If strength == 1
			return "Your Vaginal and Anal plugs start to vibrate very weak"
		ElseIf strength == 2
			return "Your Vaginal and Anal plugs start to vibrate weak"
		ElseIf strength == 3    
			return "Your Vaginal and Anal plugs start to vibrate"
		ElseIf strength == 4
			return "Your Vaginal and Anal plugs start to vibrate strongly"
		Else    
			return "Your Vaginal and Anal plugs start to vibrate very strongly"
		EndIf
	endif
EndFunction

Function SetVibrationStrengthVaginal(Actor akActor, int ammount)
	if ammount < 1
		ammount = 1
	elseif ammount > 5
		ammount = 5
	endif
	akActor.SetValue(DD_AV_VibrateStrengthVaginal, ammount)
EndFunction

Function SetVibrationStrengthAnal(Actor akActor, int ammount)
	if ammount < 1
		ammount = 1
	elseif ammount > 5
		ammount = 5
	endif
	akActor.SetValue(DD_AV_VibrateStrengthAnal, ammount)
EndFunction

Bool Function VibratePlugs(Actor akActor, int PlugVibrateDuration = 0)
	;Vibration duration minumum is 25 seconds due to animation durations
	
    bool VaginalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugVaginal)
    bool AnalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugAnal)
    If !VaginalPlugWorn && !AnalPlugWorn
        return false
    EndIf
	
	if PlugVibrateDuration == 0
		PlugVibrateDuration = (Utility.randomInt(25,65))
	endif
	
	if PlugVibrateDuration < 25
		PlugVibrateDuration = 25 ;idles are 20 seconds roughly with little margin
	endif
	
	float orgasmChance = Utility.randomFloat(80.0,95.0)
	float vibrateChance = Utility.randomFloat(15.0,20.0)

	Bool VaginalVibratorWorn = akActor.WornHasKeyword(DD_kw_ItemSubType_VibratingPlugVaginal)
	Bool AnalVibratorWorn = akActor.WornHasKeyword(DD_kw_ItemSubType_VibratingPlugAnal)
    
	int ArousalValue
	if config.ShowDDArousalMessages == 3 && akActor == player
		ArousalValue = FPA_Value_Arousal.GetValueInt()
	else
		ArousalValue = akActor.GetValue(DD_AV_Arousal) as Int
	endif

    ;ArousalValue = ClampArousal(ArousalValue + (akActor.GetValue(DD_AV_InflateStatusVaginal)as int * 2) + (akActor.GetValue(DD_AV_InflateStatusAnal)as int * 2))
    ;akActor.SetValue(DD_AV_Arousal, ArousalValue)
	;notify("Checking actor:"+ akActor.GetActorBase().GetName())
	    
    If VaginalPlugWorn || AnalPlugWorn
		If (Utility.RandomFloat(0.0, 99.9) < orgasmChance) && (ArousalValue>90); plug send to orgasm!
            If akActor.HasKeyword(DD_kw_Event_IsVibrating)        
                ; no two vibrations at the same time
                return false
            EndIf
			
			akActor.AddKeyword(DD_kw_Event_IsVibrating)
			
			int instanceID
			Int vibstan=akActor.GetValue(DD_AV_VibrateStrengthAnal) as int
			Int vibstvag=akActor.GetValue(DD_AV_VibrateStrengthVaginal) as int
			if vibstan >= vibstvag ;get highest strength
				instanceID = GetVibrateSounds(vibstan).play(akActor)
			else
				instanceID = GetVibrateSounds(vibstvag).play(akActor)
			endif
			
			PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
						
			Utility.wait(PlugVibrateDuration)
			
			
			if akActor.WornHasKeyword(DD_kw_ItemEffect_PlugVibrate_EdgeOnly)
				If akActor == player
					notify("Your plug stops vibrating just before you can orgasm.")
				Else    
					notify(akActor.GetActorBase().GetName() + "'s plugs stop vibrating just before she can orgasm.")					
				EndIf
				Sound.StopInstance(instanceID)				
			else
				If akActor == player
					notify("Your plug sends you into an uncontrollable orgasm.")
				Else    
					notify(akActor.GetActorBase().GetName() + "'s plug send her into an uncontrollable orgasm.")    
				EndIf
				ArousalValue=0
				if config.ShowDDArousalMessages == 3 && akActor == player
					FPA_Value_Arousal.SetValue(0.0)
				else
					akActor.SetValue(DD_AV_Arousal, 0)
				endif
			endif
            
            Utility.Wait(1)
            ;InputEnableLayer myLayerv = InputEnableLayer.Create()
            If akActor == player
                ;myLayerv.DisablePlayerControls()
                UI.CloseMenu("pipboymenu")
            EndiF    
            if akActor.WornHasKeyword(DD_kw_EffectType_GagTalkStrict) || akActor.WornHasKeyword(DD_kw_EffectType_GagTalkNormal)
                GaggedSexNoWait(akActor)
                Utility.Wait(1)
				If akActor == player
					player.PlayIdle(RaiderSheath)
				else
					akActor.PlayIdle(RaiderSheath)
				endif
				Utility.Wait(1)
                PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
                Utility.Wait(1)
                GaggedSexNoWait(akActor)
                Utility.Wait(3)
                GaggedSexNoWait(akActor)
                Utility.Wait(3)
                Orgasm(akActor, 3)
            Else
                ArousedMoanNoWait(akActor)
                Utility.Wait(1)
				If akActor == player
					player.PlayIdle(RaiderSheath)
				else
					akActor.PlayIdle(RaiderSheath)
				endif
				Utility.Wait(1)
                PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
                Utility.Wait(12)
                PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
                Utility.Wait(12)
                Orgasm(akActor, 1)
            EndIf
            If akActor==player
                ;myLayerv.EnablePlayerControls()
                ;game.SetPlayerAIDriven(false)
               ; myLayerv.Delete()            
            EndIf  
			
			if !akActor.WornHasKeyword(DD_kw_ItemEffect_PlugVibrate_EdgeOnly)
				If akActor == player
					notify("Your plug stops vibrating.")
				Else    
					notify(akActor.GetActorBase().GetName() + "'s plug stops vibrating.")    
				EndIf			
				Sound.StopInstance(instanceID)
			Endif
			akActor.RemoveKeyword(DD_kw_Event_IsVibrating)
            return true
        EndIf
    EndIf 
	;End of Orgasm Loop

	int rndPlug
	if VaginalVibratorWorn == true && AnalVibratorWorn == true
		rndPlug = 0
	elseif VaginalVibratorWorn == true && AnalVibratorWorn == false
		rndPlug = 1
	elseif VaginalVibratorWorn == false && AnalVibratorWorn == true
		rndPlug = 2
	endif
	
	int bothVibrate = Utility.Randomint()
	if rndPlug > 0
		bothVibrate = 0 ;force single vib event
	endif
	
	if bothVibrate <= 50
		;If AnalVibratorWorn
		if rndPlug == 2
			Int VibrateStrength = akActor.GetValue(DD_AV_VibrateStrengthAnal) as int
			;If (Utility.RandomFloat(0.0, 99.9) < vibrateChance * VibrateStrength as float); plug vibrate!
				If akActor==player
					notify(GetVibrateTextPlayer(VibrateStrength,0))
					;PlayVibrateSounds(tt,akActor)
					akActor.AddKeyword(DD_kw_Event_IsVibrating)
					int instanceID = GetVibrateSounds(VibrateStrength).play(akActor) 
					Edge(akActor, 1)
					if Utility.randomint() > 50
						PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
					endif
					Utility.wait(PlugVibrateDuration)
					Sound.StopInstance(instanceID)
					notify("Your anal plug stops vibrating.")
					akActor.RemoveKeyword(DD_kw_Event_IsVibrating) 
				Else
					;akActor.PathToReference(player, 1)
					notify(akActor.GetActorBase().GetName()+"'s anal vibrator starts to vibrate")
					akActor.AddKeyword(DD_kw_Event_IsVibrating)
					int instanceID = GetVibrateSounds(VibrateStrength).play(akActor) 
					PlayHornyIdle(akActor)
					Utility.wait(PlugVibrateDuration)
					Sound.StopInstance(instanceID)
					notify(akActor.GetActorBase().GetName() + "'s plug stops vibrating.") 
					akActor.RemoveKeyword(DD_kw_Event_IsVibrating) 
				EndIf    
				ArousalValue=ClampArousal(ArousalValue + VibrateStrength * 4)
				if config.ShowDDArousalMessages == 3 && akActor == player
					FPA_Value_Arousal.SetValue(ArousalValue as float)
				else
					akActor.SetValue(DD_AV_Arousal, ArousalValue)
				endif
				return true
			;EndIf
		Endif
		
		;if VaginalVibratorWorn
		if rndPlug == 1
			int VibrateStrength=akActor.GetValue(DD_AV_VibrateStrengthVaginal) as int
			;If (Utility.RandomFloat(0.0, 99.9) < vibrateChance * VibrateStrength as float); plug vibrate!
				If akActor==player
					notify(GetVibrateTextPlayer(VibrateStrength,1))
					;PlayVibrateSounds(tt,akActor)
					akActor.AddKeyword(DD_kw_Event_IsVibrating)
					int instanceID = GetVibrateSounds(VibrateStrength).play(akActor) 
					Edge(akActor, 1)
					if Utility.randomint() > 50
						PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
					endif
					Utility.wait(PlugVibrateDuration)
					Sound.StopInstance(instanceID)
					notify("Your vaginal plug stops vibrating.")
					akActor.RemoveKeyword(DD_kw_Event_IsVibrating) 
				Else
					akActor.PlayIdle(RaiderSheath)
					notify(akActor.GetActorBase().GetName()+"'s vaginal vibrator starts to vibrate.")
					;VibrateSounds(tt,akActor)
					akActor.AddKeyword(DD_kw_Event_IsVibrating)
					int instanceID = GetVibrateSounds(VibrateStrength).play(akActor)
					PlayHornyIdle(akActor)
					Edge(akActor, 1)
					Utility.wait(PlugVibrateDuration)
					Sound.StopInstance(instanceID)
					notify(akActor.GetActorBase().GetName() + "'s plug stops vibrating.") 
					akActor.RemoveKeyword(DD_kw_Event_IsVibrating) 
				EndIf    
				ArousalValue=ClampArousal(ArousalValue + VibrateStrength * 4)
				if config.ShowDDArousalMessages == 3 && akActor == player
					FPA_Value_Arousal.SetValue(ArousalValue as float)
				else
					akActor.SetValue(DD_AV_Arousal, ArousalValue)
				endif
				return true
			;EndIf
		Endif
	Else
		;if AnalVibratorWorn && VaginalVibratorWorn
		if rndPlug == 0
			Int VibrateStrength
			Int vibstan=akActor.GetValue(DD_AV_VibrateStrengthAnal) as int
			Int vibstvag=akActor.GetValue(DD_AV_VibrateStrengthAnal) as int
			if vibstan >= vibstvag ;get highest strength
				VibrateStrength = vibstan
			else
				VibrateStrength = vibstvag
			endif
			
			;If (Utility.RandomFloat(0.0, 99.9) < vibrateChance * VibrateStrength as float); both plugs vibrate!
				If akActor==player
					notify(GetVibrateTextPlayer(VibrateStrength,2))
					akActor.AddKeyword(DD_kw_Event_IsVibrating)
					int instanceID = GetVibrateSounds(VibrateStrength).play(akActor) 
					Edge(akActor, 1)
					if Utility.randomint() > 50
						PlayHornyIdle(akActor, config.PlugsDisablePlayerControl)
					endif
					Utility.wait(PlugVibrateDuration)
					Sound.StopInstance(instanceID)
					notify("Your plugs stops vibrating.")
					akActor.RemoveKeyword(DD_kw_Event_IsVibrating) 
				Else
					akActor.PlayIdle(RaiderSheath)
					notify(akActor.GetActorBase().GetName()+"'s vaginal and anal starts to vibrate.")
					;VibrateSounds(tt,akActor)
					akActor.AddKeyword(DD_kw_Event_IsVibrating)
					int instanceID = GetVibrateSounds(VibrateStrength).play(akActor)
					Edge(akActor, 1)
					PlayHornyIdle(akActor)
					Utility.wait(PlugVibrateDuration)
					Sound.StopInstance(instanceID)
					notify(akActor.GetActorBase().GetName() + "'s plugs stops vibrating.") 
					akActor.RemoveKeyword(DD_kw_Event_IsVibrating) 
				EndIf    
				ArousalValue=ClampArousal(ArousalValue + VibrateStrength * 8)
				if config.ShowDDArousalMessages == 3 && akActor == player
					FPA_Value_Arousal.SetValue(ArousalValue as float)
				else
					akActor.SetValue(DD_AV_Arousal, ArousalValue)
				endif
				return true
			;endif
		Endif
	Endif
	
    return false
EndFunction

Function StaticPlugs(Actor akActor)
    bool VaginalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugVaginal)
    bool AnalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugAnal)
    If !VaginalPlugWorn && !AnalPlugWorn
        return
    EndIf
	
	int ArousalValue
	if config.ShowDDArousalMessages == 3 && akActor == player
		ArousalValue = FPA_Value_Arousal.GetValueInt()
	else
		ArousalValue = akActor.GetValue(DD_AV_Arousal) as Int
	endif
	
	int rndPlug
	if VaginalPlugWorn == true && AnalPlugWorn == true
		rndPlug = utility.randomint(1,2)
	elseif VaginalPlugWorn == true && AnalPlugWorn == false
		rndPlug = 1
	elseif VaginalPlugWorn == false && AnalPlugWorn == true
		rndPlug = 2
	endif
	
    ;If (Utility.RandomFloat(0.0, 99.9) < 30.0) && VaginalPlugWorn; plug moves!
	if rndPlug == 1
        If akActor==player
            notify("Your vaginal plug moves, sending pleasure trough your body.")
            EdgeWinddown(akActor, 1)
        Else
            notify(akActor.GetActorBase().GetName()+"'s vaginal plug moves sending pleasure trough her body.")
        EndIf    
        ArousalValue=ClampArousal(ArousalValue + 10)
        if config.ShowDDArousalMessages == 3 && akActor == player
			FPA_Value_Arousal.SetValue(ArousalValue as float)
		else
			akActor.SetValue(DD_AV_Arousal, ArousalValue)
		endif
        return
    ;EndIf
    ;If (Utility.RandomFloat(0.0, 99.9) < 30.0) && AnalPlugWorn; plug moves!
	else
        If akActor==player
            notify("Your anal plug moves, sending pleasure trough your body.")
            EdgeWinddown(akActor, 1)
        Else
            notify(akActor.GetActorBase().GetName()+"'s anal plug moves sending pleasure trough her body.")
        EndIf
        ArousalValue=ClampArousal(ArousalValue + 10)
        if config.ShowDDArousalMessages == 3 && akActor == player
			FPA_Value_Arousal.SetValue(ArousalValue as float)
		else
			akActor.SetValue(DD_AV_Arousal, ArousalValue)
		endif
        return
    EndIf
EndFunction

Function InflatePlug(Actor akActor, bool VagPlug)
	if VagPlug == true
		akActor.ModValue(DD_AV_InflateStatusVaginal,1)
	else
		akActor.ModValue(DD_AV_InflateStatusAnal,1)
	endif
EndFunction

Function DeflatePlug(Actor akActor, bool VagPlug)
	if VagPlug == true
		;akActor.SetValue(DD_AV_InflateStatusVaginal,0) doesnt work?
		Int i = akActor.GetValue(DD_AV_InflateStatusVaginal) as int
		Debug.notification(i)
		While i > 0
			i -= 1
			Debug.notification("modav")
			akActor.ModValue(DD_AV_InflateStatusVaginal,-1)
		EndWhile
	else
		akActor.SetValue(DD_AV_InflateStatusAnal,0)
	endif
EndFunction

Function InflatablePlugs(Actor akActor)
	bool VaginalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugVaginal)
    bool AnalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugAnal)
    If !VaginalPlugWorn && !AnalPlugWorn
        return
    EndIf
	
    bool pAnalInflatablestatus = akActor.WornHasKeyword(DD_kw_ItemSubType_InflatablePlugAnal)
    bool pVaginalInflatablestatus = akActor.WornHasKeyword(DD_kw_ItemSubType_InflatablePlugVaginal)
	
	bool didDeflate = false
	
    If pVaginalInflatablestatus
		akActor.AddKeyword(DD_kw_Event_IsVibrating)
		
        If (Utility.RandomFloat(0.0, 99.9) < 20.0) && (akActor.GetValue(DD_AV_InflateStatusVaginal) as int > 0) ; deflate trigger!
            akActor.ModValue(DD_AV_InflateStatusVaginal,-1)
            If akActor==player
                notify("Your vaginal plug valve releases some pressure.")
            Else
                notify(akActor.GetActorBase().GetName()+"'s vaginal plug valve releases some pressure.")
            EndIf
            didDeflate = true
        EndIf
        If (Utility.RandomFloat(0.0, 99.9) < 20.0) && (akActor.GetValue(DD_AV_InflateStatusVaginal) as int < 5) && (!didDeflate); inflate trigger!
            akActor.ModValue(DD_AV_InflateStatusVaginal,1)
			int rnddia = Utility.randomInt()
			if rnddia <= 50
				If akActor == player
					notify("You acidentally bump your vaginal plug pumpbulb and it inflates.")
				Else
					notify(akActor.GetActorBase().GetName()+" acidentally bumps her vaginal plug pumpbulb and it inflates.")
				EndIf
			else
				If akActor==player
					notify("You hear your vaginal plug pump whirr and inflating.")
				Else
					notify(akActor.GetActorBase().GetName()+"'s vaginal plug start whirring and inflates.")
				EndIf
			endif
        EndIf
		
		if config.ShowDDArousalMessages == 3 && akActor == player
			int ar = FPA_Value_Arousal.GetValueInt()
			float newVal = ar + akActor.GetValue(DD_AV_InflateStatusVaginal) as int*10
			if newVal > 100
				newVal = 100
			endif
			FPA_Value_Arousal.SetValue(newVal)
		else
			ModDDArousal(akActor, akActor.GetValue(DD_AV_InflateStatusVaginal) as int*10, false)
		endif
		
		akActor.RemoveKeyword(DD_kw_Event_IsVibrating)
    EndIf

    If pAnalInflatablestatus
	akActor.AddKeyword(DD_kw_Event_IsVibrating)
	
        If (Utility.RandomFloat(0.0, 99.9) < 20.0) && (akActor.GetValue(DD_AV_InflateStatusAnal) as int > 0) ; deflate trigger!
            akActor.ModValue(DD_AV_InflateStatusAnal,-1)
            If akActor==player
                notify("Your anal plug valve releases some pressure.")
            Else
                notify(akActor.GetActorBase().GetName()+"'s anal plug valve releases some pressure.")
            EndIf    
            didDeflate = true
        EndIf
        If (Utility.RandomFloat(0.0, 99.9) < 20.0) && (akActor.GetValue(DD_AV_InflateStatusAnal) as int < 5) && (!didDeflate); inflate trigger!
            akActor.ModValue(DD_AV_InflateStatusAnal,1)
			int rnddia = Utility.randomInt()
			if rnddia <= 50
				If akActor == player
					notify("You acidentally bump your anal plug pumpbulb and it inflates.")
				Else
					notify(akActor.GetActorBase().GetName()+" acidentally bumps her anal plug pumpbulb and it inflates.")
				EndIf
			else
				If akActor==player
					notify("You hear your anal plug pump whirr and inflating.")
				Else
					notify(akActor.GetActorBase().GetName()+"'s anal plug start whirring and inflates.")
				EndIf
			endif  
        EndIf
		
		if config.ShowDDArousalMessages == 3 && akActor == player
			int ar = FPA_Value_Arousal.GetValueInt()
			float newVal = ar + akActor.GetValue(DD_AV_InflateStatusAnal) as int*10
			if newVal > 100
				newVal = 100
			endif
			FPA_Value_Arousal.SetValue(newVal)
		else
			ModDDArousal(akActor, akActor.GetValue(DD_AV_InflateStatusAnal) as int*10, false)
		endif
		
		akActor.RemoveKeyword(DD_kw_Event_IsVibrating)
    EndIf
EndFunction

Function ShockPlugs(Actor akActor, int times = 1, bool silent = false)
    bool VaginalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugVaginal)
    bool AnalPlugWorn = akActor.WornHasKeyword(DD_kw_ItemType_PlugAnal)
    If !VaginalPlugWorn && !AnalPlugWorn
        return
    EndIf
			
	if silent == false
			if times == 1
				If akActor == player
					notify("Your plug gives a painfull shock.")
				Else
					notify(akActor.GetActorBase().GetName()+"'s plug gives her a painfull shock.")
				EndIf
			else
				If akActor == player
					notify("Your plug gives multiple painfull shocks.")
				Else
					notify(akActor.GetActorBase().GetName()+"'s plug gives her multiple painfull shocks.")
				EndIf
			endif
	endif
	
	if akActor.WornHasKeyword(DD_kw_ItemEffect_PlugShock) ;sanity check
		akActor.AddKeyword(DD_kw_Event_IsVibrating)
		int DecreaseArousalCount = 0
		
		While times > 0
			times -= 1
			DD_EffectSpell_Shock.Cast(akActor, akActor)
			Utility.wait(3)
			DecreaseArousalCount + 1
		EndWhile
		

		if config.ShowDDArousalMessages == 3 && akActor == player
			int ar = FPA_Value_Arousal.GetValueInt()
			float newVal = ar - DecreaseArousalCount*10
			if newVal < 0
				newVal = 0
			endif
			FPA_Value_Arousal.SetValue(newVal)
		else
			ModDDArousal(akActor, DecreaseArousalCount*10, true)
		endif
		akActor.RemoveKeyword(DD_kw_Event_IsVibrating)
	endif
EndFunction
