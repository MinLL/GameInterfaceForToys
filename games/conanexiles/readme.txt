Put files into ModsShared folder of devkit.
Add BP_AC_GIFT_PlayerController component to FunCombat_PlayerController in your mod controller.
Get controller for player you need, get component by interface BPI_GIFT_EventsManager from it.
Call ICallToysEvent from that component, and pass event id into it.
Available events listed in DT_GIFT_EventList datatable.