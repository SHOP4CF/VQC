## FIWARE
Basically to comprehend FIWARE functonality that we use in this app it is enough to read [this walkthrought](https://fiware-orion.readthedocs.io/en/latest/user/walkthrough_apiv2/index.html)

`Entities` - in our case these may be `camera sending pcb's images`, `visual quality check component (vqc)`, `interface showing results`. Each of those entities can have some attributes, camera may have: `current_pcb_to_check`, `current_instruction`, `state` etc. vqc component may have 
`status` indicating whether it waits for new image or it is processing it etc. It is possible to perform all comunication between components using FIWARE only it is as simple as sending HTTP requests to the server where FIWARE is running.

`Subscriptions` - when "something" happens, your application will get an asynchronous notification with POST request. We can subscribe for changes of some particular attributes in some particulat entity and send notification to any ip adress we want to.

**When our fiware server is running we can go to the http://localhost:1026/v2/entities and http://localhost:1026/v2/subscriptions to see how thing are chaning**

Communication can proceed as follows:  `Camera` has scanned Barcode and using POST request updated `current_instruction` attribute, then `interface` can subscribe to those changes and receive POST with needed information every time `camera` updates instruction. The same thing with `vqc`. `Camera` do photos and updates it's attributes using simple POST. `Vqc` subscribes for those changes and listens on some URL if it get POST request then some function is fired. Now when `interface` and `vqc` are working, `camera` component can be idle and just subscribe for some changess in one of components, when it gets POST from FIWARE it proceed with its work.
**This is just a sketch of how communication using FIWARe may be performed, a lot of different scenarios may be implemented**

**One drawback of using Subscriptions is that they are only send if attribute has really changed so for example if `vqc` always have status 1 (working) then no notifications will be send but is can be easily solved using somee checksum or something random as an attribute.**

**Drawback of using FIWARE is that we need to have some prior knowledge about entities (their attribute names) we can get them either by their specific id `camera1`, `vqc1` (which has to be known in advance) etc. or just get all entities and filter them.**